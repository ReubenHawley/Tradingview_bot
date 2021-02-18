import sqlite3
import os


script_dir = os.path.abspath("../data/tvBot.db")
connection = sqlite3.connect(script_dir)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute(""" SELECT * FROM users """)
traders = dict(result=[dict(r) for r in cursor.fetchall()])
print(traders)