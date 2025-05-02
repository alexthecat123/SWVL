const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process');
const path = require('path');
const executablePath = path.resolve(__dirname, 'main');
const { exec } = require('child_process');
const os = require('os');
//execCommand('. ../SWVL_venv/bin/activate && python3 python/main.py');
//execCommand('.', ['../SWVL_venv/bin/activate']);
execCommand('../SWVL_venv/bin/python3', ['python/main.py']);
//const child = spawn(executablePath); // UNCOMMENT THIS TO SPAWN THE PYTHON PROCESS AGAIN
const { ipcMain } = require('electron');


const { SerialPort } = require('serialport');
const { kill } = require('process');

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 650,
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
          if(ports[i].manufacturer != null){
              validPorts.push(ports[i]);
          }
        }
        if(arg1 == true){
            console.log('validPorts', validPorts);
        }
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
        //child.kill(); // UNCOMMENT THIS TO KILL THE PYTHON PROCESS
        killProcessByName('python3').then(() => {
            console.log('python3 process killed successfully');
        }
        ).catch((error) => {
            console.error('Error killing python3 process:', error);
        });
        killProcessByName('pt_main_thread').then(() => {
            console.log('pt_main_thread process killed successfully');
        }
        ).catch((error) => {
            console.error('Error killing pt_main_thread process:', error);
        });
    },1000);
    setTimeout(function(){
        if (process.platform !== 'darwin') app.quit()
    },1000);
})


function killProcessByName(processName) {
  return new Promise((resolve, reject) => {
    const platform = os.platform();

    let command;

    if (platform === 'win32') {
      command = `taskkill /IM ${processName} /F`;
    } else if (platform === 'linux' || platform === 'darwin') {
      command = `pkill -f ${processName}`;
    } else {
      return reject(new Error(`Unsupported platform: ${platform}`));
    }

    exec(command, (error, stdout, stderr) => {
      if (error) {
        return reject(new Error(`Failed to kill process: ${stderr || error.message}`));
      }
      return resolve();
    });
  });
}

/*function execCommand(command) {
    const child = exec(command);
  
    child.stdout.pipe(process.stdout);
    child.stderr.pipe(process.stderr);
  
    child.on('exit', (code, signal) => {
      console.log(`Command exited with code ${code} and signal ${signal}`);
    });
  }*/

function execCommand(command, args = []) {
    const child = spawn(command, args, { stdio: 'inherit' });
    
    child.on('error', (err) => {
        console.error(`Failed to start command: ${err}`);
    });
    
    child.on('exit', (code, signal) => {
        console.log(`Command exited with code ${code} and signal ${signal}`);
    });
    }


/*child.stdout.on('data', (data) => {   // UNCOMMENT THIS TO SEE THE OUTPUT OF THE PYTHON PROCESS
    console.log(data.toString("utf-8"));
});

child.stderr.on('data', (data) => {
    console.log(data.toString("utf-8"));
});

child.on('error', (error) => {
    console.log(error.toString("utf-8"));
});*/