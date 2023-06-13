
let cached_devices = []
let cached_events = []

function element(id){
    return document.getElementById(id);
}

function deviceById(id){

    for(let i = 0; i < cached_devices.length; ++i){

        if(cached_devices[i].uuid === id){
            return cached_devices[i]
        }

    }

    return null

}

function retrieveEvents(){

    const request = new XMLHttpRequest();

    request.onload = function() {

        let list = JSON.parse(this.responseText)
        let eventContainer = element('event-container')

        eventContainer.innerHTML = ''

        cached_events = list;

        for(let i = 0; i < list.length; ++i){

            let event = list[i];
            let eventInfo = document.createElement('event-info');

            let names = []

            for(var j = 0; j < event.ids.length; ++j){

                let device = deviceById(event.ids[j]);

                if(device != null){
                    names.push(device.display_name);
                }

            }

            eventInfo.setAttribute('class', 'list-div secondary-text');
            eventInfo.setAttribute('name', event.name);
            eventInfo.setAttribute('devices', names.length > 0 ? names.join(', ') : 'None');
            eventInfo.setAttribute('days', event.trigger.weekdays.join(', '));
            eventInfo.setAttribute('start', event.trigger.start_date);
            eventInfo.setAttribute('end', event.trigger.end_date);
            eventInfo.setAttribute('time', `${event.trigger.start_time} - ${event.trigger.end_time}`);
            eventInfo.setAttribute('button', 'Edit');
            eventInfo.setAttribute('onclick', '');

            eventContainer.appendChild(eventInfo);

        }

        const div = eventContainer.appendChild(document.createElement('div'));
        div.setAttribute('class', 'list-div');
        div.setAttribute('style', 'border: 0;');

        const button = div.appendChild(document.createElement('button'));

        button.setAttribute('class', 'button-style');
        button.innerText = 'Add event';
        button.onclick = () => {

            fetchAndShowAddView();

        }

    }

    request.open("GET", "/events");
    request.send();

}

function retrieveDevices(){

    const request = new XMLHttpRequest();

    request.onload = function() {

        cached_devices = JSON.parse(this.responseText)

        let deviceContainer = element('device-container')

        deviceContainer.innerHTML = '';

        for(let i = 0; i < cached_devices.length; ++i){

            let device = cached_devices[i];
            let deviceInfo = document.createElement('device-info');

            deviceInfo.setAttribute('class', 'list-div secondary-text');
            deviceInfo.setAttribute('name', device.display_name);
            deviceInfo.setAttribute('ip', device.ip_addresses[0]);
            deviceInfo.setAttribute('mac', device.mac_address);
            deviceInfo.setAttribute('activity', device.last_activity);
            deviceInfo.setAttribute('button', 'Manage');

            deviceContainer.appendChild(deviceInfo);

        }

        retrieveEvents()

    }

    request.open("GET", "/devices");
    request.send();

}

window.addEventListener("load", (event) => {

    retrieveDevices();

});