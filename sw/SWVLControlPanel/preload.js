// preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    getSerialPorts: () => ipcRenderer.invoke('get-serials')
});
