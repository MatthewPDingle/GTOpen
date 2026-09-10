import copy,json,tempfile,unittest,os
from pathlib import Path
from compare_build_pairs import compare_rows,verified,IDENTITY,same_existing_file
class TestComparator(unittest.TestCase):
 def row(self):
  r={k:None for k in IDENTITY};r.update(phase="verified",mode="load",operation_ms=10,topology={"topology_hash":"abc","nodes":2,"action_nodes":1,"edges":1,"action_string_len_bytes":4,"action_vec_capacity_bytes":64,"action_string_capacity_bytes":8,"action_retained_bytes":72},native_arenas={"arrays":[{"index":i,"elements":169,"hash":"abc","nonzero_bytes":1} for i in range(2)]});return r
 def test_capacity(self):
  a=self.row();b=copy.deepcopy(a);b["topology"]["action_string_capacity_bytes"]+=12;b["topology"]["action_retained_bytes"]+=12
  self.assertEqual(compare_rows(a,b)["capacity_bytes"]["action_retained_bytes"]["delta"],12)
 def test_identity(self):
  a=self.row()
  for k in IDENTITY:
   b=copy.deepcopy(a);b[k]="changed"
   with self.assertRaises(ValueError):compare_rows(a,b)
  b=copy.deepcopy(a);b["topology"]["topology_hash"]="changed"
  with self.assertRaises(ValueError):compare_rows(a,b)
 def test_missing(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x";t={"phase":"timed","mode":"load","operation_ms":10};r=self.row()
   def put(rows):p.write_text("".join("BUILD_BENCH "+json.dumps(x)+"\n" for x in rows),encoding="utf-8")
   put([t]);self.assertRaises(ValueError,verified,p)
   put([t,r,r]);self.assertRaises(ValueError,verified,p)
   put([t,r]);self.assertEqual(verified(p)["operation_ms"],10)
   del r["typed_profile_hash"];put([t,r]);self.assertRaises(ValueError,verified,p)
 def test_existing_file_identity_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/"a";b=Path(d)/"b";a.write_text("same contents");b.write_text("same contents")
   self.assertTrue(same_existing_file(a,a))
   self.assertFalse(same_existing_file(a,b))
   self.assertFalse(same_existing_file(a,Path(d)/"absent"))
 @unittest.skipUnless(os.name=="nt","Windows extended path syntax")
 def test_windows_extended_prefix_identity(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/"same file.txt";a.write_text("fixture")
   extended=chr(92)*2+"?"+chr(92)+str(a.resolve())
   self.assertNotEqual(str(a),extended)
   self.assertTrue(same_existing_file(a,extended))
   self.assertTrue(same_existing_file(extended,a))
if __name__=="__main__":unittest.main()
