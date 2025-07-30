# db.update.py
# This script populates the database with initial parking lot and spot data.
# It creates 3 parking lots, each with 10 parking spots.
from app import app
from controllers.database import db, ParkingLot, ParkingSpot

with app.app_context():
    for i in range(1, 4):
        lot = ParkingLot(
            location=f"Sector-{i*5}, CityCenter",
            prices=30.0 * i,
            address=f"{100+i} Main Avenue, City",
            pincode=f"1100{i}",
            max_spots=10
        )
        db.session.add(lot)
        db.session.flush()  # Assigns lot.id for ParkingSpot foreign key reference

        for s in range(1, 11):
            spot = ParkingSpot(
                lot_id=lot.id,        # Correct: use lot.id, not lot.lot_id
                spot_number=s,        # Assign spot number per spot (1-10)
                status='A'            # Available by default
            )
            db.session.add(spot)

    db.session.commit()
    print("3 parking lots (with 10 spots each) created.")
