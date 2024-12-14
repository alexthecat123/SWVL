const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process');
const path = require('path');
const executablePath = path.resolve(__dirname, 'main');
const child = spawn(executablePath);

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 900
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
/*
app.on('before-quit', (event) => {
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
    },100);
    setTimeout(function(){
        app.quit();
    },1000);
    //app.quit()//if (process.platform !== 'darwin') app.quit()   
});*/

child.stdout.on('data', (data) => {
    console.log(data.toString("utf-8"));
});

child.stderr.on('data', (data) => {
    console.log(data.toString("utf-8"));
});

child.on('error', (error) => {
    console.log(error.toString("utf-8"));
});