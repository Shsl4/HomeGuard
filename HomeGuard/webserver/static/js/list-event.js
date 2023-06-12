function element(id){
    return document.getElementById(id);
}

let cached_devices = []
let cached_events = []

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
            
            eventInfo.setAttribute('button-index', i);

            eventContainer.appendChild(eventInfo);

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

        for(let i = 0; i < cached_devices.length; ++i){

            let device = cached_devices[i];
            let deviceInfo = document.createElement('device-info');

            deviceInfo.setAttribute('class', 'list-div secondary-text');
            deviceInfo.setAttribute('name', device.display_name);
            deviceInfo.setAttribute('ip', device.ip_addresses[0]);
            deviceInfo.setAttribute('mac', device.mac_address);
            deviceInfo.setAttribute('activity', device.last_activity);
            deviceInfo.setAttribute('uuid', device.uuid);
            deviceInfo.setAttribute('button', 'Manage');
            
            deviceInfo.setAttribute('button-index', i);

            deviceContainer.appendChild(deviceInfo);

        }

        retrieveEvents()

    }

    request.open("GET", "/devices");
    request.send();

}


// Function to edit an event.

function editEvent(index){
    
    const overlay = document.querySelector('.editOverlay');
    const getEvents = document.querySelectorAll('.list-div');
    const eventName = document.getElementById('event-name');
    const selectName = document.getElementById('device-select');
    const dateStart = document.getElementById('date-start');
    const dateEnd = document.getElementById('date-end');
    const hourStart = document.getElementById('hour-start');
    const hourEnd = document.getElementById('hour-end');
    const listButtonDiv = document.querySelector('.submit-button-div');

    var nameEvent = getEvents[index + 1].getAttribute('name'); // + 1 because there is already a list-div that is not use for event.
    var deviceName = getEvents[index + 1].getAttribute('devices');
    var listDay = getEvents[index + 1].getAttribute('days').split(',');
    var start = getEvents[index + 1].getAttribute('start').split('/');
    var end = getEvents[index + 1].getAttribute('end').split('/');
    var time = getEvents[index + 1].getAttribute('time').replace(' ', '').split('-');

    // We set the values.


    eventName.value = nameEvent;
    selectName.value = deviceName;
    dateStart.value = `${start[2]}-${start[1]}-${start[0]}`;
    dateEnd.value = `${end[2]}-${end[1]}-${end[0]}`;
    hourStart.value = time[0];
    hourEnd.value = time[1].replace(' ', '');

    const deleteButton = document.createElement('button');
    deleteButton.innerHTML = "Delete";
    deleteButton.classList.add('delete-button', 'button-style', 'basic-text');

    // Function to delete the event. TODO.

    deleteButton.addEventListener('click', function() {
        console.log(`Event to delete is ${index}`);
    });

    listButtonDiv.appendChild(deleteButton);
    
    overlay.style.display = "flex";
    overlay.setAttribute('is-active', 'true');
}

// Function to apply the modification from the event.

function applyEditEvent(){
    const overlay = document.querySelector('.editOverlay');

    overlay.style.display = "none";
    overlay.setAttribute('is-active', 'false');

}



class DeviceInfo extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback(){

        this.attachShadow({ mode: "open" });

        const widths = ["width: 20%", "width: 10%", "width: 15%", "width: 15%", "width: 30%"];
        const attrs = ["name", "ip", "mac", "activity", "uuid"];

        generateListElementBody(this, widths, attrs);

    }

}

class EventInfo extends HTMLElement {

    constructor() {
        super();
    }

    connectedCallback(){

        this.attachShadow({ mode: "open" });

        const widths = ["width: 15%", "width: 20%", "width: 22.5%", "width: 10%", "width: 10%", "width: 12.5%"];
        const attrs = ["name", "devices", "days", "start", "end", "time"];

        generateListElementBody(this, widths, attrs);

    }

}

function generateListElementBody(elem, widths, attrs){

    for (let i = 0; i < widths.length; ++i){

        let div = document.createElement('div');

        div.setAttribute('style', widths[i]);
        const label1 =  div.appendChild(document.createElement('label'));

        label1.textContent = elem.hasAttribute(attrs[i]) ? elem.getAttribute(attrs[i]) : "";

        elem.shadowRoot.append(div);



    }

    let div = document.createElement('div');

    div.setAttribute('style','width: 10%');

    if(elem.hasAttribute('button')){

        const button =  div.appendChild(document.createElement('button'));

        button.textContent = elem.getAttribute('button');
        button.classList.add('button-style')
        button.setAttribute('onclick',  elem.hasAttribute("onclick") ? elem.getAttribute("onclick") : `editEvent(${elem.getAttribute('button-index')})`);
        button.setAttribute('index', elem.getAttribute('button-index'));

    }

    const linkElem = document.createElement('link');
    linkElem.setAttribute('rel', 'stylesheet');
    linkElem.setAttribute('href', 'css/shared.css');

    elem.shadowRoot.append(linkElem, div);

}

customElements.define("event-info", EventInfo);
customElements.define("device-info", DeviceInfo);

retrieveDevices()
