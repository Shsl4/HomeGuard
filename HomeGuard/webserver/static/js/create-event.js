function element(id){
    return document.getElementById(id);
}

function cssVariable(name){
    return getComputedStyle(document.documentElement).getPropertyValue(name);
}

let selectedDeviceIndex = -1
let selectedDevices = []

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

function deviceSelected(){

    let select = element('device-select');
    selectedDeviceIndex = select.selectedIndex - 1;

}

function addDevice(){

    if(selectedDeviceIndex >= cached_devices.length) return;

    let device = cached_devices[selectedDeviceIndex]

    if(device != null && !selectedDevices.includes(selectedDeviceIndex)){

        let div = element('devices-wrapper');

        let button = div.appendChild(document.createElement('device-select-button'));
        button.setNameAndId(device.display_name, selectedDeviceIndex);
        selectedDevices.push(selectedDeviceIndex)

    }

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