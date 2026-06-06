from pathlib import Path
import tempfile
import unittest

from opencode_harness.messages import Message
from opencode_harness.session import SessionState, TodoItem


class SessionTests(unittest.TestCase):
    def test_save_and_load_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "session.json"
            session = SessionState(
                task="fix tests",
                steps=2,
                status="running",
                messages=[Message("user", "hello")],
                todos=[TodoItem("inspect", "done")],
            )

            session.save(path)
            loaded = SessionState.load(path)

            self.assertEqual(loaded.task, "fix tests")
            self.assertEqual(loaded.steps, 2)
            self.assertEqual(loaded.messages[0].content, "hello")
            self.assertEqual(loaded.todos[0].status, "done")
