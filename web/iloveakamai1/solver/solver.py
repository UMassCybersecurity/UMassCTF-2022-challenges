import requests as r
val = input("Enter your unsigned token\n")
payload = {"message":val}
r1 = r.post('http://127.0.0.1:8000/api/sign-hmac',data=payload)

print(r1.text)



