from flask import Flask, make_response, render_template, request
from bot import bot
from threading import Thread

app = Flask(__name__)

def check_for_cookie():
    if(request.cookies.get("admin")):
        return True
    return False
@app.route("/", methods = ['GET'])
def get_main():
    response = make_response(render_template('index.html'))
    if(check_for_cookie()==False):
        response.set_cookie("auth","-1",secure=True,samesite=None)
    return response

@app.route("/register",methods = ['GET','POST'])
def get_register():
    if(request.method=='GET'):
        response = make_response(render_template('register.html'))
        if(check_for_cookie()==False):
            response.set_cookie("auth","-1",secure=True,samesite=None)
        return response
    elif(request.method=='POST'): 
        data = request.form.to_dict()
        thread = Thread(target=bot.checkEssay,kwargs={'data':data})
        thread.start()
        return "We got your request and will read it shortly!",200

@app.route("/review/essay",methods = ['GET','POST'])
def reviewEssay():
    essay = {"email":request.args.get("name"),"essay":request.args.get("essay")}
    if(request.remote_addr != '127.0.0.1'):
        return "Sorry pal you\'re not admin"
    try:
        return render_template('essay_checker.html', essay = essay)
    except:
        return 'no essays to read',200



@app.route("/join",methods = ['GET'])
def get_play():
    if(request.cookies.get("auth")=="UMASS{N4MB3R_0N3_1N_$TUD3NT_D1N1NG_DVMA216537}"):
        return "Welcome!",200
    return "You're not allowed here!",403