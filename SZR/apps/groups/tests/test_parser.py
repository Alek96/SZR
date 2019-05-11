import unittest

from groups.parser import csv_members_parse, csv_subgroup_and_members_parse


class CsvMembersParseTests(unittest.TestCase):
    csv_data_1 = '"surname";"name";0;0;999999'
    csv_data_2 = '"surname";"name";"second_name";0;0;999999'

    def test_incorrect_format(self):
        csv_data = "'surname';'name';0;999999"
        with self.assertRaises(ValueError):
            csv_members_parse(csv_data)

    def test_read_data(self):
        data = csv_members_parse(self.csv_data_1)
        self._test_read_data(data[0])

    def _test_read_data(self, data):
        self.assertEqual(data['surname'], 'surname')
        self.assertEqual(data['name'], 'name')
        self.assertEqual(data['inactive'], '0')
        self.assertEqual(data['resignation'], '0')
        self.assertEqual(data['index'], '999999')

    def test_read_data_with_second_name(self):
        data = csv_members_parse(self.csv_data_2)
        self._test_read_data_with_second_name(data[0])

    def _test_read_data_with_second_name(self, data):
        self._test_read_data(data)
        self.assertEqual(data['second_name'], 'second_name')

    def test_read_multiple_lines(self):
        data = csv_members_parse(self.csv_data_1 + '\n' + self.csv_data_2)
        self._test_read_data(data[0])
        self._test_read_data_with_second_name(data[1])


class CsvSubgroupAndMembersParseTest(unittest.TestCase):
    csv_data = '999999;"name";"surname";0;"CWI102, LAB102, WYK1";"103B-ISP-IN (G2-IN000-ISP-I2-1030)"'

    def test_incorrect_format(self):
        csv_data = "999999;'name';'surname';0;'CWI102, LAB102, WYK1'"
        with self.assertRaises(ValueError):
            csv_subgroup_and_members_parse(csv_data)

    def test_read_data(self):
        data = csv_subgroup_and_members_parse(self.csv_data)
        self._test_read_data(data[0])

    def _test_read_data(self, data):
        self.assertEqual(data['index'], '999999')
        self.assertEqual(data['name'], 'name')
        self.assertEqual(data['surname'], 'surname')
        self.assertEqual(data['inactive'], '0')
        self.assertEqual(data['groups'], ['CWI102', 'LAB102', 'WYK1'])
        self.assertEqual(data['programs'], '103B-ISP-IN (G2-IN000-ISP-I2-1030)')

    def test_read_multiple_lines(self):
        data = csv_subgroup_and_members_parse(self.csv_data + '\n' + self.csv_data)
        self._test_read_data(data[0])
        self._test_read_data(data[1])
