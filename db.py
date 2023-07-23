import sqlite3
from url import unt

class DB:
    def __init__(self, db_name):
        self.connect = sqlite3.connect(db_name)
        self.cursor = self.connect.cursor()
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    name TEXT,
    currency TEXT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
    );""")
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pm TEXT NOT NULL,
    value REAL NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);""")
        self.connect.commit()

    def user_exist(self, user_id) -> bool:
        result = self.cursor.execute('SELECT id FROM user WHERE id = ?', (user_id,))
        return bool(len(result.fetchall()))

    def new_user(self, user_id, username, currency) -> None:
        if not self.user_exist(user_id):
            self.cursor.execute('INSERT INTO user(id, name, currency) VALUES (?, ?, ?)', (user_id, username, currency))
            self.connect.commit()
        else:
            pass

    def currency(self, user_id) -> str:
        self.cursor.execute('SELECT currency FROM user WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_data(self, user_id, value, pm: str) -> None:
        self.cursor.execute('INSERT INTO data(user_id, value, pm) VALUES (?,?,?)', (user_id, value, pm))
        self.connect.commit()

    def history(self, user_id, period: str = 'whole_time') -> list:
        result: list = []
        balance: float = 0
        t = 'start of year'
        if period != 'whole_time':
            if period == 'day':
                t: str = 'start of day'
            elif period == 'week':
                t: str = '-6 days'
            elif period == 'month':
                t: str = 'start of month'
            elif period == 'year':
                t: str = 'start of year'
            self.cursor.execute(f"SELECT pm, value, date FROM data WHERE user_id = ? and date BETWEEN datetime('now', '{t}') AND datetime('now', 'localtime') ORDER BY date", (user_id,))
            result = self.cursor.fetchall()
            self.cursor.execute(f"SELECT value FROM data WHERE user_id = ? and pm= 'plus' and date BETWEEN datetime('now', '{t}') AND datetime('now', 'localtime')", (user_id,))
            sum_1 = sum(unt(self.cursor.fetchall()))
            self.cursor.execute(f"SELECT value FROM data WHERE user_id = ? and pm = 'minus' and date BETWEEN datetime('now', '{t}') AND datetime('now', 'localtime')", (user_id,))
            sum_2: int = sum(unt(self.cursor.fetchall()))
        else:
            self.cursor.execute(f"SELECT pm, value, date FROM data WHERE user_id = ? ORDER BY date", (user_id,))
            result = self.cursor.fetchall()
            self.cursor.execute("SELECT value FROM data WHERE user_id = ? and pm = 'plus'", (user_id,))
            sum_1: int = sum(unt(self.cursor.fetchall()))
            self.cursor.execute("SELECT value FROM data WHERE user_id = ? and pm = 'minus'", (user_id,))
            sum_2: int = sum(unt(self.cursor.fetchall()))
        res = sum_1 - sum_2
        return [result, res]

    def del_last(self, user_id) -> None:
        self.cursor.execute('DELETE FROM data WHERE date = (SELECT MAX(date) FROM data WHERE user_id = ?) and user_id = ?', (user_id, user_id))
        self.connect.commit()