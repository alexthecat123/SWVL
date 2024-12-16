const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process');
const path = require('path');
const executablePath = path.resolve(__dirname, 'main');
const child = spawn(executablePath);
const { ipcMain } = require('electron');


const { SerialPort } = require('serialport')

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 900,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'), // Specify the preload script
            contextIsolation: true, // Keep context isolation enabled
            nodeIntegration: false // Disable Node.js integration for security
        }
    })
    win.setMaximizable(false)
    win.setResizable(false)
    win.loadFile('index.html')
  }

setTimeout(() => {
    app.whenReady().then(() => {
        createWindow();
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) createWindow()
        })
    })
}, 1000);

ipcMain.handle('get-serials', async (event, arg1, arg2) => {
    let validPorts = [];
    await SerialPort.list().then((ports, err) => {
        if(err) {
          console.log(err.message);
          return
        }
        //console.log('ports', ports);
        for(let i = 0; i < ports.length; i++){
          if(ports[i].manufacturer != undefined){
              validPorts.push(ports[i]);
          }
        }
        console.log('validPorts', validPorts);  
        if (ports.length === 0) {
          console.log('No ports discovered');
        }
    })
    return validPorts; // This will be sent back to the renderer
});

app.on('window-all-closed', (event) => {
    event.preventDefault();
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
    setTimeout(function(){
        child.kill();
    },1000);
    setTimeout(function(){
        if (process.platform !== 'darwin') app.quit()
    },1000);
})

child.stdout.on('data', (data) => {
    console.log(data.toString("utf-8"));
});

child.stderr.on('data', (data) => {
    console.log(data.toString("utf-8"));
});

child.on('error', (error) => {
    console.log(error.toString("utf-8"));
});