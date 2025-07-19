from datetime import datetime

class Admin(db.Model):
    #Admin - root access - It is the superuser of the app and requires no registration
    id = db.Column(db.Integer, primary_key=True, default=1)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class User(db.Model):
    #User - Can reserve a parking space
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    booking = db.relationship('Booking', backref='user', lazy=True)