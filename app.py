from flask import Flask
from controllers.database import db, print_tables


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SECRET_KEY'] = 'S8tEnpx6ifheXAstgiWRFB3X7O4BZq9iR3uJb0RdoCFBsMpgjWE3KyUGBEG8FJ4Q'

# Initialize the database
db.init_app(app)

# Ensure tables are created BEFORE handling the first request
@app.before_request
def setup():
    db.create_all()
    print("Database tables created.")
    # Show the table names in the terminal
    print_tables(app)

# Main entry (not needed for flask run, but keeps python app.py workable)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created [via __main__].")
        print_tables(app)
    app.run()