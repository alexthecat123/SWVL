const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process');
const path = require('path');
const executablePath = path.resolve(__dirname, 'main');
const child = spawn(executablePath);

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600
    })
  
    win.loadFile('index.html')
  }

setTimeout(() => {
    console.log('Waiting for Python...');
    app.whenReady().then(() => {
        createWindow();
        fetch(`http://127.0.0.1:5000/test-function?string=AlexTheCat123`,
            {
                method: "GET",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
            }
        ).then(res => res.json()).then((data) => {
            //data.result should have the result from python script
            //put the result inside the h1 tag 
            console.log(data.result);
    
        })
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) createWindow()
        })
    })
}, 1000);

app.on('window-all-closed', () => {
    child.kill();
    if (process.platform !== 'darwin') app.quit()
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