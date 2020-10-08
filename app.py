import json
import os
import sqlite3

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
import sys
sys.path.insert(1, r'C:\Users\Trung\Documents\GitHub\amongUSTH\login')
import login.Db as logDb
import login.User as logUsr

# Configuration
GOOGLE_CLIENT_ID='754525070220-c2lfse3erd1rk52lvas6orr9im9ojkp3.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='7TMNNst1I5ueVjacoQDa1sJg'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


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
        name = user.getName()
        email = user.getEmail()

        return render_template("myprofile.html", name = name, email=email)
    else:
        return render_template("login.html")


@app.route("/login", methods = ["POST"])
def login():
    # Find out what URL to hit for Google login
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
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    
    from db.db import user as udb

    global user
    user = logUsr.user(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )
    # Doesn't exist? Add to database
    if not user.get(unique_id):
        user.create(unique_id, users_name, users_email, picture)
    
    udb.login(users_name, users_email)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout", methods = ["GET","POST"])
@login_required
def logout():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        logout_user()
        return redirect(url_for("index"))
    else:
        print('error logout')


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/')
@app.route('/homepage')
def homepage():
   return render_template("homepage.html")

@app.route('/all_discussion')
def all_discussion():
   return render_template("all_discussion.html")



if __name__ == '__main__':
   app.run(debug=True, ssl_context="adhoc")

