from flask import Flask, send_from_directory, request
from werkzeug.utils import redirect
from sussy import integrate
app = Flask(__name__)

@app.route("/", methods = ['GET'])
def index():
    return send_from_directory("../static","index.html")

@app.route("/submit", methods = ['GET','POST'])
def submit():
    return redirect("/venting",code=307)

@app.route("/venting",methods = ['GET','POST'])
def sus():
    data = request.form.to_dict(flat=False)
    urlParams = "?lname={lname}&fname={fname}&comment={comment}&admin={mod}".format(fname=data['fname'][0],lname=data['lname'][0],comment=data['comment'][0],mod=False)
    return send_from_directory("../static","redir.html"),302,{"Location":"/inthevents"+urlParams}

@app.route("/inthevents",methods= ['GET','POST'])
def venting():
    if(request.args.get("admin") == 'True'):
        return redirect("/fff5bf676ba8796f0c51033403b35311/success",code=307)
    else:
        return redirect("/submitted",code=307)

@app.route("/submitted",methods = ['GET'])
def submitted():
    return send_from_directory("../static","commentsubmitted.html")

@app.route("/fff5bf676ba8796f0c51033403b35311/success",methods=['GET'])
def success():
    return  send_from_directory("../static","success.html")

@app.route("/fff5bf676ba8796f0c51033403b35311/login", methods = ['POST'])
def login():
    return integrate.validate(request.form.get("user"),request.form.get("pass"))

if __name__ == "__main__":
    app.run(host='0.0.0.0')

