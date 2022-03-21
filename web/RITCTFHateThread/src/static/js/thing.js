var iloveumass = document.getElementById("welcome").getAttribute("data-iloveumass");
function say_something(words)
{
    setTimeout(`console.log('${words}')`,500)
}
document.addEventListener("DOMContentLoaded", function() {
    say_something(iloveumass)
});