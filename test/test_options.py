import unittest

from data_migrator.models.options import Options
from data_migrator.models import Model, IntField


class OptionsModel:
    pass

FIELDS = {
    "a": IntField(),
    "b": IntField(),
    "c": IntField()
}


class TestOptions(unittest.TestCase):

    def test_init_default(self):
        '''model options initialization'''
        class MetaA:
                pass

        o = Options(OptionsModel, MetaA, {})
        self.assertEqual(o.remark, 'remark')
        self.assertEqual(o.model_name, "OptionsModel") # Class name in lower case by default
        self.assertEqual(o.drop_if_none, [])
        self.assertFalse(o.drop_non_unique)
        self.assertFalse(o.fail_non_unique)
        self.assertEqual(o.file_name, None)


    def test_init_settings(self):
        '''model options initialization'''
        class MetaB:
            remark = "bla_remark"
            table_name = "bla_table"
            drop_if_none = ["a", "b"]
            fail_non_unique = True
            file_name = 'bla_file.sql'

        o = Options(OptionsModel, MetaB, FIELDS)
        self.assertEqual(o.remark, 'bla_remark')
        self.assertEqual(o.table_name, "bla_table") # Class name in lower case by default
        self.assertEqual(o.drop_if_none, ["a", "b"])
        self.assertFalse(o.drop_non_unique)
        self.assertTrue(o.fail_non_unique)
        self.assertEqual(o.file_name, 'bla_file.sql')

if __name__ == '__main__':
    unittest.main()
