// preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    getSerialPorts: (arg1) => ipcRenderer.invoke('get-serials', arg1)
});
