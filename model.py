import sqlite3


class Model:
    def __init__(self):
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()

    def addTodata(self, data):
        with self.conn:
            self.cur.execute('''INSERT INTO data VALUES (?,?,?,?,?,?)''', data)

    def findUrl(self, url):
        self.cur.execute('''SELECT page_url FROM data WHERE page_url = (:url)''', {"url": url})
        value = self.cur.fetchone()
        return value

    def getAllRecords(self):
        """:return list of tuples"""
        self.cur.execute('''SELECT name, address, phone, email, website FROM data''')
        data = self.cur.fetchall()
        return data

    def clearDatabase(self):
        with self.conn:
            self.cur.execute("DELETE FROM data")

    # def findRecord(self, name, address, phone):
    #     self.cur.execute('''SELECT * FROM data WHERE name = (?) AND address = (?) AND phone = (?)''',
    #                      (name, address, phone))
    #     print(self.cur.fetchone())
