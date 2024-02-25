import json

from flask import Flask, render_template, request, redirect, url_for, make_response
from requests_oauthlib import OAuth2Session
import os

try:
    import secrets_1
except ImportError as e:
    pass

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/github/login")
def github_login():
    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID")) # pripravimo Github OAuth sejo
    authorization_url, state = github.authorization_url("https://github.com/login/oauth/authorize") # url githubove avtorizacije

    response = make_response(redirect(authorization_url)) # preusmerimo uporabnika do githubove avtorizacije
    response.set_cookie("oauth_state", state, httponly=True) # za zascito

    return response


@app.route("/github/callback")
def github_callback():
    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"), state=request.cookies.get("oauth_state"))
    token = github.fetch_token("https://github.com/login/oauth/access_token", client_secret=os.environ.get("GITHUB_CLIENT_SECRET"), authorization_response=request.url)

    response = make_response(redirect(url_for('profile'))) # preusimeri na stran profila
    response.set_cookie("oauth_token", json.dumps(token), httponly=True)

    return response


@app.route("/profile")
def profile():
    github = OAuth2Session(os.environ.get("GITHUB_CLIENT_ID"), token=json.loads(request.cookies.get("oauth_token")))
    github_profile_data = github.get('https://api.github.com/user').json()

    return render_template("profile.html", github_profile_data=github_profile_data)


@app.route("/github/logout")
def logout():
    response = make_response(redirect(url_for('index'))) # preusmeri te na index stran 
    response.set_cookie("oauth_token", expires=0) # izbrise piskotek za izpis

    return response


if __name__ == '__main__':
    app.run(use_reloader=True)
