function pronounce(){
    let word = window.location.pathname.substring(1);
    let pronunciaton = new Audio(`https://media.merriam-webster.com/audio/prons/es/me/mp3/s/${word}01sp.mp3`);
    pronunciaton.play();
}



