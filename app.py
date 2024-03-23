from flask import Flask, flash, request, jsonify, render_template,redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import UserMixin, login_manager, login_user, logout_user, login_manager, LoginManager, login_required, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/tf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = '7867'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# For loading and retrieving users
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Define the database models
class Users(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)

class Turfs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    turf_id = db.Column(db.Integer, db.ForeignKey('turfs.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'turf_id': self.turf_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
    

@app.route('/')
def index():
    return render_template('index.html')

# Add this route for the dashboard after successful login
# @app.route('/dashboard')
# def dashboard():
#     user_id = session.get('user_id')
#     if user_id:
#         user = Users.query.get(user_id)
#         return render_template('dashboard.html', user=user)
#     else:
#         return redirect(url_for('login'))


@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    print(data['password'])
    encpassword = generate_password_hash(data['password'])
    new_user = Users(username=data['username'], email=data['email'], password=encpassword)
    print(encpassword)
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Username or email already exists'}), 400

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        print(username)
        password = request.form.get('password')
        print(password)
        user = Users.query.filter_by(username=username).first()
        print(user)
        if user and check_password_hash(generate_password_hash(user.password),password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials", "danger")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/turfs', methods=['POST'])
def create_turf():
    data = request.json
    new_turf = Turfs(name=data['name'], location=data['location'], capacity=data['capacity'])
    db.session.add(new_turf)
    db.session.commit()
    return jsonify({'message': 'Turf created successfully'}), 201

@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    new_booking = Bookings(user_id=data['user_id'], start_time=datetime.fromisoformat(data['start_time']), end_time=datetime.fromisoformat(data['end_time']))
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Booking created successfully'}), 201


@app.route('/locations', methods=['GET'])
def get_locations():
    locations_name = [turf.name for turf in Turfs.query.distinct(Turfs.name)]
    return jsonify(locations_name)

@app.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = Bookings.query.all()
    return jsonify([booking.to_json() for booking in bookings]), 200

@app.route('/gallery')
def serve_gallery():
    return render_template('gallery.html')



# @app.route('/login', methods=['GET'])
# def serve_login():
#     return render_template('login.html')




if __name__ == '__main__':
    app.run(debug=True)
