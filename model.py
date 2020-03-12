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



str = "ahmed"
str.replace("q", "s")