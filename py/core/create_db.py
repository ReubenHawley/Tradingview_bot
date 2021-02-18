import sqlite3


class Database:
    def __init__(self):
        """instantiate database"""
        self.connection = sqlite3.connect('../data/tvBot.db')
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                api_key TEXT NOT NULL UNIQUE,
                api_secret TEXT NOT NULL UNIQUE,
                trendfollower TEXT NOT NULL,
                twopercent TEXT NOT NULL,
                gridtrader TEXT NOT NULL
            )
        """)
        return 'successfully created database'

    def add_new_user(self):
        if self.connection:
            id = input('please enter userid: ')
            name = input('please enter your name: ')
            API_ID = input('please enter (1) trading account api id: ')
            API_KEY = input('please enter (2) trading account api secret key: ')
            email_address = input('please enter your email address')
            trendfollower = input('is this the trendfollowing strat? true/false: ')
            twopercent = input('is this the 2% strat? true/false: ')
            gridtrader = input('is this the gridtrader strat? true/false: ')

            self.cursor.execute("""INSERT INTO users VALUES
                    (:key,
                    ':username:',
                    ':email',
                    ':api_key',
                    ':api_secret',
                    ':trendfollower',
                    ':twopercent',
                    ':gridtrader'
                    )
                    """, {
                'key': id,
                'username': name,
                'email': email_address,
                'api_key': API_ID,
                'api_secret': API_KEY,
                'trendfollower': trendfollower,
                'twopercent': twopercent,
                'gridtrader': gridtrader
            })
            self.connection.commit()
            self.cursor.close()
            return "user successfully added"
        else:
            print('connection closed, reestablishing connection')
            self.connection = sqlite3.connect('../data/tvBot.db')
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            self.add_new_user()


if __name__ == '__main__':
    tvbot_users = Database()
    tvbot_users.add_new_user()
