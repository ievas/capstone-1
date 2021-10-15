function pronounce(){
    let word = window.location.pathname.substring(1);
    let pronunciaton = new Audio(`https://media.merriam-webster.com/audio/prons/es/me/mp3/s/${word}01sp.mp3`);
    pronunciaton.play();
}


function toggleDiv(id){
    let div = document.getElementById(id);
    div.style.visibility = div.style.visibility == "visible" ? "hidden" : "visible";
}

let form = $('#translate-form');
let textarea = document.querySelector("textarea");


let checkButton = document.getElementById("check");

if(checkButton){
    checkButton.addEventListener("click", function(e){
        e.preventDefault();
        form.submit();
    })
}





