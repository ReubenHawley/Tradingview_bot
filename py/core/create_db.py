import sqlite3

"instantiate database"
connection = sqlite3.connect('../data/tvBot.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# cursor.execute("""CREATE TABLE IF NOT EXISTS users (
#         user_id INTEGER PRIMARY KEY,
#         username TEXT NOT NULL,
#         email TEXT NOT NULL,
#         api_key TEXT NOT NULL UNIQUE,
#         api_secret TEXT NOT NULL UNIQUE,
#         trendfollower TEXT NOT NULL,
#         twopercent TEXT NOT NULL,
#         gridtrader TEXT NOT NULL
#     )
# """)
def delete_user():
    "instantiate database"
    connection = sqlite3.connect('../data/tvBot.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""DELETE FROM users WHERE user_id='6'""")


def add_new_user():
    user_id = int(input('please enter user id: '))
    name = str(input('please enter your name: '))
    API_ID = str(input('please enter (1) trading account api id: '))
    API_KEY = str(input('please enter (2) trading account api secret key: '))
    email_address = str(input('please enter your email address'))
    trendfollower = str(input('is this the trendfollowing strat? true/false: '))
    twopercent = str(input('is this the 2% strat? true/false: '))
    gridtrader = str(input('is this the gridtrader strat? true/false: '))

    "instantiate database"
    connection = sqlite3.connect('../data/tvBot.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""INSERT INTO users VALUES
            (:key,
            :username,
            :email,
            :api_key,
            :api_secret,
            :trendfollower,
            :twopercent,
            :gridtrader
            )
            """, {
        'key': user_id,
        'username': name,
        'email': email_address,
        'api_key': API_ID,
        'api_secret': API_KEY,
        'trendfollower': trendfollower,
        'twopercent': twopercent,
        'gridtrader': gridtrader
    })
    connection.commit()
    cursor.close()


def find_user_info():
    connection = sqlite3.connect('../data/tvBot.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(""" SELECT * FROM users WHERE username ='chris'""")
    traders = dict(result=[dict(r) for r in cursor.fetchall()])
    return traders['result']

if __name__ == '__main__':
    add_new_user()