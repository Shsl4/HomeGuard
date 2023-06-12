function element(id){
    return document.getElementById(id);
}

const nameEvent = document.querySelector('.event-name');
const selectedDevice = document.querySelector('.list-devices');
const selectedDateStart = document.querySelector('.date-start');
const selectedEndStart = document.querySelector('.date-end');
const selectedDayButton = document.querySelectorAll('.day');
const selectedHourStart = document.querySelector('.hour-start');
const selectedHourEnd = document.querySelector('.hour-end');

/* For error message. */

const errorMessageName = element('name-requirement');
const errorMessageDevice = element('device-requirement');
const errorMessageDate = element('date-requirement');
const errorMessageDay = element('day-requirement');
const errorMessageHour = element('hour-requirement');

// JSON.

var selectedDay = [];
var nameEventUser;
var nameDevice;
var hourBegin;
var minuteBegin;
var minuteEnd;
var hoursEnd;
var startDay;
var endDay;
var startMonth;
var endMonth;

var hourJSONBegin;
var hourJSONEnd;

// We check every input.

function checkInputEvent() {
    var isNameValid = checkName();
    var isDateValid = checkDate();
    var isDeviceValid = checkDevice();
    var isHourValid = checkHour();

    
    if (isNameValid && isDateValid && isDeviceValid && isHourValid && selectedDay.length > 0) { // If every input is valid.
        
        hourJSONBegin = formatHour(hourBegin, minuteBegin); // 22 h 30 -> 22,5
        hourJSONEnd = formatHour(hoursEnd, minuteEnd);

        console.log(nameEventUser);
        console.log("Trigger (Interval Date)");

        console.log(startDay);
        console.log(startMonth);
        console.log(endDay);
        console.log(endMonth);

        console.log("Time Windows");

        console.log(hourJSONBegin);
        console.log(hourJSONEnd);

        console.log("Days Selected");
        console.log(selectedDay);
    } else {
        
    }
}



// Function to select days.


selectedDayButton.forEach(function(day, index){
    day.addEventListener("click", function(){
        
        if(day.getAttribute('active') === 'true'){
            day.setAttribute('active', 'false');
            day.style.backgroundColor = "#484c59";

            const index = selectedDay.indexOf(day.innerHTML);

            selectedDay.splice(index, 1); // We remove the day that have been unselected.

            if(selectedDay.length > 0){
                errorMessageDay.style.color = 'green';
                errorMessageDay.innerHTML = `Day have been selected`;

            }
            else{
                errorMessageDay.style.color = 'red';
                errorMessageDay.innerHTML = `Select at least one day.`;
            }
            

        }
        else{
            day.setAttribute('active', 'true');
            day.style.backgroundColor = "rgb(0, 140, 255)";

            selectedDay.push(day.innerHTML);

            if(selectedDay.length > 0){
                errorMessageDay.style.color = 'green';
                errorMessageDay.innerHTML = `Day have been selected`;
                return true;
            }

            
        }
        
    });
});



function checkName(){ // We check the name of the event.
    
    if(nameEvent.value.length <= 4){
        errorMessageName.innerHTML = `The name have to be at least 5 characters.`;
        errorMessageName.style.color = 'red';
        return false;
    }
    errorMessageName.innerHTML = `Valid name`;
    errorMessageName.style.color = 'green';
    
    nameEventUser = nameEvent.value;
    
    return true;
}

function checkDevice(){ // We check if a device have been selected.
    if(selectedDevice.value !== 'Select Device'){
        errorMessageDevice.innerHTML = `You selected the device ${selectedDevice.value}`;
        errorMessageDevice.style.color = 'green';

        nameDevice = selectedDevice.value;

        return true;
    }
}

function checkDate(){ // We check if there is no overlap from the date that the user gave us.
    let dateStart = new Date(selectedDateStart.value);
    let dateEnd = new Date(selectedEndStart.value);

    if (Object.prototype.toString.call(dateStart) === "[object Date]" && Object.prototype.toString.call(dateEnd) === "[object Date]") { // We check if the date are set or not.
        if (isNaN(dateStart) && isNaN(dateEnd)) { 
          errorMessageDate.innerHTML = `Set a correct interval`;
          errorMessageDate.style.color = 'red';
        } else {
            if(dateStart !== undefined && dateEnd !== undefined){ // If the two have been given.
                if(dateStart > dateEnd){
                    errorMessageDate.innerHTML = `Interval Overlap`;
                    errorMessageDate.style.color = 'red';

                    return false;
                }
                else{
                    errorMessageDate.innerHTML = `Interval set`;
                    errorMessageDate.style.color = 'green';

                    // We get the month and the day of that month.

                    startDay = dateStart.getDate();
                    endDay = dateEnd.getDate();

                    startMonth = dateStart.getMonth() + 1;
                    endMonth = dateStart.getMonth() + 1;

                    return true;
                }
            }
        }
      }

}

// Function to check interval hour.

function checkHour() {
    var hourStart = selectedHourStart.value.split(':');
    var hourEnd = selectedHourEnd.value.split(':');

    if(hourStart.length > 1 && hourEnd.length > 1){
        var startHour = parseInt(hourStart[0]);
        var startMinutes = parseInt(hourStart[1]);
        var endHour = parseInt(hourEnd[0]);
        var endMinutes = parseInt(hourEnd[1]);

        if(endHour < startHour || (endHour === startHour && endMinutes < startMinutes)){ // Overlap to the next day
            errorMessageHour.innerHTML = `Hour set`;
            errorMessageHour.style.color = "green";
            
            hourBegin = startHour;
            hoursEnd = endHour;

            minuteBegin = startMinutes;
            minuteEnd = endMinutes;
            
            return true;
        }
        else if(startHour === endHour && startMinutes === endMinutes){ // Same hour and minute
            errorMessageHour.innerHTML = `Overlap hour`;
            errorMessageHour.style.color = "red";


            return false;
        }
        else if(startHour < endHour || (startHour === endHour && startMinutes < endMinutes)){ // The same day and valid time interval
            errorMessageHour.innerHTML = `Hour set`;
            errorMessageHour.style.color = "green";

            hourBegin = startHour;
            hoursEnd = endHour;

            minuteBegin = startMinutes;
            minuteEnd = endMinutes;

            return true;
        }
        else{
            errorMessageHour.innerHTML = `Overlap hour`;
            errorMessageHour.style.color = "red";

            return false;
        }
    }
}

function formatHour(hour, minute){
    var decimalHour = hour + minute / 60;
    return decimalHour;
}