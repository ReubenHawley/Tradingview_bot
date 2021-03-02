from py.TV_bot import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    api_key = db.Column(db.String(120), unique=True, nullable=False)
    api_secret = db.Column(db.String(120), unique=True,
                           nullable=False) #TODO change string length to 60 when implementing hashing
    trending = db.Column(db.Boolean, unique=False, nullable=False)
    twopercent = db.Column(db.Boolean, unique=False, nullable=False)
    gridtrader = db.Column(db.Boolean, unique=False, nullable=False)
    trades = db.relationship('Trade', backref='account', lazy=True)

    def __repr__(self):
        return f'ID:{self.id} - {self.username}'


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    timestamp = db.Column(db.Integer, unique=False, nullable=False)
    symbol = db.Column(db.String(10), unique=False, nullable=False)
    side = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Float, unique=True, nullable=False)
    amount = db.Column(db.Float, unique=False, nullable=False)
    cost = db.Column(db.Float, unique=False, nullable=False)
    fees = db.Column(db.Float, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'{self.timestamp} - {self.symbol} - {self.side} - {self.amount} - {self.price}'
