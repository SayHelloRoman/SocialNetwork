import psycopg2
import json


with open("data.json") as file:
    db = psycopg2.connect(
        **json.load(file)
    )

cursor = db.cursor()
cursor.execute("""
CREATE TABLE users
(
    Id VARCHAR(20) NOT NULL PRIMARY KEY,
    status TEXT,
    pasword VARCHAR(20)
);
""")

cursor.close()
db.commit()
db.close()
