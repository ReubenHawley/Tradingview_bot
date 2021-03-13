from py.TV_bot import db
from py.TV_bot.models import User


def delete_user(id_number: int):
    User.query.filter_by(id=id_number).delete()


def add_new_user(name, email, api_key, api_secret,
                 trendfollower, twopercent, gridtrader):

    user = User(
        username=name,
        email=email,
        api_key=api_key,
        api_secret=api_secret,
        trending=trendfollower,
        twopercent=twopercent,
        gridtrader=gridtrader)
    db.session.add(user)
    db.session.commit()


def find_users_info(*args, **kwargs):
    accounts = User.query.filter_by(kwargs).all()
    return accounts


if __name__ == '__main__':
   accounts = User.query.filter_by(username='chris').all()
   for account in accounts:
       print(account.username, account.api_key,account.api_secret,account.twopercent)
