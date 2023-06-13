
class DeviceInfo extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback(){

        this.attachShadow({ mode: "open" });

        const widths = ["width: 30%", "width: 20%", "width: 20%", "width: 20%"];
        const attrs = ["name", "ip", "mac", "activity"];

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

            updateCreateButton();

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
customElements.define("event-info", EventInfo);
customElements.define("device-info", DeviceInfo);
