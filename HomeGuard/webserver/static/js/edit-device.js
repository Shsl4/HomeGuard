
let deviceIps = []

function fetchAndShowDeviceView(deviceId){

    let device = null;

    for(let i = 0; i < cached_devices.length; ++i){

        if(cached_devices[i].uuid === deviceId){
            device = cached_devices[i];
        }

    }

    if(!device) return;

    const request = new XMLHttpRequest();

    request.onload = function() {

        const overlay = element('overlay');

        overlay.innerHTML = this.responseText;

        onDeviceViewLoaded(device);
        showOverlay();

    }

    request.open("FETCH", "/device-view");
    request.send();

}

function checkIpField() {

    let field = element('ip-input');
    let button = element('ip-button');

    if(field.validity.valid && !deviceIps.includes(field.value)){
        button.removeAttribute('disabled');
    }
    else{
        button.setAttribute('disabled', '');
    }

}

function addIp() {

    const input = element('ip-input');
    const ip = input.value;

    if(!input.validity.valid) return;

    if(!deviceIps.includes(ip)){

        let div = element('ip-wrapper');

        let button = div.appendChild(document.createElement('device-select-button'));
        button.setNameAndId(ip, ip);

        button.setClickEvent(() => {

            let index = deviceIps.indexOf(button.id);

            if (index !== -1) {
                deviceIps.splice(index, 1);
            }

            updateSubmitDeviceButton();

            button.remove();

        });

        deviceIps.push(ip);

    }

    checkIpField();
    updateSubmitDeviceButton();

}

function onDeviceViewLoaded(device){

    element('device-name').value = device.display_name;

    element('view-title').innerText = 'Edit device';
    element('view-description').innerText = 'Edit an existing device';

    deviceIps = device.ip_addresses;

    let div = element('ip-wrapper');

    for(let i = 0; i < deviceIps.length; ++i){

        let button = div.appendChild(document.createElement('device-select-button'));

        button.setNameAndId(deviceIps[i], deviceIps[i]);

        button.setClickEvent(() => {

            let index = deviceIps.indexOf(button.id);

            if (index !== -1) {
                deviceIps.splice(index, 1);
            }

            updateSubmitDeviceButton();

            button.remove();

        });

    }

    element('mac-input').value = device.mac_address;

    const button = element('submit-button');
    const forget = element('forget-button');

    button.innerText = 'Edit'
    button.onclick = () => submitEditDeviceRequest(device.uuid);
    forget.onclick = () => submitForgetDeviceRequest(device.uuid);

    element('uuid-label').innerText = device.uuid;
    element('activity-label').innerText = device.last_activity;

    const namesDiv = element('recognized-names')
    const names = device.recognized_names;

    if(names.length === 0){

        const label = namesDiv.appendChild(document.createElement('label'));
        label.setAttribute('class', 'secondary-text');

        label.innerText = 'None';

    }

    for(let i = 0; i < names.length; ++i){

        const label = namesDiv.appendChild(document.createElement('label'));
        label.setAttribute('class', 'secondary-text');

        label.innerText = names[i];

    }

    updateSubmitDeviceButton()

}

function submitEditDeviceRequest(deviceId) {

    if (!canSubmitDevice()) return;

    const name = element('device-name').value

    const jsonContent = {

        mac_address: element('mac-input').value,
        uuid: deviceId,
        display_name: name,
        ip_addresses: deviceIps,

    }

    const button = element('submit-button');

    button.setAttribute('disabled', '');

    const request = new XMLHttpRequest();

    request.onload = function() {

        const jsonResponse = JSON.parse(this.responseText);

        if(jsonResponse.result === true){

            closeOverlay();
            retrieveDevices();

        }

        showNotification(jsonResponse.result, jsonResponse.status);

    }

    request.open("POST", "/edit-device");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(jsonContent));

}

function submitForgetDeviceRequest(deviceId) {

    const jsonContent = {
        uuid: deviceId
    }

    const request = new XMLHttpRequest();

    request.onload = function() {

        const jsonResponse = JSON.parse(this.responseText);

        if(jsonResponse.result === true){

            closeOverlay();
            retrieveDevices();

        }

        showNotification(jsonResponse.result, jsonResponse.status);

    }

    request.open("POST", "/forget-device");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(jsonContent));

}

function updateSubmitDeviceButton(){

    const button = element('submit-button');

    if(canSubmitDevice()){
        button.removeAttribute('disabled');
    }
    else{
        button.setAttribute('disabled', '');
    }

}

function canSubmitDevice(){

    if(!element('device-name').value) return false;

    return element('mac-input').validity.valid;

}
