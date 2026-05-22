import importlib.util
import sys
import types
import unittest
from pathlib import Path


class RuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        histories = types.ModuleType("langchain_mongodb.chat_message_histories")

        class MongoDBChatMessageHistory:
            def __init__(self, uri, session_id, database_name=None, collection_name=None):
                self.uri = uri
                self.session_id = session_id
                self.database_name = database_name
                self.collection_name = collection_name

        histories.MongoDBChatMessageHistory = MongoDBChatMessageHistory
        sys.modules["langchain_mongodb.chat_message_histories"] = histories

        target = Path(__file__).resolve().parents[1] / "mongodb" / "connect.py"
        spec = importlib.util.spec_from_file_location("hr_connect", target)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_get_mongo_client_success_and_failure(self):
        class GoodAdmin:
            @staticmethod
            def command(_):
                return {"ok": 1}

        class GoodClient:
            def __init__(self, *args, **kwargs):
                self.admin = GoodAdmin()

        class BadAdmin:
            @staticmethod
            def command(_):
                raise RuntimeError("nope")

        class BadClient:
            def __init__(self, *args, **kwargs):
                self.admin = BadAdmin()

        self.mod.MongoClient = GoodClient
        self.assertIsNotNone(self.mod.get_mongo_client("mongodb://ok"))

        self.mod.MongoClient = BadClient
        self.assertIsNone(self.mod.get_mongo_client("mongodb://bad"))

    def test_get_session_history_contract(self):
        history = self.mod.get_session_history("s1")
        self.assertEqual(history.session_id, "s1")
        self.assertEqual(history.collection_name, "history")


if __name__ == "__main__":
    unittest.main()
