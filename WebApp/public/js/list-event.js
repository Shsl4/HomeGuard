


fetch('js/test.json') // We have to change that in the future. // TODO.
  .then(response => response.json())
  .then(data => {

    for(var i = 0 ; i < data.length ; i++){
        const eventDiv = document.createElement('div');
        eventDiv.classList.add('event');

        const eventTitle = document.createElement('div');
        eventDiv.classList.add('title-event');

        const deviceName = document.createElement('div');
        deviceName.classList.add('device-event');


        eventDiv.innerHTML = `data[i].name`;
        deviceName.innerHTML = `data[i].device_name`;

        console.log(data[i].name);
    }
    var p = document.createElement('p');
    

    p.textContent = data[0].name;
    

    document.body.appendChild(p);
  })
  .catch((error) => {
    console.error('Erreur : ', error);
  });


// To go from 22,5 to 22 h 30.

function revertFormatHour(decimalHour){
    var hour = Math.floor(decimalHour);
    var minute = Math.round((decimalHour - hour) * 60);
    return [hour, minute];
}