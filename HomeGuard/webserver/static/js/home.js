

function showOverlay(){
    element('overlay').style.display = 'flex';
}

function closeOverlay() {

    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
    overlay.innerHTML = '';

}

function fetchAndShowAddView(){

    const request = new XMLHttpRequest();

    request.onload = function() {

        const overlay = element('overlay');

        overlay.innerHTML = this.responseText;

        onAddViewLoaded();
        showOverlay();

    }

    request.open("FETCH", "/add-event-view");
    request.send();

}

window.addEventListener("load", (event) => {

    const overlay = document.getElementById('overlay');

    overlay.addEventListener('click', function(e) {

        if(e.target === overlay){
            overlay.innerHTML = '';
            overlay.style.display = 'none';
        }

    });

});