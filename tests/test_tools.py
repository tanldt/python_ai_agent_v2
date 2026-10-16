import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tools

class TestTools(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(tools.calculate('2 + 3 * 4'), '14')
        self.assertTrue(tools.calculate('__import__("os")').startswith('Error:'))
        self.assertTrue(tools.calculate('2 ** 100').startswith('Error:'))

    def test_sql(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(tools, 'DB_PATH', Path(directory) / 'sales.db'):
                tools.init_db()
                self.assertIn('Laptop', tools.query_database('SELECT product FROM sales LIMIT 1'))
                self.assertIn('SQL error', tools.query_database('DELETE FROM sales'))
                self.assertIn('SQL error', tools.query_database('SELECT 1; DROP TABLE sales'))

if __name__ == '__main__':
    unittest.main()
