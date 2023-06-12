function element(id){
    return document.getElementById(id);
}

function cssVariable(name){
    return getComputedStyle(document.documentElement).getPropertyValue(name);
}


let cached_devices = []
const dayButtons = document.querySelectorAll('.day');

function retrieveDevices(){

    const request = new XMLHttpRequest();

    request.onload = function() {

        cached_devices = JSON.parse(this.responseText)

        for(let i = 0; i < cached_devices.length; ++i){

            let select = element('device-select');

            let option = select.appendChild(document.createElement('option'))
            let device = cached_devices[i];

            option.textContent = `${device.display_name} (${device.mac_address})`

        }

    }

    request.open("GET", "/devices");
    request.send();

}

dayButtons.forEach(function(day, index){

    day.addEventListener("click", function(){

        if(day.classList.contains('day-selected')){
            day.classList.remove('day-selected');
        }
        else{
            day.classList.add('day-selected');
        }

    });

});


retrieveDevices()