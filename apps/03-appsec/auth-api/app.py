# flask imports
import os

from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid  # for public id
from werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps

# creates Flask object
from werkzeug.utils import redirect

app = Flask(__name__)
# configuration
# NEVER HARDCODE CONFIGURATION IN CODE
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['REDIRECT_HOST'] = os.environ['REDIRECT_HOST']

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", 3306)
DB_DATABASE = os.environ["DB_DATABASE"]
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
connection = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
)

app.config["SQLALCHEMY_DATABASE_URI"] = connection
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)


# Database ORMs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(255))


db.create_all()


# Default home route
@app.route('/', methods=['GET'])
def home():
    return render_template(
        'index.html',
        context={
           'redirect_host': app.config['REDIRECT_HOST'],
        }
    )


# route for logging user in
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    # creates dictionary of form data
    auth = request.form

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query \
        .filter_by(email=auth.get('email')) \
        .first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        redir_url = f'{app.config["REDIRECT_HOST"]}/?token={token}'
        return redirect(redir_url)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


# signup route
@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # checking for existing user
    user = User.query.filter_by(email=email).first()
    if not user:
        # database ORM object
        user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            role='user',
            email=email,
            password=generate_password_hash(password)
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        # return make_response('Successfully signed up.', 201)
        return render_template('signup_success.html')
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)


if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(host='0.0.0.0', port=8080, debug=True)