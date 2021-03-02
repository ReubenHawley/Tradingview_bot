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


def find_users_info(**kwargs):
    accounts = User.query.filter_by(kwargs).all()
    return accounts


if __name__ == '__main__':
    users = User.query.all()
    for value in users:
        print(value.id,value.username,value.email,value.api_key,value.api_secret,value.trending,value.twopercent,value.gridtrader )
