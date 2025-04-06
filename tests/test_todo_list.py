import unittest
import os
import sys
import json
import sqlite3
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['TG_TOKEN'] = 'dummy_token_for_testing'

class MockFilters:
    @staticmethod
    def command(update):
        return update.message and update.message.text and update.message.text.startswith('/')

with patch('telegram.ext.Filters', MockFilters):
    from handler import get_all_todos, show_todos, show_all_todos, show_completed_todos, show_pending_todos

TEST_DB = './tests/test_tobedo.sqlite3'

class TestTodoList(unittest.TestCase):

    def setUp(self):
        self.db_patcher = patch('handler.DB_NAME', TEST_DB)
        self.db_patcher.start()

        with sqlite3.connect(TEST_DB) as db:
            db.execute('''
                CREATE TABLE IF NOT EXISTS Replies (
                    message_and_chat_id VARCHAR(255) NOT NULL,
                    reply_and_chat_id VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    state TEXT,
                    PRIMARY KEY (message_and_chat_id),
                    UNIQUE (reply_and_chat_id)
                )
            ''')

            db.execute(
                '''
                INSERT OR REPLACE INTO Replies (message_and_chat_id, reply_and_chat_id, state, created_at)
                VALUES (?, ?, ?, datetime('now'))
                ''',
                ('123_101', '123_201', json.dumps({'Buy milk': True, 'Buy eggs': False}))
            )

            db.execute(
                '''
                INSERT OR REPLACE INTO Replies (message_and_chat_id, reply_and_chat_id, state, created_at)
                VALUES (?, ?, ?, datetime('now', '-1 day'))
                ''',
                ('123_102', '123_202', json.dumps({'Clean house': True}))
            )

            db.execute(
                '''
                INSERT OR REPLACE INTO Replies (message_and_chat_id, reply_and_chat_id, state, created_at)
                VALUES (?, ?, ?, datetime('now', '-2 days'))
                ''',
                ('123_103', '123_203', json.dumps({'Write code': False}))
            )

            db.commit()

    def tearDown(self):
        self.db_patcher.stop()

        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_get_all_todos(self):
        todos = get_all_todos('123')

        self.assertEqual(len(todos), 4)

        for todo in todos:
            self.assertIn('message_id', todo)
            self.assertIn('text', todo)
            self.assertIn('completed', todo)
            self.assertIn('created_at', todo)

    def test_get_all_todos_empty(self):
        todos = get_all_todos('456')
        self.assertEqual(len(todos), 0)

    @patch('handler.update_message_reply_text')
    def test_show_todos_all(self, mock_reply):
        update = MagicMock()
        update.message.chat_id = '123'
        context = MagicMock()

        show_todos(update, context)

        args = mock_reply.call_args[0][0]
        self.assertIn('Buy milk', args)
        self.assertIn('Buy eggs', args)
        self.assertIn('Clean house', args)
        self.assertIn('Write code', args)

    @patch('handler.update_message_reply_text')
    def test_show_todos_completed(self, mock_reply):
        update = MagicMock()
        update.message.chat_id = '123'
        context = MagicMock()

        show_todos(update, context, filter_completed=True)

        args = mock_reply.call_args[0][0]
        self.assertIn('Buy milk', args)
        self.assertIn('Clean house', args)
        self.assertNotIn('Buy eggs', args)
        self.assertNotIn('Write code', args)

    @patch('handler.update_message_reply_text')
    def test_show_todos_pending(self, mock_reply):
        update = MagicMock()
        update.message.chat_id = '123'
        context = MagicMock()

        show_todos(update, context, filter_completed=False)

        args = mock_reply.call_args[0][0]
        self.assertNotIn('Buy milk', args)
        self.assertNotIn('Clean house', args)
        self.assertIn('Buy eggs', args)
        self.assertIn('Write code', args)

    @patch('handler.update_message_reply_text')
    def test_show_todos_empty(self, mock_reply):
        update = MagicMock()
        update.message.chat_id = '456'
        context = MagicMock()

        show_todos(update, context)

        mock_reply.assert_called_once()
        args = mock_reply.call_args[0][0]
        self.assertIn('No todo items found', args)

if __name__ == '__main__':
    unittest.main()
