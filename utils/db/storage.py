import sqlite3 as lite


class DatabaseManager(object):

    def __init__(self, path):
        self.conn = lite.connect(path)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()



    def create_tables(self):
        self.query("CREATE TABLE IF NOT EXISTS exams (idx INTEGER PRIMARY KEY, code TEXT, title TEXT, about TEXT, num_questions INTEGER, correct TEXT, running INTEGER)")
        # self.query('CREATE TABLE IF NOT EXISTS current (correct text, option integer)')
        self.query("CREATE TABLE IF NOT EXISTS submissions(idx INTEGER PRIMARY KEY, exid INTEGER, userid TEXT, date TEXT, corr INTEGER)")
        self.query('CREATE TABLE IF NOT EXISTS user (idx INTEGER PRIMARY KEY, userid TEXT, fullname TEXT, username TEXT, regdate TEXT)')

    def query(self, arg, values=None):
        if values == None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()

    def fetchone(self, arg, values=None):
        if values == None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        if values == None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()


'''
current: correct, option
user: idx, answered
'''