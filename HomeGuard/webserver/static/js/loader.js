
let cached_devices = []
let cached_events = []

let selectedDeviceIndex = -1
let selectedDevices = []
let selectedDays = []

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

            for(let j = 0; j < event.ids.length; ++j){

                let device = deviceById(event.ids[j]);

                if(device != null){
                    names.push(device.display_name);
                }

            }

            let devices = 'None';

            if(names.length === 1){
                devices = names[0];
            }
            else if(names.length > 1){
                devices = `${names.length} devices`
            }

            eventInfo.setAttribute('class', 'list-div secondary-text');
            eventInfo.setAttribute('name', event.name);
            eventInfo.setAttribute('devices', devices);
            eventInfo.setAttribute('days', event.trigger.weekdays.join(', '));
            eventInfo.setAttribute('start', event.trigger.start_date);
            eventInfo.setAttribute('end', event.trigger.end_date);
            eventInfo.setAttribute('time', `${event.trigger.start_time} - ${event.trigger.end_time}`);
            eventInfo.setAttribute('button', 'Edit');
            eventInfo.setAttribute('clickEvent', `fetchAndShowEditView("${event.name}")`);

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

        refresh();

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
            deviceInfo.setAttribute('clickEvent', `fetchAndShowDeviceView("${device.uuid}")`);

            deviceContainer.appendChild(deviceInfo);

        }

        retrieveEvents()

    }

    request.open("GET", "/devices");
    request.send();

}

function submitEditEventRequest(oldName) {

    if (!canSubmitEvent()) return;

    const name = element('event-name').value

    const dateStart = element('date-start').value.replace(/-/g, '/')
    const dateEnd = element('date-end').value.replace(/-/g, '/')

    const hourStart = element('time-start').value
    const hourEnd = element('time-end').value

    const jsonContent = {

        old_name: oldName,
        name: name,
        ids: selectedDevices,
        trigger: {
            start_date: dateStart,
            end_date: dateEnd,
            start_time: hourStart,
            end_time: hourEnd,
            weekdays: selectedDays
        }

    }

    const button = element('submit-button');

    button.setAttribute('disabled', '');

    const request = new XMLHttpRequest();

    request.onload = function() {

        const jsonResponse = JSON.parse(this.responseText);

        if(jsonResponse.result === true){

            closeOverlay();
            retrieveEvents();

        }

        showNotification(jsonResponse.result, jsonResponse.status);

    }

    request.open("POST", "/edit-event");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(jsonContent));

}

function showNotification(success, message){

    const container = element('message-overlay');
    const title = success ? 'Operation succeeded' : 'Operation Failed';

    const div = document.createElement('div');
    div.setAttribute('class', 'message-div');

    const titleLabel = div.appendChild(document.createElement('label'));

    titleLabel.setAttribute('class', 'basic-text');
    titleLabel.innerText = title;

    const descriptionLabel = div.appendChild(document.createElement('label'));
    descriptionLabel.setAttribute('class', 'secondary-text');
    descriptionLabel.innerText = message;

    div.onclick = () => div.remove();

    container.appendChild(div);

    setTimeout(() => {
        div.remove();
    }, 10000);

}

window.addEventListener("load", (event) => {

    retrieveDevices();

});