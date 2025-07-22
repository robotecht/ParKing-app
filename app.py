from flask import Flask, render_template, request, redirect, url_for, flash, session
from controllers.database import db, print_tables, User


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
            return render_template('signup.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('signup.html')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
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
        # If login successful (expand as needed for sessions etc):
        session['user_id'] = user.id
        flash('Logged in successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('login.html')

# Main entry (not needed for flask run, but keeps python app.py workable)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created [via __main__].")
        print_tables(app)
    app.run()