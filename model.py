import sqlite3


class Model:
    def __init__(self):
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()

    def addTodata(self, data):
        with self.conn:
            self.cur.execute('''INSERT INTO data VALUES (?,?,?,?,?)''', data)
            

