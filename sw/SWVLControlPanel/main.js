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