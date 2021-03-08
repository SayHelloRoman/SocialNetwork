import psycopg2
import json

class DB:
    def __init__(self):
        with open("data.json") as file:
            self.db = psycopg2.connect(
                **json.load(file)
            )

    def search(self, name):
        cursor = self.db.cursor()

        cursor.execute(f"SELECT id, pasword, status FROM users WHERE id = '{name}'")

        r = cursor.fetchall()
        cursor.close()
        return r

    def update(self, nick, new_nick, status):
        cursor = self.db.cursor()
        cursor.execute(f"UPDATE users SET  id='{new_nick}',status='{status}' WHERE id='{nick}';")
        
        self.db.commit()
        cursor.close()

    def sing_up(self, nick, password):
        cursor = self.db.cursor()

        try:
            cursor.execute(f"INSERT INTO users values('{nick}', '', '{password}')")

        except psycopg2.errors.UniqueViolation:
            return False

        except psycopg2.errors.InFailedSqlTransaction:
            cursor.rollback()
        
        else:
            self.db.commit()

        cursor.close()
        return True
