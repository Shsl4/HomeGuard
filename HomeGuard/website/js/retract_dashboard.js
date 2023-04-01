var dashboard_main = document.querySelector('.dashboard-square')
var dashboard = document.querySelector('.dashboard')
var retract_elements = document.querySelectorAll('.retract');
var retract_icons = document.querySelectorAll('.icon');

function toggle_retract(){
    const visibility = dashboard.getAttribute('data-visible');

    if(visibility === "true"){
        dashboard.setAttribute('data-visible', false);
        dashboard_main.classList.remove('hidden');
        dashboard.classList.remove('hidden');

        for (var i = 0; i < retract_elements.length; i++) {
            retract_elements[i].classList.remove('display');
        }

        
        for (var i = 0; i < retract_icons.length; i++) {
            retract_icons[i].classList.remove('icon-retract');
        }
    }
    else{
        dashboard.setAttribute('data-visible', true);
        dashboard_main.classList.add('hidden')
        dashboard.classList.add('hidden');

        for (var i = 0; i < retract_elements.length; i++) {
            retract_elements[i].classList.add('display');
        }

        for (var i = 0; i < retract_icons.length; i++) {
            retract_icons[i].classList.add('icon-retract');
        }
    }
}