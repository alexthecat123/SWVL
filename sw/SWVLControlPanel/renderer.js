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
