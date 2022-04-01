import base64
import hmac
import hashlib
from flask import Flask, render_template,make_response,redirect, request
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, jwt_required
from flask_jwt_extended import JWTManager

flag = "UMASS{W0W_TH1$_1$_4_C00L_FL4G_BRUH!_69420}"
app = Flask(__name__)
#JWT STUFF
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

@app.route("/api/sign-hmac",methods=["POST"])
def sign():
    message = bytes(request.form['message'],'utf-8')
    signature = base64.b64encode(hmac.new(
        bytes("is-this-secret-enough",'utf-8'),
        msg=message,
        digestmod=hashlib.sha256
    ).digest())
    return signature

@app.route("/flag", methods=["GET"])
@jwt_required(optional=True)
def protected():
    current_identity = get_jwt_identity()
    if current_identity == 'admin':
        return flag
    elif current_identity == 'anonymous':
        data = "<img src='/static/images/anonuserflag'>"
        resp = make_response(render_template('flag.html', flag=data))
        return resp, 200
    else:
        return redirect('/login')

@app.route('/')
def index():
    resp = make_response(render_template('welcome.html'))
    return resp, 200