from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

db = SQLAlchemy()

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

class ParkingLot(db.Model):
    #Parking lot: It’s the physical space where the collection of parking spots are available for an area
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120), nullable=False)
    prices = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True)

class ParkingSpot(db.Model):
    #Parking spot: The physical space for parking a 4-wheeler parking.
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A = available, O = occupied
    booking = db.relationship('Booking', backref='parking_spot', lazy=True)

class Reservation(db.Model):
    #Reserve parking spot: Allocates parking spot as per the user requests
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Float, nullable=False)

def print_tables(app):
    """Print the list of tables in the connected SQLite database."""
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"Table created: {table}")