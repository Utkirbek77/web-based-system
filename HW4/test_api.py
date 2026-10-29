
import os
import unittest

os.environ["TODO_DATABASE_URI"] = "sqlite:///:memory:"

import app as todo_app


class TodoApiTest(unittest.TestCase):

    def setUp(self):
        todo_app.app.config["TESTING"] = True
        self.client = todo_app.app.test_client()
        self.ctx = todo_app.app.app_context()
        self.ctx.push()
        todo_app.db.drop_all()
        todo_app.db.create_all()

    def tearDown(self):
        todo_app.db.session.remove()
        self.ctx.pop()

    def test_all_todos_are_returned_without_filter(self):
        self.client.post("/api/todos/", json={"text": "Milk", "done": True})
        self.client.post("/api/todos/", json={"text": "Book", "done": False})

        response = self.client.get("/api/todos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    def test_post_returns_201_and_note(self):
        response = self.client.post(
            "/api/todos/",
            json={"text": "Milk", "note": "Two liters"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["text"], "Milk")
        self.assertEqual(response.get_json()["note"], "Two liters")
        self.assertFalse(response.get_json()["done"])

    def test_note_defaults_to_empty_string(self):
        response = self.client.post(
            "/api/todos/",
            json={"text": "Book"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["note"], "")

    def test_get_single_todo(self):
        made = self.client.post(
            "/api/todos/",
            json={"text": "Milk"}
        ).get_json()

        response = self.client.get(f"/api/todos/{made['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], "Milk")

    def test_missing_todo_returns_404_json(self):
        response = self.client.get("/api/todos/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json()["message"],
            "999 번 할 일이 없습니다"
        )

    def test_patch_changes_only_done(self):
        made = self.client.post(
            "/api/todos/",
            json={"text": "Book", "note": "Library"}
        ).get_json()

        response = self.client.patch(
            f"/api/todos/{made['id']}",
            json={"done": True}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], "Book")
        self.assertEqual(response.get_json()["note"], "Library")
        self.assertTrue(response.get_json()["done"])

    def test_filter_done(self):
        self.client.post(
            "/api/todos/",
            json={"text": "Milk", "done": True}
        )

        self.client.post(
            "/api/todos/",
            json={"text": "Book", "done": False}
        )

        completed = self.client.get("/api/todos/?done=true")
        incomplete = self.client.get("/api/todos/?done=false")

        self.assertEqual(completed.status_code, 200)
        self.assertEqual(incomplete.status_code, 200)

        self.assertEqual(
            [item["text"] for item in completed.get_json()],
            ["Milk"]
        )

        self.assertEqual(
            [item["text"] for item in incomplete.get_json()],
            ["Book"]
        )

    def test_delete_returns_204_and_then_404(self):
        made = self.client.post(
            "/api/todos/",
            json={"text": "Delete me"}
        ).get_json()

        self.assertEqual(
            self.client.delete(
                f"/api/todos/{made['id']}"
            ).status_code,
            204
        )

        self.assertEqual(
            self.client.get(
                f"/api/todos/{made['id']}"
            ).status_code,
            404
        )

    def test_docs_url(self):
        response = self.client.get("/api/docs")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
