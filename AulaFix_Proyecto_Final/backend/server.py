import os,sys,json,secrets,threading,hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from http.cookies import SimpleCookie
sys.path.insert(0,str(Path(__file__).parent))
from core import Store,BusinessError
ROOT=Path(__file__).resolve().parent.parent
DB=Store(os.getenv('DB_PATH','/tmp/aulafix.sqlite3'))
ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD','')
if os.getenv('APP_ENV')=='production' and len(ADMIN_PASSWORD)<8:raise RuntimeError('Configurá ADMIN_PASSWORD (mínimo 8 caracteres) en Render')
DB.seed(ADMIN_PASSWORD or 'Admin2026!')
TOKENS={};LOCK=threading.RLock()
class Handler(BaseHTTPRequestHandler):
 def send_json(self,data,status=200,headers=None):
  payload=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
  for k,v in (headers or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(payload)
 def auth(self):
  c=SimpleCookie()
  try:c.load(self.headers.get('Cookie',''))
  except:return None
  token=c.get('session');return DB.user(TOKENS.get(token.value,0)) if token else None
 def serve_static(self,path):
  path={'/':'/index.html'}.get(path,path)
  file=(ROOT/'frontend'/path.lstrip('/')).resolve()
  if not file.is_relative_to((ROOT/'frontend').resolve()) or not file.is_file():return self.send_error(404)
  content=file.read_bytes();ctype={'.html':'text/html','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml'}.get(file.suffix,'application/octet-stream')
  self.send_response(200);self.send_header('Content-Type',ctype+'; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(content)
 def do_GET(self):
  p=self.path.split('?')[0]
  if not p.startswith('/api/'):return self.serve_static(p)
  try:
   if p=='/api/health':return self.send_json({'ok':True,'service':'AulaFix'})
   if p=='/api/session':return self.send_json({'user':self.auth()})
   u=self.auth()
   if not u:return self.send_json({'error':'Iniciá sesión para continuar'},401)
   if p=='/api/tickets':return self.send_json({'tickets':DB.list_tickets(u)})
   if p=='/api/stock':
    if u['role']=='alumno':raise BusinessError('Acceso restringido')
    return self.send_json({'stock':DB.rows('SELECT * FROM stock ORDER BY name')})
   if p=='/api/staff':
    if u['role']!='admin':raise BusinessError('Acceso restringido')
    return self.send_json({'staff':DB.rows("SELECT id,name FROM users WHERE role='tecnico'")})
   if p=='/api/dashboard':return self.send_json({'dashboard':DB.dashboard()})
   if p.startswith('/api/tickets/'):
    return self.send_json(DB.details(int(p.split('/')[3]),u))
   return self.send_json({'error':'Ruta inexistente'},404)
  except (ValueError,BusinessError) as e:return self.send_json({'error':str(e)},400)
 def do_POST(self):
  try:
   length=int(self.headers.get('Content-Length',0))
   if length>20000:raise BusinessError('Solicitud demasiado grande')
   body=json.loads(self.rfile.read(length) or b'{}');p=self.path.split('?')[0]
   if p=='/api/login':
    u=DB.login(body.get('email',''),body.get('password',''));token=secrets.token_urlsafe(32)
    with LOCK:TOKENS[token]=u['id']
    return self.send_json({'user':u},headers={'Set-Cookie':f'session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=86400'})
   if p=='/api/logout':
    raw=self.headers.get('Cookie','');c=SimpleCookie();c.load(raw);t=c.get('session')
    if t:
     with LOCK:TOKENS.pop(t.value,None)
    return self.send_json({'ok':True},headers={'Set-Cookie':'session=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/'})
   u=self.auth()
   if not u:return self.send_json({'error':'Sesión requerida'},401)
   if p=='/api/tickets':return self.send_json({'ticket':DB.create(u,body.get('title',''),body.get('category',''),body.get('description',''),body.get('priority',''),body.get('location',''))},201)
   seg=p.strip('/').split('/')
   if len(seg)==4 and seg[:2]==['api','tickets']:
    tid=int(seg[2]);action=seg[3]
    if action=='assign':result=DB.assign(u,tid,int(body.get('technician',0)))
    elif action=='status':result=DB.status(u,tid,body.get('status',''),body.get('resolution',''))
    elif action=='part':result=DB.consume(u,tid,int(body.get('item',0)),body.get('quantity',0))
    else:return self.send_json({'error':'Acción desconocida'},404)
    return self.send_json({'result':result})
   return self.send_json({'error':'Ruta inexistente'},404)
  except (ValueError,TypeError,json.JSONDecodeError,BusinessError) as e:return self.send_json({'error':str(e)},400)
 def log_message(self,*args):pass
if __name__=='__main__':
 port=int(os.getenv('PORT','8000'));print('AulaFix listening on',port,flush=True)
 ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
