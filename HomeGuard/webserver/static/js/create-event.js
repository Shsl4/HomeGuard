function element(id){
    return document.getElementById(id);
}

function cssVariable(name){
    return getComputedStyle(document.documentElement).getPropertyValue(name);
}

let selectedDeviceIndex = -1
let selectedDevices = []
let selectedDays = []

function deviceSelected(){

    let select = element('device-select');
    selectedDeviceIndex = select.selectedIndex - 1;

}

function addDevice(){

    if(selectedDeviceIndex >= cached_devices.length) return;

    let device = cached_devices[selectedDeviceIndex]

    if(device != null && !selectedDevices.includes(device.uuid)){

        let div = element('devices-wrapper');

        let button = div.appendChild(document.createElement('device-select-button'));
        button.setNameAndId(device.display_name, device.uuid);
        selectedDevices.push(device.uuid)

    }

}

function canSubmit(){

    if(!element('event-name').value) return false;

    if(selectedDevices.length === 0) return false;

    if(!element('date-start').value) return false;

    if(!element('date-end').value) return false;

    if(!element('time-start').value) return false;

    if(!element('time-end').value) return false;

    return selectedDays.length > 0;

}

function submitRequest() {

    if (!canSubmit()) return;

    const name = element('event-name').value

    const dateStart = element('date-start').value.replace(/-/g, '/')
    const dateEnd = element('date-end').value.replace(/-/g, '/')

    const hourStart = element('time-start').value
    const hourEnd = element('time-end').value

    const jsonContent = {

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

    console.log(jsonContent)
    console.log(JSON.stringify(jsonContent))

    const request = new XMLHttpRequest();

    request.onload = function() {
        console.log(this.responseText)
    }

    request.open("POST", "/create_event");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(jsonContent));

}

function onCreateEvent(){

    element('event-name').value = '';
    element('date-start').value = '';
    element('date-end').value = '';
    element('time-start').value = '';
    element('time-end').value = '';
    element('device-select').selectedIndex = 0;

    selectedDevices = [];
    selectedDeviceIndex = [];
    selectedDays = [];

    for(let i = 0; i < cached_devices.length; ++i){

        let select = element('device-select');

        let option = select.appendChild(document.createElement('option'))
        let device = cached_devices[i];

        option.textContent = `${device.display_name} (${device.mac_address})`

    }

    const dayButtons = document.querySelectorAll('.day');

    dayButtons.forEach(function(day, index){

        day.addEventListener("click", function(){

            if(day.classList.contains('day-selected')){
                day.classList.remove('day-selected');
                selectedDays.splice(selectedDays.indexOf(day.getAttribute('id')), 1);
            }
            else{
                day.classList.add('day-selected');
                selectedDays.push(day.getAttribute('id'));
            }

        });

    });

}

class DeviceSelectButton extends HTMLElement {

    label = null
    id = null

    constructor() {
        super();
    }

    connectedCallback(){

        this.attachShadow({ mode: "open" });

        let div = document.createElement('div');

        div.setAttribute('class', 'basic-text selected-device-div');

        this.label = div.appendChild(document.createElement('label'));

        this.label.textContent = this.getAttribute('name');
        this.label.setAttribute('style', 'color: white');

        let button = div.appendChild(document.createElement('button'));

        button.setAttribute('class', 'remove-device-button');
        button.onclick = () => {

            let index = selectedDevices.indexOf(this.id);

            if (index !== -1) {
                selectedDevices.splice(index, 1);
            }

            this.remove();

        };
        button.textContent = 'X'

        const linkElem = document.createElement('link');
        linkElem.setAttribute('rel', 'stylesheet');
        linkElem.setAttribute('href', 'css/shared.css');

        this.shadowRoot.append(div, linkElem);

    }

    setNameAndId(name, id){
        this.label.textContent = name;
        this.id = id;
    }

}

customElements.define("device-select-button", DeviceSelectButton);
