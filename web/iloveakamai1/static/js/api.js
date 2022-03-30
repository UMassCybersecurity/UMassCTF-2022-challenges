//Autoflag API patched due to bad clientside code, see repo 
document.getElementById('redir').innerText = 'Redirecting you to your flag shortly'
setTimeout(()=>{
    window.location.replace("/flag");
},2000)
