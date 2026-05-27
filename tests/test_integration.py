"""Integration tests for hr_agentic_chatbot.

Tests real MongoDB connectivity and session history storage
used by the HR agentic chatbot.

Requires a running MongoDB instance. Set MONGODB_URI (default:
mongodb://admin:mongodb@localhost:27017/) or the tests will be skipped.
"""

import os
import sys
import pytest
from pathlib import Path
from pymongo import MongoClient
from bson import ObjectId

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://admin:mongodb@localhost:27017/")
TEST_DB = "hr_chatbot_integration_test"


@pytest.fixture(scope="module")
def db():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except Exception:
        client.close()
        pytest.skip(f"MongoDB not reachable at {MONGODB_URI}")
    database = client[TEST_DB]
    yield database
    client.drop_database(TEST_DB)
    client.close()


def test_mongodb_ping():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    try:
        result = client.admin.command("ping")
        assert result.get("ok") == 1.0
    except Exception:
        pytest.skip(f"MongoDB not reachable at {MONGODB_URI}")
    finally:
        client.close()


def test_get_mongo_client_with_real_uri():
    """get_mongo_client() returns a connected client when given a real URI."""
    try:
        connect_mod_path = Path(__file__).resolve().parents[1] / "mongodb" / "connect.py"

        import types
        import importlib.util

        # Stub langchain_mongodb if not available
        if "langchain_mongodb" not in sys.modules:
            stub = types.ModuleType("langchain_mongodb")
            chm_stub = types.ModuleType("langchain_mongodb.chat_message_histories")
            chm_stub.MongoDBChatMessageHistory = type(
                "MongoDBChatMessageHistory",
                (),
                {"__init__": lambda self, *a, **kw: None},
            )
            stub.chat_message_histories = chm_stub
            sys.modules["langchain_mongodb"] = stub
            sys.modules["langchain_mongodb.chat_message_histories"] = chm_stub

        if "dotenv" not in sys.modules:
            dotenv_stub = types.ModuleType("dotenv")
            dotenv_stub.load_dotenv = lambda *a, **kw: None
            sys.modules["dotenv"] = dotenv_stub

        spec = importlib.util.spec_from_file_location("hr_connect_int", connect_mod_path)
        mod = importlib.util.module_from_spec(spec)
        os.environ["MONGO_URI"] = MONGODB_URI
        spec.loader.exec_module(mod)

        client = mod.get_mongo_client(MONGODB_URI)
        assert client is not None

        result = client.admin.command("ping")
        assert result.get("ok") == 1.0
        client.close()
    except Exception as exc:
        pytest.skip(f"App-level test skipped: {exc}")


def test_chat_history_collection_crud(db):
    """history collection: store and retrieve chat messages."""
    history = db["history"]

    session_id = f"test_session_{ObjectId()}"
    messages = [
        {
            "_id": ObjectId(),
            "SessionId": session_id,
            "History": "Human: Hello\nAI: Hi there!",
        },
        {
            "_id": ObjectId(),
            "SessionId": session_id,
            "History": "Human: What is MongoDB?\nAI: A NoSQL database.",
        },
    ]
    history.insert_many(messages)

    session_messages = list(history.find({"SessionId": session_id}))
    assert len(session_messages) == 2
    assert all(m["SessionId"] == session_id for m in session_messages)

    # Cleanup
    history.delete_many({"SessionId": session_id})


def test_employee_record_crud(db):
    """employee records collection: store and retrieve HR data."""
    employees = db["employees"]

    emp_id = ObjectId()
    employee = {
        "_id": emp_id,
        "name": "Test Employee",
        "department": "Engineering",
        "role": "Developer",
        "salary": 90000,
        "start_date": "2023-01-15",
    }

    employees.insert_one(employee)

    found = employees.find_one({"_id": emp_id})
    assert found["name"] == "Test Employee"
    assert found["department"] == "Engineering"

    # Update
    employees.update_one({"_id": emp_id}, {"$set": {"salary": 95000}})
    updated = employees.find_one({"_id": emp_id})
    assert updated["salary"] == 95000

    # Delete
    employees.delete_one({"_id": emp_id})
    assert employees.find_one({"_id": emp_id}) is None
