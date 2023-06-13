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

    updateCreateButton();
    updateCreateButton();

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

function updateCreateButton(){

    const button = element('create-button');

    if(canSubmit()){
        button.removeAttribute('disabled');
    }
    else{
        button.setAttribute('disabled', '');
    }


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

    const button = element('create-button');

    button.setAttribute('disabled', '');

    const request = new XMLHttpRequest();

    request.onload = function() {

        const jsonResponse = JSON.parse(this.responseText);

        if(jsonResponse.result === true){

            closeOverlay();
            retrieveEvents();

        }

        console.log(jsonResponse)

    }

    request.open("POST", "/create_event");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(jsonContent));

}

function onAddViewLoaded(){

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

            updateCreateButton();

        });

    });

}