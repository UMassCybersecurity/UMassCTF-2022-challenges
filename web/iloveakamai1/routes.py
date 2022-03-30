import hmac
from click import option
from flask import Flask, render_template,make_response,redirect,url_for,jsonify
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, jwt_required
from flask_jwt_extended import JWTManager


app = Flask(__name__)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "is-this-secret-enough" 
app.config["JWT_TOKEN_LOCATION"]=['cookies']
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

@app.route("/login", methods=["GET"])
def login():
    username = 'anonymous'
    access_token = create_access_token(identity=username)
    resp = make_response(render_template('login.html',username=username))
    set_access_cookies(resp, access_token)
    return resp, 200

@app.route("/35d8d35f35f867ad95bceb5f391bf5626ee218e23bbb7c6dc4022a7bc6e67b24/sign-hmac")
def sign():
    #hmac.new("is-this-secret-enough",)
    return 'in dev'
@app.route("/flag", methods=["GET"])
@jwt_required(optional=True)
def protected():
    current_identity = get_jwt_identity()
    print(current_identity)
    if current_identity == 'admin':
        indexmd = open(f"/md/flag", "r").read()
        resp = make_response(render_template('blank.html', data=indexmd))
        return resp, 200
    elif current_identity == 'anonymous':
        data = 'No No No!!! - This is super-secret'
        resp = make_response(render_template('blank.html', data=data))
        return resp, 404
    else:
        return redirect('/login')

@app.route('/')
@jwt_required(optional=True)
def index():
    return 'in dev'
