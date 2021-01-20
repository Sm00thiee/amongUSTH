import json
import os
from re import template
import sqlite3
from datetime import timedelta


# Third party libraries
from flask import Flask, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
import login.Db as logDb
import login.User as logUsr
from login.mongo import User as mongoUsr
from login.mongo import Book as mongoBook
from flask_bcrypt import Bcrypt
from forms.forms import Password,BookPost
# Configuration
GOOGLE_CLIENT_ID = '754525070220-c2lfse3erd1rk52lvas6orr9im9ojkp3.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '7TMNNst1I5ueVjacoQDa1sJg'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)

@login_manager.unauthorized_handler
def unauthorized():
    return render_template("login.html", display_navbar="none")


# Naive database setup
try:
    logDb.init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return logUsr.user.get(user_id)


@app.route("/index")
def index():
    if current_user.is_authenticated:
        form = Password()
        id_ = user.get_id()
        name = mongoUsr.get_name(id_)
        email = mongoUsr.get_email(id_)
        profile_pic = mongoUsr.get_profile_pic(id_)
        first_Name = name.split(' ', 1)[0]
        print("Logged in")
        return render_template('profile.html', name=first_Name, email=email, picture=profile_pic, display_navbar="inline")

    else:
        print("Not logged in")
        return render_template("login.html", text="Login", display_noti="none", display_navbar="none", name="SIGN UP NOW!")


def generate_password():
    form = Password()
    hashed_password = str(bcrypt.generate_password_hash("123456").decode('utf-8'))[:8]
    id_ = user.get_id()
    email = mongoUsr.get_email(id_)
    username = email.split(".")[1].split("@")[0]
    profile_pic = mongoUsr.get_profile_pic(id_)
    mongoUsr.add_login_info(id_, username, hashed_password)

    print(hashed_password)
from flask_login import login_user
@app.route("/login", methods = ['GET', 'POST'])
def login():
    #Find out what URL to hit for Google login
    if request.method=="POST" :
        username = request.form["username"]
        password = request.form["password"]
        user = mongoUsr.login(username, password)
        if user:
            # @login_manager.user_loader  
            # login_user(user)
            return redirect(url_for("index"))
        else:
            print("login failed")

    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google

    global user
    user = logUsr.user(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )
    # Doesn't exist? Add to database
    if not user.get(unique_id):
        user.create(unique_id, users_name, users_email, picture)

    if "@st.usth.edu.vn" in users_email:
        # Begin user session by logging the user in
        login_user(user)

        # Create session timeout
        time = timedelta(minutes=60)
        # User will automagically kicked from session after 'time'
        app.permanent_session_lifetime = time

        # Add user information to Online database
        id_ = user.get_id()
        name = user.getName()
        email = user.getEmail()
        profile_pic = user.getprofile_pic()
        mongoUsr.register(id_, name, email, profile_pic)

        generate_password()
        return redirect(url_for('index'))       

    else:
        logout_user()
        return redirect(url_for('loginfail'))

@app.route('/loginfail')
def loginfail():
    return render_template('login.html', text="LOGIN FAILED :(", display_navbar="none", display_noti="block", loginNotiText="Login failed! The email address that you used is not a valid USTH Email")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route('/')
@app.route('/homepage')
def homepage():
    if current_user.is_authenticated:
        profile_pic = user.getprofile_pic()
        name = user.getName()
        first_Name = name.split(' ', 1)[0]
        return render_template("homepage.html", display_navbar="inline", picture=profile_pic, name=first_Name)

    else:
        return render_template("homepage.html", display_navbar="none", name='SIGN UP NOW!')


@app.route('/browse')
def browse():
    if current_user.is_authenticated:
        name = user.getName()
        profile_pic = user.getprofile_pic()
        first_Name = name.split(' ', 1)[0]

        return render_template("browse.html", display_navbar="inline", name=first_Name, picture=profile_pic)
    else:
        return render_template('login.html', text="You need to login!")


@app.route('/admin')
def admin():
    return render_template("admin.html", display_navbar="none", name="ADMIN")


@app.route('/content')
def content():
    if current_user.is_authenticated:
        name = user.getName()
        profile_pic = user.getprofile_pic()
        first_Name = name.split(' ', 1)[0]

        return render_template("content.html", display_navbar="inline", name=first_Name, picture=profile_pic)
    else:
        return render_template('login.html', text="You need to login!")

@app.route('/book',methods=['GET','POST'])
def new_book():
    form = BookPost()
    if form.validate_on_submit():
        # book = Book(file_name=form.file_name.data,description=form.description.data,
        #     file=form.file.data,author=current_user)
        try:
           mongoBook.post_book(form.file_name.data,form.file.data,form.description.data)
        except:
           print("insert failed")
        return render_template('homepage.html',title='Created Post')
    return render_template('homepage.html',title='BookPost',form=form)

if __name__ == '__main__':
    app.run(debug=True, ssl_context="adhoc")
