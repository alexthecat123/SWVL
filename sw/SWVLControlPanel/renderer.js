const videoElement = document.getElementById('webcam');

// Access the webcam
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
    } catch (error) {
        console.error('Error accessing webcam:', error);
    }
}


let connected = false;
let select = document.getElementById("serialPortDropdown");
let statusText = document.getElementById("connectionStatus");
let connectButton = document.getElementById("connect");

// what takes precedence, JS colors or CSS colors? Like, once the button gets disabled, will the CSS get rid of the red that we apply to it?
// check for if somebody unplugs the cable or conn fails, in which case our repeated poll of the gimbal will fail and we'll...
// automatically update the status to disconnected and start polling for devices again; i guess just poll python for conn status
// handle the exception in Python where either the cam or the Arduino get unplugged in the middle of a session
// disable all control options and set them all to default/zero until we're connected

async function connectSerial(serialPort) {
    let connectString = 'http://127.0.0.1:5000/serial-connect?port=' + serialPort;
    let result = await fetch(connectString,
        {
            method: "GET",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        }
    );
    result = result.json();
    //console.log(result);
    return result;
};

connectButton.addEventListener('click', async () => {
    if(connectButton.textContent == "Connect"){
        let result = await connectSerial(select.options[select.selectedIndex].value); 
        console.log(result);
        if(result == 1){
            connected = true; // now start polling connection status to make sure we stay connected and drop if not
            statusText.style.color = "#23D18B";
            statusText.textContent = "Gimbal Connected";
            select.disabled = true;
            connectButton.textContent = "Disconnect";
            connectButton.style.color = "#FFFFFF";
            connectButton.style.backgroundColor = "#FF2042";
        }
        else{
            connected = false;
            statusText.style.color = "#FF2042";
            statusText.textContent = "Connection Failed";
            select.disabled = false;
            connectButton.textContent = "Connect";
            connectButton.style.color = "#282C34";
            connectButton.style.backgroundColor = "#23D18B";
        }
    }
    else{
        /*let result = disconnectSerial(); // NOT IMPLEMENTED YET!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111
        if(result == 1){
            connected = false;
            statusText.style.color = "#FF2042";
            statusText.textContent = "Gimbal Disconnected";
            select.disabled = false;
        }
        else{
            connected = true;
            statusText.style.color = "#23D18B";
            statusText.textContent = "Gimbal Connected";
            select.disabled = true;
        }*/
    }
});

function populateSerialPorts() {
    window.electronAPI.getSerialPorts().then(result => {
        const currentlySelected = select.options[select.selectedIndex].value
        if(result.length == 0){
            for (let item in select.options) {
                select.options.remove(0); 
            }
            //console.log("No ports available.");
            let option = document.createElement("option");
            option.textContent = "No ports available!";
            option.value = "No ports available!";
            select.appendChild(option);
            statusText.style.color = "#FF2042";
            statusText.textContent = "Gimbal Disconnected";
            connectButton.disabled = true;
            connected = false;
        }
        else{
            for (let item in select.options) {
                select.options.remove(0); 
            }
            //console.log("Valid ports found.");
            for (let i = 0; i < result.length; i++) {
                let selection = result[i].path;
                let option = document.createElement("option");
                option.textContent = selection;
                option.value = selection;
                select.appendChild(option);
                if(statusText.textContent != "Connection Failed" && statusText.textContent != "Gimbal Connected"){
                    statusText.style.color = "#FF2042";
                    statusText.textContent = "Gimbal Disconnected";
                }
                if(statusText.textContent != "Gimbal Connected"){
                    connected = false;
                }
                connectButton.disabled = false;
                if(option.value == currentlySelected){
                    select.selectedIndex = i;
                }
            }
        }
    }).catch(err => {
        for (let item in select.options) {
            select.options.remove(0); 
        }
        console.error('Error when reading serial ports:', err);
        let option = document.createElement("option");
        option.textContent = "No ports available!";
        option.value = "No ports available!";
        select.appendChild(option);
        statusText.style.color = "#FF2042";
        statusText.textContent = "Gimbal Disconnected";
        connectButton.disabled = true;
        connected = false;
    });
}

setInterval(populateSerialPorts, 1000);

function startTracking() {
    fetch(`http://127.0.0.1:5000/start-tracking`,
        {
            method: "GET",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        }
    ).then(res => res.json()).then((data) => {
        console.log(data);

    })
}

function stopTracking() {
    fetch(`http://127.0.0.1:5000/stop-tracking`,
        {
            method: "GET",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        }
    ).then(res => res.json()).then((data) => {
        console.log(data);

    })
}

// Start the webcam when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    startWebcam();
    const trackingToggle = document.getElementById('trackingToggle');

// Add an event listener for the 'change' event
    trackingToggle.addEventListener('change', (event) => {
        if (event.target.checked) {
            startTracking();
        } else {
            stopTracking();
        }
    });
});