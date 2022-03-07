var ihaterit = document.getElementById("welcome").getAttribute("data-ihaterit");
function say_something(words)
{
    console.log('alert('+words+')')
    setTimeout('alert('+words+')',500)
}
document.addEventListener("DOMContentLoaded", function() {
    say_something(ihaterit)
});