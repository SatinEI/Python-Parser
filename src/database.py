import sqlite3


class DatabaseRepository:
    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096)
            )
        """)
        self.connection.commit()
    @staticmethod
    def convert_result(result):
        if result is None:
            return None
        return {
            "id": result[0],
            "name": result[1],
            "message": result[2]
        }
    def get_by_id(self, comment_id: int):
        result = self.connection.execute(
            "SELECT * FROM comments where id = ?",
            (comment_id,)
        ).fetchone()

        return self.convert_result(result)

    def get_by_name(self, username: str):
        result = self.connection.execute(
            "SELECT * FROM comments WHERE name = ?",
            (username,)
        ).fetchall()

        comments = []

        for row in result:
            comments.append(self.convert_result(row))
        return comments

    def add(self, comment_id: int, username: str, message: str):

        if type(comment_id) is not int:
            raise TypeError("ID должен быть целым числом")

        if not isinstance(username, str):
            raise TypeError("Имя должно быть строкой")

        if not isinstance(message, str):
            raise TypeError("Сообщение должно быть строкой")

        if len(username) > 256:
            raise ValueError("Имя слишком длинное")

        if len(message) > 8096:
            raise ValueError("Сообщение слишком длинное")

        self.connection.execute(
            "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
            (comment_id, username, message)
        )

        self.connection.commit()
        return True

    def update(self, comment_id: int, new_message: str):
        if type(comment_id) is not int:
            raise TypeError("ID должен быть целым числом")
        if not isinstance(new_message, str):
            raise TypeError("Сообщение должно быть строкой")
        if len(new_message) > 8096:
            raise ValueError("Сообщение слишком длинное")
        cursor = self.connection.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id)
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete(self, comment_id: int):
        if type(comment_id) is not int:
            raise TypeError("ID должен быть целым числом")
        cursor = self.connection.execute(
            "DELETE FROM comments WHERE id = ?", (comment_id,)
        )
        self.connection.commit()
        return cursor.rowcount > 0
