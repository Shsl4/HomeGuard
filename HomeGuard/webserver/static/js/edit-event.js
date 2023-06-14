
function fetchAndShowEditView(eventName){

    let event = null;

    for(let i = 0; i < cached_events.length; ++i){

        if(cached_events[i].name === eventName){
            event = cached_events[i];
        }

    }

    if(!event) return;

    const request = new XMLHttpRequest();

    request.onload = function() {

        const overlay = element('overlay');

        overlay.innerHTML = this.responseText;

        onEditViewLoaded(event);
        showOverlay();

    }

    request.open("FETCH", "/event-view");
    request.send();

}

function submitDeleteEventRequest(name) {

    const jsonContent = {
        name: name
    }

    const request = new XMLHttpRequest();

    request.onload = function() {

        const jsonResponse = JSON.parse(this.responseText);

        if(jsonResponse.result === true){

            closeOverlay();
            retrieveEvents();

        }

        showNotification(jsonResponse.result, jsonResponse.status);

    }

    request.open("POST", "/delete-event");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(JSON.stringify(jsonContent));

}

function onEditViewLoaded(event){

    element('event-name').value = event.name;
    element('date-start').value = event.trigger.start_date.replace(/\//g, '-');
    element('date-end').value = event.trigger.end_date.replace(/\//g, '-');
    element('time-start').value = event.trigger.start_time;
    element('time-end').value = event.trigger.end_time;
    element('device-select').selectedIndex = 0;

    element('view-title').innerText = 'Edit Event';
    element('view-description').innerText = 'Edit an existing event';

    selectedDevices = event.ids;
    selectedDeviceIndex = 0;
    selectedDays = event.trigger.weekdays;

    for(let i = 0; i < cached_devices.length; ++i){

        let select = element('device-select');

        let option = select.appendChild(document.createElement('option'))
        let device = cached_devices[i];

        option.textContent = `${device.display_name} (${device.mac_address})`

    }

    const dayButtons = document.querySelectorAll('.day');

    dayButtons.forEach(function(day, index){

        if(selectedDays.includes(day.getAttribute('id'))){
            day.classList.add('day-selected');
        }

        day.addEventListener("click", function(){

            if(day.classList.contains('day-selected')){
                day.classList.remove('day-selected');
                selectedDays.splice(selectedDays.indexOf(day.getAttribute('id')), 1);
            }
            else{
                day.classList.add('day-selected');
                selectedDays.push(day.getAttribute('id'));
            }

            updateSubmitEventButton();

        });

    });

    let div = element('devices-wrapper');

    for(let i = 0; i < selectedDevices.length; ++i){

        let device = deviceById(selectedDevices[i]);

        if(!device) continue;

        let button = div.appendChild(document.createElement('device-select-button'));
        button.setNameAndId(device.display_name, device.uuid);

        button.setClickEvent(() => {

            let index = selectedDevices.indexOf(button.id);

            if (index !== -1) {
                selectedDevices.splice(index, 1);
            }

            updateSubmitEventButton();

            button.remove();

        });

    }

    const button = element('submit-button');
    const deleteButton = element('delete-button');

    button.innerText = 'Edit'
    button.onclick = () => submitEditEventRequest(event.name);
    deleteButton.onclick = () => submitDeleteEventRequest(event.name);

    updateSubmitEventButton();

}