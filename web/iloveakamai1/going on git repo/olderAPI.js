secret = 'super-secret'
function base64url(source) {
  encodedSource = btoa(source);
  while(encodedSource.endsWith('='))
  {
    encodedSource = encodedSource.substring(0,encodedSource.length-1)
	}
  return encodedSource;
}
header=`{"typ":"JWT","alg":"HS256"}`
data = `{"fresh":false,"iat":1648660807,"jti":"70c86b4e-b9c9-423e-b210-e9c67364b1ae","type":"access","sub":"anonymous","nbf":1648660807,"exp":1648661707}`
unsignedToken = base64url(header) + "." + base64url(data)
console.log(unsignedToken)
var hash = Crypto.HmacSHA256("Message", "Secret Passphrase");
console.log(hash)
JWT = unsignedToken + "." + base64url(Crypto.HMACSHA256(unsignedToken, secret))
console.log(JWT)