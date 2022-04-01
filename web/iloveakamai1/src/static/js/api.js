//AUTOFLAG API V.2 : AUTOMATICALLY AUTHENTICATE USERS THEN REDIRECT TO FLAG
//Users should no longer be able to change their user identify from 'anonymous' to 'admin'
//WE DEPLOYED A PATCH! OUR API HAS BEEN MOVED TO SERVER-SIDE! SEE OUR GIT -> 
document.getElementById('redir').innerText = 'Redirecting you to your flag shortly'
setTimeout(()=>{
    window.location.replace("/flag");
},2000)
