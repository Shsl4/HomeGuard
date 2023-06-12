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
            eventInfo.setAttribute('onclick', `editEvent(${i})`);
            
        
            
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
    const eventName = element('event-name');
    const selectName = element('device-select');
    const dateStart = element('date-start');
    const dateEnd = element('date-end');
    const hourStart = element('hour-start');
    const hourEnd = element('hour-end');
    const listButtonDiv = element('submit-div');

    let event = cached_events[index];

    let deviceNames = []

    for(var j = 0; j < event.ids.length; ++j){

        let device = deviceById(event.ids[j]);

        if(device != null){
            deviceNames.push(device.display_name);
        }

    }
    
    // We set the values.


    eventName.value = event.name;
    selectName.value = deviceNames[0];
    dateStart.value = event.trigger.start_date;
    dateEnd.value = event.trigger.end_date;
    hourStart.value = event.trigger.start_time;
    hourEnd.value = event.trigger.end_time;

    
    const deleteButton = document.createElement('button');
    deleteButton.innerHTML = "Delete";
    deleteButton.classList.add('delete-button', 'button-style', 'basic-text');

    // Function to delete the event. TODO.

    deleteButton.addEventListener('click', function() {
        console.log(`Event to delete is ${index}`);
    });
    const existingDeleteButton = listButtonDiv.querySelector('.delete-button');
    if (!existingDeleteButton) {
        const deleteButton = document.createElement('button');
        deleteButton.innerHTML = "Delete";
        deleteButton.classList.add('delete-button', 'button-style', 'basic-text');

        // Function to delete the event. TODO.
        deleteButton.addEventListener('click', function() {
            console.log(`Event to delete is ${index}`);
        });

        listButtonDiv.appendChild(deleteButton);
    } else {
        existingDeleteButton.addEventListener('click', function() {
            console.log(`Event to delete is ${index}`);
        });
    }
    
    
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
        button.setAttribute('onclick',  elem.hasAttribute("onclick") ? elem.getAttribute("onclick") : ``);
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
