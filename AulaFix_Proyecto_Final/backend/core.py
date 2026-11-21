import sqlite3, os, datetime
from contextlib import contextmanager

PRIORITIES={'baja':1,'media':2,'alta':3,'critica':4}
TRANSITIONS={'abierto':{'en_proceso','cancelado'},'en_proceso':{'resuelto','en_espera','cancelado'},'en_espera':{'en_proceso','cancelado'},'resuelto':{'cerrado','en_proceso'},'cerrado':set(),'cancelado':set()}

class BusinessError(Exception):pass

def iso():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')

class Store:
 def __init__(self,path=':memory:'):
  self.db=sqlite3.connect(path,check_same_thread=False,isolation_level=None,timeout=20)
  self.db.row_factory=sqlite3.Row
  self.db.execute('PRAGMA foreign_keys=ON')
  self.db.execute('PRAGMA busy_timeout=20000')
  self.setup()
 @contextmanager
 def tx(self):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   yield
   self.db.commit()
  except:
   self.db.rollback();raise
 def setup(self):
  self.db.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,role TEXT NOT NULL CHECK(role IN ('alumno','tecnico','admin')),password TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS stock(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL,quantity INTEGER NOT NULL CHECK(quantity>=0),minimum INTEGER NOT NULL DEFAULT 2);
  CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY,reporter_id INTEGER NOT NULL REFERENCES users(id),title TEXT NOT NULL,category TEXT NOT NULL,description TEXT NOT NULL,priority TEXT NOT NULL,location TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'abierto',assignee_id INTEGER REFERENCES users(id),created_at TEXT NOT NULL,updated_at TEXT NOT NULL,due_at TEXT NOT NULL,resolution TEXT NOT NULL DEFAULT '');
  CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY,ticket_id INTEGER NOT NULL REFERENCES tickets(id),stock_id INTEGER NOT NULL REFERENCES stock(id),quantity INTEGER NOT NULL CHECK(quantity>0),created_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY,ticket_id INTEGER NOT NULL REFERENCES tickets(id),actor_id INTEGER NOT NULL REFERENCES users(id),action TEXT NOT NULL,detail TEXT NOT NULL,at TEXT NOT NULL);
  CREATE INDEX IF NOT EXISTS idx_ticket_state ON tickets(status,priority);''')
 def rows(self,sql,params=()):return [dict(r) for r in self.db.execute(sql,params).fetchall()]
 def one(self,sql,params=()):
  r=self.db.execute(sql,params).fetchone();return dict(r) if r else None
 def seed(self,password='AulaFix2026!'):
  with self.tx():
   if self.one('SELECT id FROM users LIMIT 1'):return
   for n,e,r,p in [('Martina López','martina@aulafix.test','alumno','alumno123'),('Tomás Herrera','tomas@aulafix.test','alumno','alumno123'),('Lucía Torres','lucia@aulafix.test','tecnico','tecnico123'),('Nicolás Soto','nicolas@aulafix.test','tecnico','tecnico123'),('Coordinación TIC','admin@aulafix.test','admin',password)]:
    self.db.execute('INSERT INTO users(name,email,role,password) VALUES(?,?,?,?)',(n,e,r,p))
   for n,q,m in [('Teclado USB',8,3),('Mouse óptico',12,4),('Cable HDMI',5,2),('Fuente ATX',2,2),('Disco SSD 240 GB',3,2)]:self.db.execute('INSERT INTO stock(name,quantity,minimum) VALUES(?,?,?)',(n,q,m))
 def login(self,email,password):
  user=self.one('SELECT * FROM users WHERE email=? AND password=?',(email,password))
  if not user:raise BusinessError('Credenciales incorrectas')
  user.pop('password');return user
 def user(self,id):return self.one('SELECT id,name,email,role FROM users WHERE id=?',(id,))
 def log(self,tid,uid,action,detail):self.db.execute('INSERT INTO history(ticket_id,actor_id,action,detail,at) VALUES(?,?,?,?,?)',(tid,uid,action,detail,iso()))
 def ticket(self,tid):return self.one('''SELECT t.*,u.name AS reporter,COALESCE(a.name,'Sin asignar') AS assignee FROM tickets t JOIN users u ON t.reporter_id=u.id LEFT JOIN users a ON t.assignee_id=a.id WHERE t.id=?''',(tid,))
 def list_tickets(self,user):
  where='WHERE t.reporter_id=?' if user['role']=='alumno' else ''
  params=(user['id'],) if where else ()
  return self.rows('''SELECT t.*,u.name AS reporter,COALESCE(a.name,'Sin asignar') AS assignee FROM tickets t JOIN users u ON t.reporter_id=u.id LEFT JOIN users a ON t.assignee_id=a.id '''+where+''' ORDER BY CASE t.priority WHEN 'critica' THEN 4 WHEN 'alta' THEN 3 WHEN 'media' THEN 2 ELSE 1 END DESC,t.id DESC''',params)
 def create(self,actor,title,category,description,priority,location):
  if actor['role']!='alumno':raise BusinessError('Solo los alumnos pueden registrar incidencias')
  if priority not in PRIORITIES:raise BusinessError('Prioridad inválida')
  if category not in ('hardware','software','red','otro'):raise BusinessError('Categoría inválida')
  if not (5<=len(title.strip())<=100 and 10<=len(description.strip())<=1000 and 2<=len(location.strip())<=100):raise BusinessError('Revisá los datos: título 5-100, descripción 10-1000 y ubicación 2-100 caracteres')
  hours={'critica':4,'alta':12,'media':48,'baja':120}[priority]
  now=datetime.datetime.now(datetime.timezone.utc);due=(now+datetime.timedelta(hours=hours)).isoformat(timespec='seconds')
  with self.tx():
   cur=self.db.execute('INSERT INTO tickets(reporter_id,title,category,description,priority,location,status,created_at,updated_at,due_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(actor['id'],title.strip(),category,description.strip(),priority,location.strip(),'abierto',now.isoformat(timespec='seconds'),now.isoformat(timespec='seconds'),due))
   tid=cur.lastrowid;self.log(tid,actor['id'],'creación','Incidencia registrada')
  return self.ticket(tid)
 def assign(self,actor,tid,techid):
  if actor['role']!='admin':raise BusinessError('Solo administración puede asignar técnicos')
  with self.tx():
   t=self.ticket(tid);tech=self.user(techid)
   if not t:raise BusinessError('Incidencia inexistente')
   if not tech or tech['role']!='tecnico':raise BusinessError('El responsable debe ser técnico')
   if t['status'] in ('cerrado','cancelado'):raise BusinessError('No se puede asignar una incidencia finalizada')
   active=self.one("SELECT COUNT(*) AS n FROM tickets WHERE assignee_id=? AND status IN ('en_proceso','en_espera') AND id<>?",(techid,tid))['n']
   if active>=3:raise BusinessError('Este técnico alcanzó el cupo de 3 incidencias activas')
   self.db.execute('UPDATE tickets SET assignee_id=?,updated_at=? WHERE id=?',(techid,iso(),tid));self.log(tid,actor['id'],'asignación',tech['name'])
  return self.ticket(tid)
 def status(self,actor,tid,target,resolution=''):
  with self.tx():
   t=self.ticket(tid)
   if not t:raise BusinessError('Incidencia inexistente')
   if actor['role']=='alumno':
    if target!='cancelado' or t['reporter_id']!=actor['id'] or t['status']!='abierto':raise BusinessError('El alumno solo cancela sus incidencias abiertas')
   elif actor['role']=='tecnico':
    if t['assignee_id']!=actor['id']:raise BusinessError('Esta incidencia no está asignada a tu usuario')
    if target in ('cancelado','cerrado'):raise BusinessError('Esa acción corresponde a administración')
   if target not in TRANSITIONS.get(t['status'],set()):raise BusinessError('Cambio de estado no permitido')
   if target=='en_proceso' and not t['assignee_id']:raise BusinessError('Asigná un técnico antes de iniciar')
   if target=='resuelto' and len(resolution.strip())<10:raise BusinessError('Explicá la solución en al menos 10 caracteres')
   self.db.execute('UPDATE tickets SET status=?,resolution=CASE WHEN ?="resuelto" THEN ? ELSE resolution END,updated_at=? WHERE id=?',(target,target,resolution.strip(),iso(),tid));self.log(tid,actor['id'],'estado',f"{t['status']} → {target}")
  return self.ticket(tid)
 def consume(self,actor,tid,itemid,qty):
  if actor['role'] not in ('admin','tecnico'):raise BusinessError('No autorizado')
  try:qty=int(qty)
  except:raise BusinessError('Cantidad inválida')
  if qty<=0:raise BusinessError('La cantidad debe ser positiva')
  with self.tx():
   t=self.ticket(tid);item=self.one('SELECT * FROM stock WHERE id=?',(itemid,))
   if not t or not item:raise BusinessError('Incidencia o repuesto inexistente')
   if actor['role']=='tecnico' and t['assignee_id']!=actor['id']:raise BusinessError('No sos el técnico asignado')
   if t['status']!='en_proceso':raise BusinessError('Los repuestos solo se usan en incidencias en proceso')
   changed=self.db.execute('UPDATE stock SET quantity=quantity-? WHERE id=? AND quantity>=?',(qty,itemid,qty)).rowcount
   if not changed:raise BusinessError('Stock insuficiente')
   self.db.execute('INSERT INTO usage(ticket_id,stock_id,quantity,created_at) VALUES(?,?,?,?)',(tid,itemid,qty,iso()))
   self.log(tid,actor['id'],'repuesto',f'{qty} × {item["name"]}')
  return self.one('SELECT * FROM stock WHERE id=?',(itemid,))
 def dashboard(self):
  return {'tickets':self.one('SELECT COUNT(*) n FROM tickets')['n'],'open':self.one("SELECT COUNT(*) n FROM tickets WHERE status IN ('abierto','en_proceso','en_espera')")['n'],'critical':self.one("SELECT COUNT(*) n FROM tickets WHERE priority='critica' AND status NOT IN ('cerrado','cancelado')")['n'],'lowStock':self.one('SELECT COUNT(*) n FROM stock WHERE quantity<=minimum')['n']}
 def details(self,tid,user):
  t=self.ticket(tid)
  if not t or (user['role']=='alumno' and t['reporter_id']!=user['id']):raise BusinessError('Incidencia no disponible')
  return {'ticket':t,'history':self.rows('SELECT * FROM history WHERE ticket_id=? ORDER BY id DESC',(tid,)),'parts':self.rows('SELECT s.name,u.quantity FROM usage u JOIN stock s ON s.id=u.stock_id WHERE u.ticket_id=?',(tid,))}
