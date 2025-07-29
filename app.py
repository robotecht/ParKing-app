from flask import Flask, render_template, request, redirect, url_for, flash, session
from controllers.database import db, print_tables, User, ParkingLot, ParkingSpot, Reservation, Admin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from math import ceil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SECRET_KEY'] = 'S8tEnpx6ifheXAstgiWRFB3X7O4BZq9iR3uJb0RdoCFBsMpgjWE3KyUGBEG8FJ4Q'
app.config['DEBUG'] = True

# Initialize the database
db.init_app(app)

# Ensure tables are created BEFORE handling the first request
with app.app_context():
    db.create_all()
    print("Database tables created.")
    # Show the table names in the terminal
    print_tables(app)

    # Check if admin exists
    admin = Admin.query.filter_by(username='iitm').first()
    if not admin:
        admin = Admin(
            username='iitm',
            password=generate_password_hash('iitm123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if not admin or not check_password_hash(admin.password, password):
            flash('Invalid username or password.', 'danger')
            return render_template('admin_login.html')

        session.clear()
        session['admin_id'] = admin.id
        flash('Logged in successfully as admin!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash("Admin logged out.", "success")
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Please log in as admin to access dashboard.", "danger")
        return redirect(url_for('admin_login'))

    # Example: Get all parking lots
    parking_lots = ParkingLot.query.all()
    users = User.query.all()

    # Render admin dashboard template (you need to create it)
    return render_template('admin_dashboard.html', lots=parking_lots, users=users)

@app.route('/admin/lot/<int:lot_id>/edit', methods=['GET', 'POST'])
def admin_edit_lot(lot_id):
    # Ensure admin is logged in (check session)
    if 'admin_id' not in session:
        flash('Please login as admin.', 'danger')
        return redirect(url_for('admin_login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        # Process form data to update the lot
        lot.location = request.form.get('location', lot.location)
        lot.address = request.form.get('address', lot.address)
        lot.pincode = request.form.get('pincode', lot.pincode)
        lot.prices = float(request.form.get('prices', lot.prices))
        new_max_spots = int(request.form.get('max_spots', lot.max_spots))

        # Synchronize ParkingSpot entries with new max_spots
        current_spots_count = len(lot.spots)

        if new_max_spots > current_spots_count:
            # Add new spots
            for spot_num in range(current_spots_count + 1, new_max_spots + 1):
                new_spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=spot_num,
                    status='A'  # Available by default
                )
                db.session.add(new_spot)

        elif new_max_spots < current_spots_count:
            # Remove extra spots if possible (not occupied)
            spots_to_remove = [spot for spot in lot.spots if spot.spot_number > new_max_spots]
            for spot in spots_to_remove:
                if spot.status == 'O':  # Occupied
                    flash(f"Cannot remove spot #{spot.spot_number} because it is currently occupied.", "danger")
                    return redirect(url_for('admin_edit_lot', lot_id=lot.id))
                else:
                    db.session.delete(spot)

        lot.max_spots = new_max_spots

        db.session.commit()
        flash("Parking lot updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    # For GET request, render edit form with existing lot data
    return render_template('admin_edit_lot.html', lot=lot)

@app.route('/admin/lot/<int:lot_id>/delete', methods=['POST'])
def admin_delete_lot(lot_id):
    if 'admin_id' not in session:
        flash("Please log in as admin.", "danger")
        return redirect(url_for('admin_login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    # Only allow delete if no spots are occupied
    occupied_spots = [spot for spot in lot.spots if spot.status == 'O']
    if occupied_spots:
        flash("Cannot delete this lot because some spots are occupied.", "danger")
        return redirect(url_for('admin_dashboard'))

    # Delete spots first (optional if cascade delete is not configured)
    for spot in lot.spots:
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    flash(f"Parking lot '{lot.location}' has been deleted.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/lot/add', methods=['GET', 'POST'])
def admin_add_lot():
    if 'admin_id' not in session:
        flash('Please log in as admin.', 'danger')
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        location = request.form['location']
        address = request.form['address']
        pincode = request.form['pincode']
        prices = float(request.form['prices'])
        max_spots = int(request.form['max_spots'])
        lot = ParkingLot(location=location, address=address, pincode=pincode, prices=prices, max_spots=max_spots)
        db.session.add(lot)
        db.session.commit()
        # Create parking spots for the new lot
        for spot_num in range(1, max_spots + 1):
            spot = ParkingSpot(lot_id=lot.id, spot_number=spot_num, status='A')
            db.session.add(spot)
        db.session.commit()
        flash("New parking lot added.", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add_lot.html')




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


from datetime import datetime

@app.route('/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view the dashboard.", "danger")
        return redirect(url_for("login"))

    user = User.query.get(user_id)
    lots = ParkingLot.query.all()

      # Fetch all bookings for the user ordered by start_time descending
    bookings = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.start_time.desc()).all()
    # Prepare data with calculated duration and cost per booking for user
    bookings_data = []
    now = datetime.utcnow()
    for booking in bookings:
        start = booking.start_time
        end = booking.end_time or now  # If booking still active, calculate till now
        duration_seconds = (end - start).total_seconds()
        duration_hours = max(1, ceil(duration_seconds / 3600))  # Minimum 1 hour charge
        total_cost = duration_hours * booking.cost  # Assuming booking.cost is hourly rate

        bookings_data.append({
            'booking': booking,
            'duration_hours': duration_hours,
            'total_cost': total_cost,
        })

    return render_template(
        "user_dashboard.html",
        user=user,
        lots=lots,
        bookings=bookings_data,  # pass the prepared data list
        now=now
    )


@app.route('/logout')
def logout():
    session.clear()  # remove all session data — logs out the user
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))  # redirect to login or home page



@app.route('/finish_parking/<int:booking_id>', methods=['POST'])
def finish_parking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to finish your parking.", "danger")
        return redirect(url_for("login"))

    booking = Reservation.query.get_or_404(booking_id)

    # Check booking ownership:
    if booking.user_id != user_id or booking.end_time is not None:
        flash("Invalid action.", "danger")
        return redirect(url_for("user_dashboard"))

    # Update booking end time to now:
    booking.end_time = datetime.utcnow()

    # Set spot to available:
    spot = ParkingSpot.query.get(booking.spot_id)
    spot.status = 'A'

    db.session.commit()

    flash("Your parking session has been finished and spot is released.", "success")
    return redirect(url_for("user_dashboard"))




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
        # end_time = start_time + timedelta(hours=1)
        cost = lot.prices

        reservation = Reservation(
            user_id=user_id,
            spot_id=spot.id,
            start_time=start_time,
            end_time=None,
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