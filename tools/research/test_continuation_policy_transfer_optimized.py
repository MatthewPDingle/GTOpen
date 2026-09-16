import pathlib
import unittest
from unittest.mock import patch
import continuation_policy_transfer_optimized as optimized


class OptimizedTransferChecks(unittest.TestCase):
    def test_failed_runtime_blocks_optimized_policy_study(self):
        def read(path):
            return {'accuracy_screen_passed':True} if path.name=='evaluation.json' else {'within_runtime_target':False}
        with patch.object(optimized.study,'read',side_effect=read):
            with self.assertRaises(AssertionError):optimized.selection('N17')

    def test_adapter_source_is_in_signed_manifest(self):
        value=optimized.study.signed(dict(inputs={},jobs=[]))
        old_id=value['id'];optimized.include_adapter(pathlib.Path('manifest.json'),value)
        self.assertNotEqual(value['id'],old_id)
        self.assertEqual(value,optimized.study.signed({k:v for k,v in value.items() if k!='id'}))
        self.assertIn('tools/research/continuation_policy_transfer_optimized.py',value['inputs'])

    def test_shared_original_namespace_is_not_mutated(self):
        old=optimized.original.selection;old_out=optimized.original.OUT;old_freeze=optimized.study.freeze
        module=optimized.adapter()
        self.assertIs(optimized.original.selection,old)
        self.assertEqual(optimized.original.OUT,old_out)
        self.assertIs(optimized.study.freeze,old_freeze)
        self.assertIs(module.selection,optimized.selection)


if __name__=='__main__':unittest.main()
