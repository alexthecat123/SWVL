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

let select = document.getElementById("serialPortDropdown");


function populateSerialPorts() {
    window.electronAPI.getSerialPorts().then(result => {
        console.log(result);
        if(result.length == 0){
            for (let item in select.options) {
                select.options.remove(0); 
            }
            console.log("No ports available.");
            let option = document.createElement("option");
            option.textContent = "No ports available!";
            option.value = "No ports available!";
            select.appendChild(option);
        }
        else{
            for (let item in select.options) {
                select.options.remove(0); 
            }
            console.log("Valid ports found.");
            for (let i = 0; i < result.length; i++) {
                let selection = result[i].path;
                let option = document.createElement("option");
                option.textContent = selection;
                option.value = selection;
                select.appendChild(option);
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
    });
}

setInterval(populateSerialPorts, 1000);

// we're polling ports every second now, so now allow us to connect to whichever is currently selected
// if no ports availavble is selected, obvuously grey out the connect button and update state so that we know we're disconned
// once connected, change connect button to a red disconnect button and freeze the port updating (still show the port we're conned to; jsut prevent changing)/dropdown until we either hit discon or..
// somebody unplugs the cable, in which case our repeated poll of the gimbal will fail and we'll automatically update the status to..
// disconnected and start polling for devices again
// also add ID-ing to the gimbal so that if we try to connect to a device, it'll only succeed if it's a gimbal


function connectSerial() {
    fetch(`http://127.0.0.1:5000/test-function?string=AlexTheCat123`,
        {
            method: "GET",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            },
        }
    ).then(res => res.json()).then((data) => {
        console.log(data.result);

    })
    fetch(`http://127.0.0.1:5000/serial-connect?port=/dev/ttyUSB0`,
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
    connectSerial();
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