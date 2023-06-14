

function showOverlay(){
    element('overlay').style.display = 'flex';
}

function closeOverlay() {

    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
    overlay.innerHTML = '';

}

function sendWebhook(){

    const field= element('discord-webhook');

    if(field.value){

        const jsonContent = {
            webhook_url: field.value
        }

        field.value = '';

        const request = new XMLHttpRequest();

        request.onload = function() {

            const jsonResponse = JSON.parse(this.responseText);

            if(jsonResponse.result === true){
                refresh();
            }

            showNotification(jsonResponse.result, jsonResponse.status);

        }

        request.open("POST", "/update-webhook");
        request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        request.send(JSON.stringify(jsonContent));

    }

}

function refresh(){

    const deviceInfo = element('info-devices');
    const eventsInfo = element('info-events');
    const webhookStatus = element('webhook-status');

    deviceInfo.innerText = `Identified devices: ${cached_devices.length}`;
    eventsInfo.innerText = `Registered events: ${cached_events.length}`;

    const request = new XMLHttpRequest();

    request.onload = function() {

        const jsonResponse = JSON.parse(this.responseText);

        if(jsonResponse.result === true){
            webhookStatus.innerText = 'Webhook status: Online'
        }
        else{
            webhookStatus.innerText = 'Webhook status: Offline'
        }

    }

    request.open("GET", "/webhook-status");
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