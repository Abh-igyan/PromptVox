const vscode = require('vscode');
const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

let statusBarItem;
let pollTimer;
let isRecording = false;
let activeProgress = null;

const PYTHON_PATH = 'C:\\Users\\Abhigyan\\AppData\\Local\\Programs\\Python\\Python312\\python.exe';
const SCRIPT_PATH = 'C:\\Users\\Abhigyan\\antigravity-voice\\main.py';

function ensureBackendRunning() {
    return new Promise((resolve) => {
        const req = http.get('http://127.0.0.1:5998/ping', (res) => {
            resolve(true);
        });
        req.on('error', () => {
            // Spawn silent background worker
            try {
                const child = spawn(PYTHON_PATH, [SCRIPT_PATH], {
                    detached: true,
                    stdio: 'ignore',
                    windowsHide: true
                });
                child.unref();
            } catch (err) {
                console.error('Failed to spawn voice backend:', err);
            }
            // Give it 1.5s to initialize
            setTimeout(() => resolve(true), 1500);
        });
        req.setTimeout(500, () => {
            req.destroy();
            resolve(false);
        });
    });
}

function activate(context) {
    // 1. Auto-ensure backend is running upon extension activation
    ensureBackendRunning();

    // 2. Create Status Bar Item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'antigravity.voiceType';
    statusBarItem.text = '$(mic) Voice Type';
    statusBarItem.tooltip = 'Click or press Alt+V to Voice Type into Antigravity Chat';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // 3. Register Command
    const disposable = vscode.commands.registerCommand('antigravity.voiceType', async () => {
        // Automatically focus Antigravity chat panel so cursor is ready
        vscode.commands.executeCommand('antigravity.panel.focus').then(() => {}, () => {});

        await ensureBackendRunning();

        // Call toggle endpoint
        const req = http.get('http://127.0.0.1:5998/toggle', (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.is_recording) {
                        vscode.window.showInformationMessage('🎙️ Listening... Speak naturally, then press Alt+V to finish.');
                    }
                } catch (e) {}
            });
        });

        req.on('error', () => {
            vscode.window.showWarningMessage('Antigravity Voice is initializing. Please press Alt+V again in 2 seconds.');
        });
    });

    context.subscriptions.push(disposable);

    // 4. Live Status Bar Sync
    pollTimer = setInterval(() => {
        const req = http.get('http://127.0.0.1:5998/status', (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    isRecording = json.is_recording;

                    if (isRecording) {
                        statusBarItem.text = '$(record) Listening (Alt+V to stop)';
                        statusBarItem.color = '#ef4444';
                        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
                    } else if (json.state === 'transcribing') {
                        statusBarItem.text = '$(sync~spin) Transcribing...';
                        statusBarItem.color = '#38bdf8';
                        statusBarItem.backgroundColor = undefined;
                    } else if (json.state === 'done') {
                        statusBarItem.text = '$(check) Typed into Chat!';
                        statusBarItem.color = '#34d399';
                        statusBarItem.backgroundColor = undefined;
                    } else {
                        statusBarItem.text = '$(mic) Voice Type';
                        statusBarItem.color = undefined;
                        statusBarItem.backgroundColor = undefined;
                    }
                } catch (e) {}
            });
        });

        req.on('error', () => {
            statusBarItem.text = '$(mic) Voice Type';
            statusBarItem.color = undefined;
            statusBarItem.backgroundColor = undefined;
        });
    }, 800);
}

function deactivate() {
    if (pollTimer) {
        clearInterval(pollTimer);
    }
}

module.exports = {
    activate,
    deactivate
};
