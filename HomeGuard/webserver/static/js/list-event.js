function element(id){
    return document.getElementById(id);
}

let cached_devices = []

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

            deviceContainer.appendChild(deviceInfo);

        }

        retrieveEvents()

    }

    request.open("GET", "/devices");
    request.send();

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
        button.setAttribute('onclick',  elem.hasAttribute("onclick") ? elem.getAttribute("onclick") : "");

    }

    const linkElem = document.createElement('link');
    linkElem.setAttribute('rel', 'stylesheet');
    linkElem.setAttribute('href', 'css/shared.css');

    elem.shadowRoot.append(linkElem, div);

}

customElements.define("event-info", EventInfo);
customElements.define("device-info", DeviceInfo);

retrieveDevices()
