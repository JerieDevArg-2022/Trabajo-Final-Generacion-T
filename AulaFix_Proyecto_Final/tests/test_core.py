import sys,unittest,tempfile,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from core import Store,BusinessError
class TestAulaFix(unittest.TestCase):
 def setUp(self):
  self.s=Store();self.s.seed();self.al=self.s.login('martina@aulafix.test','alumno123');self.al2=self.s.login('tomas@aulafix.test','alumno123');self.te=self.s.login('lucia@aulafix.test','tecnico123');self.te2=self.s.login('nicolas@aulafix.test','tecnico123');self.ad=self.s.login('admin@aulafix.test','AulaFix2026!')
 def tearDown(self):self.s.db.close()
 def make(self,p='media',user=None):return self.s.create(user or self.al,'Computadora sin pantalla','hardware','No se ve imagen desde ayer',p,'Aula 4')
 def test_seed(self):self.assertEqual(len(self.s.rows('SELECT * FROM stock')),5)
 def test_login(self):self.assertEqual(self.ad['role'],'admin')
 def test_bad_password(self):
  with self.assertRaises(BusinessError):self.s.login('admin@aulafix.test','nope')
 def test_create(self):self.assertEqual(self.make()['status'],'abierto')
 def test_due_critical_before_low(self):
  from datetime import datetime
  a=self.make('critica');b=self.make('baja');self.assertLess(datetime.fromisoformat(a['due_at']),datetime.fromisoformat(b['due_at']))
 def test_bad_priority(self):
  with self.assertRaises(BusinessError):self.make('maxima')
 def test_bad_description(self):
  with self.assertRaises(BusinessError):self.s.create(self.al,'Corto','hardware','breve','alta','Aula')
 def test_tech_cannot_create(self):
  with self.assertRaises(BusinessError):self.make(user=self.te)
 def test_student_only_own(self):
  self.make();self.assertEqual(len(self.s.list_tickets(self.al2)),0)
 def test_student_no_assign(self):
  t=self.make()
  with self.assertRaises(BusinessError):self.s.assign(self.al,t['id'],self.te['id'])
 def test_assign_nontech(self):
  t=self.make()
  with self.assertRaises(BusinessError):self.s.assign(self.ad,t['id'],self.al['id'])
 def test_assign(self):
  t=self.make();self.assertEqual(self.s.assign(self.ad,t['id'],self.te['id'])['assignee_id'],self.te['id'])
 def test_no_start_unassigned(self):
  t=self.make()
  with self.assertRaises(BusinessError):self.s.status(self.ad,t['id'],'en_proceso')
 def test_start(self):
  t=self.make();self.s.assign(self.ad,t['id'],self.te['id']);self.assertEqual(self.s.status(self.te,t['id'],'en_proceso')['status'],'en_proceso')
 def test_other_tech_forbidden(self):
  t=self.make();self.s.assign(self.ad,t['id'],self.te['id'])
  with self.assertRaises(BusinessError):self.s.status(self.te2,t['id'],'en_proceso')
 def test_invalid_transition(self):
  t=self.make()
  with self.assertRaises(BusinessError):self.s.status(self.ad,t['id'],'resuelto','Listo reparado')
 def test_need_resolution(self):
  t=self.make();self.s.assign(self.ad,t['id'],self.te['id']);self.s.status(self.te,t['id'],'en_proceso')
  with self.assertRaises(BusinessError):self.s.status(self.te,t['id'],'resuelto','OK')
 def test_full_cycle(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso');self.s.status(self.te,i,'resuelto','Reemplacé el cable HDMI');self.assertEqual(self.s.status(self.ad,i,'cerrado')['status'],'cerrado')
 def test_student_cancel(self):self.assertEqual(self.s.status(self.al,self.make()['id'],'cancelado')['status'],'cancelado')
 def test_student_cant_cancel_other(self):
  with self.assertRaises(BusinessError):self.s.status(self.al2,self.make()['id'],'cancelado')
 def test_tech_cannot_close(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso');self.s.status(self.te,i,'resuelto','Reparación realizada correctamente')
  with self.assertRaises(BusinessError):self.s.status(self.te,i,'cerrado')
 def test_consume(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso');before=self.s.one('SELECT quantity FROM stock WHERE id=1')['quantity'];after=self.s.consume(self.te,i,1,2)['quantity'];self.assertEqual(before-after,2)
 def test_no_negative_stock(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso')
  with self.assertRaises(BusinessError):self.s.consume(self.te,i,1,99)
 def test_no_zero_quantity(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso')
  with self.assertRaises(BusinessError):self.s.consume(self.te,i,1,0)
 def test_part_only_in_progress(self):
  t=self.make()
  with self.assertRaises(BusinessError):self.s.consume(self.ad,t['id'],1,1)
 def test_wrong_tech_consumption(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso')
  with self.assertRaises(BusinessError):self.s.consume(self.te2,i,1,1)
 def test_tech_capacity(self):
  for _ in range(3):
   i=self.make()['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso')
  with self.assertRaises(BusinessError):self.s.assign(self.ad,self.make()['id'],self.te['id'])
 def test_history(self):
  t=self.make();self.s.assign(self.ad,t['id'],self.te['id']);self.assertEqual(len(self.s.details(t['id'],self.ad)['history']),2)
 def test_privacy(self):
  t=self.make()
  with self.assertRaises(BusinessError):self.s.details(t['id'],self.al2)
 def test_stock_alert(self):self.assertGreaterEqual(self.s.dashboard()['lowStock'],1)
 def test_reopen(self):
  t=self.make();i=t['id'];self.s.assign(self.ad,i,self.te['id']);self.s.status(self.te,i,'en_proceso');self.s.status(self.te,i,'resuelto','Problema reparado totalmente');self.assertEqual(self.s.status(self.ad,i,'en_proceso')['status'],'en_proceso')
if __name__=='__main__':unittest.main()
