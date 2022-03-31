function base64url(source) {
  encodedSource = btoa(source);
  while (encodedSource.endsWith('=')) {
    encodedSource = encodedSource.substring(0, encodedSource.length - 1)
  }
  encodedSource = encodeURI(encodedSource)
  console.log(encodedSource)
  return encodedSource;
}
function getSignedHMAC(unsignedToken) {
  return new Promise((resolve, reject) => {
    var xhr = new XMLHttpRequest()
    xhr.open("POST", '/api/sign-hmac', true)

    //Send the proper header information along with the request
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")

    xhr.onreadystatechange = function () { // Call a function when the state changes.
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        console.log(xhr.responseText)
        return xhr.responseText
      }
    }
    xhr.send(`message=${unsignedToken}`)
  })


}
async function signToken() {
  header = `{"typ":"JWT","alg":"HS256"}`
  data = `{"fresh":false,"iat":1648660807,"jti":"70c86b4e-b9c9-423e-b210-e9c67364b1ae","type":"access","sub":"anonymous","nbf":1648660807,"exp":1648661707}`
  unsignedToken = base64url(header) + "." + base64url(data)
  console.log(unsignedToken)
  let signature = await getSignedHMAC(unsignedToken)
  JWT = unsignedToken + "." + base64url(signature)
  console.log(JWT)
}

signToken()