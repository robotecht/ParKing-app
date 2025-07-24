from flask import Flask, render_template, request, redirect, url_for, flash, session
from controllers.database import db, print_tables, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SECRET_KEY'] = 'S8tEnpx6ifheXAstgiWRFB3X7O4BZq9iR3uJb0RdoCFBsMpgjWE3KyUGBEG8FJ4Q'

# Initialize the database
db.init_app(app)

# Ensure tables are created BEFORE handling the first request
with app.app_context():
    db.create_all()
    print("Database tables created.")
    # Show the table names in the terminal
    print_tables(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(username) == 0 or len(password) < 6:
            flash('Please fill all fields correctly.', 'danger')
            return render_template('new_user.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('new_user.html')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        print(f"New user added to the database: username='{username}', password='{password}'") # Debugging entry
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('new_user.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or user.password != password:
            flash('Incorrect username or password.', 'danger')
            return render_template('login.html')
        # Login successful; save user session and redirect to dashboard
        session['user_id'] = user.id
        flash('Logged in successfully!', 'success')
        return redirect(url_for('user_dashboard'))  # <-- redirect to dashboard
    return render_template('login.html')


@app.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    # Import your models properly
    lots = ParkingLot.query.all()  # Fetch parking lots from db
    user = User.query.get(user_id)
    return render_template('user_dashboard.html', user=user, lots=lots)



@app.route('/book_lot/<int:lot_id>', methods=['GET'])
def book_lot(lot_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to book a spot.', 'danger')
        return redirect(url_for('login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    # Find the first available spot in the lot, ordered by spot_number or id
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.id).first()

    if not spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for('user_dashboard'))

    # Redirect to booking page for that spot
    return redirect(url_for('book_spot', spot_id=spot.id))

@app.route('/book_spot/<int:spot_id>', methods=['GET', 'POST'])
def book_spot(spot_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to book a spot.", "danger")
        return redirect(url_for('login'))

    spot = ParkingSpot.query.get_or_404(spot_id)
    lot = ParkingLot.query.get_or_404(spot.lot_id)

    if request.method == 'POST':
        if spot.status != 'A':
            flash("This spot is no longer available.", "danger")
            return redirect(url_for('user_dashboard'))

        # Create reservation with a default booking period (e.g., 1 hour)
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)
        cost = lot.prices

        reservation = Reservation(
            user_id=user_id,
            spot_id=spot.id,
            start_time=start_time,
            end_time=end_time,
            cost=cost
        )
        spot.status = 'O'  # mark spot occupied

        db.session.add(reservation)
        db.session.commit()

        flash("Spot booked successfully!", "success")
        return redirect(url_for('user_dashboard'))

    # GET request: show booking confirmation page
    return render_template('booking.html', spot=spot, lot=lot)




# Main entry (not needed for flask run, but keeps python app.py workable)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created [via __main__].")
        print_tables(app)
    app.run()