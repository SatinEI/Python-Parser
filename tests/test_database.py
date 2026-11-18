import sqlite3
import unittest

from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):
    def setUp(self):
        self.repository = DatabaseRepository(':memory:')
        self.addCleanup(self.repository.connection.close)

    def test_add(self):
        self.assertTrue(self.repository.add(1, 'alice', 'Привет'))
        self.assertEqual(self.repository.get_by_id(1)['message'], 'Привет')

    def test_add_duplicate_id(self):
        self.repository.add(1, 'alice', 'Привет')
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.add(1, 'bob', 'Другое сообщение')

    def test_add_invalid_types(self):
        for data in [('1', 'alice', 'Текст'), (True, 'alice', 'Текст'),
                     (1, 123, 'Текст'), (1, 'alice', None)]:
            with self.subTest(data=data), self.assertRaises(TypeError):
                self.repository.add(*data)

    def test_add_too_long_strings(self):
        for name, message in [('a' * 257, 'Текст'), ('alice', 'x' * 8097)]:
            with self.subTest(name_length=len(name)), self.assertRaises(ValueError):
                self.repository.add(1, name, message)

    def test_add_maximum_lengths(self):
        self.assertTrue(self.repository.add(1, 'a' * 256, 'x' * 8096))

    def test_get_by_id(self):
        self.repository.add(1, 'alice', 'Привет')
        self.assertEqual(self.repository.get_by_id(1),
                         {'id': 1, 'name': 'alice', 'message': 'Привет'})

    def test_get_by_id_missing(self):
        self.assertIsNone(self.repository.get_by_id(99))

    def test_get_by_name(self):
        self.repository.add(1, 'alice', 'Первое')
        self.repository.add(2, 'bob', 'Второе')
        self.repository.add(3, 'alice', 'Третье')
        comments = self.repository.get_by_name('alice')
        self.assertEqual([comment['id'] for comment in comments], [1, 3])

    def test_get_by_name_missing(self):
        self.assertEqual(self.repository.get_by_name('nobody'), [])

    def test_update(self):
        self.repository.add(1, 'alice', 'Первое')
        self.assertTrue(self.repository.update(1, 'Новое'))
        self.assertEqual(self.repository.get_by_id(1)['message'], 'Новое')

    def test_update_missing(self):
        self.assertFalse(self.repository.update(99, 'Новое'))

    def test_update_invalid_message(self):
        self.repository.add(1, 'alice', 'Первое')
        with self.assertRaises(TypeError):
            self.repository.update(1, None)
        with self.assertRaises(ValueError):
            self.repository.update(1, 'x' * 8097)
        self.assertEqual(self.repository.get_by_id(1)['message'], 'Первое')

    def test_delete(self):
        self.repository.add(1, 'alice', 'Привет')
        self.assertTrue(self.repository.delete(1))
        self.assertIsNone(self.repository.get_by_id(1))

    def test_delete_missing(self):
        self.assertFalse(self.repository.delete(99))


if __name__ == '__main__':
    unittest.main()
