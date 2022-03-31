import base64
import hmac
import hashlib
from flask import Flask, render_template,make_response,redirect, request
from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, jwt_required
from flask_jwt_extended import JWTManager
from importlib_metadata import method_cache

flag = "UMASS{TH1S_1S_3XTR3M3LY_$UP3R_$3CR3T!}"
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
    print(message)
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
    print(current_identity)
    if current_identity == 'admin':
        return flag
    elif current_identity == 'anonymous':
        data = 'No No No!!! - This is super-secret'
        resp = make_response(render_template('blank.html', data=data))
        return resp, 200
    else:
        return redirect('/login')

@app.route('/')
@jwt_required(optional=True)
def index():
    return 'in dev'
