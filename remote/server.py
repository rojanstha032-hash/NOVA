# ============================================
# NOVA - Remote Access Server (server.py)
# ============================================

from flask import Flask, request, jsonify, render_template_string
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

app = Flask(__name__)
nova_instance = None

MOBILE_UI = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Nova AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: white;
            font-family: Arial, sans-serif;
            min-height: 100vh;
        }
        .header {
            background: #111;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #333;
        }
        .header h1 { color: #00aaff; font-size: 28px; }
        .header p { color: #555; font-size: 12px; }
        .status {
            background: #111;
            margin: 10px;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            color: #00ff88;
            font-size: 14px;
        }
        .chat {
            height: 40vh;
            overflow-y: auto;
            padding: 10px;
            margin: 10px;
            background: #0d0d0d;
            border-radius: 10px;
        }
        .msg {
            margin: 8px 0;
            padding: 10px;
            border-radius: 10px;
            font-size: 14px;
        }
        .msg.nova { background: #1a1a2e; color: #00aaff; }
        .msg.user { background: #1a2e1a; color: #00ff88; text-align: right; }
        .input-area {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: #111;
            padding: 10px;
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            background: #1a1a1a;
            border: 1px solid #333;
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            background: #00aaff;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
        }
        .quick-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin: 10px;
        }
        .quick-btn {
            background: #1a1a2e;
            border: 1px solid #333;
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-size: 13px;
            cursor: pointer;
            text-align: center;
        }
        .mb-100 { margin-bottom: 100px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔱 NOVA</h1>
        <p>AI Personal Assistant - Remote Access</p>
    </div>
    
    <div class="status" id="status">● Connected to Nova</div>
    
    <div class="quick-buttons">
        <div class="quick-btn" onclick="sendCommand('take a screenshot')">📸 Screenshot</div>
        <div class="quick-btn" onclick="sendCommand('open youtube')">▶️ YouTube</div>
        <div class="quick-btn" onclick="sendCommand('open camera')">📷 Camera</div>
        <div class="quick-btn" onclick="sendCommand('what time is it')">⏰ Time</div>
        <div class="quick-btn" onclick="sendCommand('volume up')">🔊 Vol Up</div>
        <div class="quick-btn" onclick="sendCommand('volume down')">🔉 Vol Down</div>
        <div class="quick-btn" onclick="sendCommand('mute')">🔇 Mute</div>
        <div class="quick-btn" onclick="sendCommand('lock screen')">🔒 Lock</div>
    </div>
    
    <div class="chat mb-100" id="chat">
        <div class="msg nova">🔱 Nova: Hello! Ready to help you remotely!</div>
    </div>
    
    <div class="input-area">
        <input 
            type="text" 
            id="userInput" 
            placeholder="Type command..."
        />
        <button id="sendBtn">Send</button>
    </div>

    <script>
        var SECRET = "NOVA_PASSWORD_HERE";
        
        function addMessage(sender, text, type) {
            var chat = document.getElementById('chat');
            var msg = document.createElement('div');
            msg.className = 'msg ' + type;
            msg.textContent = sender + ': ' + text;
            chat.appendChild(msg);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function sendCommand(command) {
            document.getElementById('status').textContent = '🧠 Nova is thinking...';
            addMessage('You', command, 'user');
            
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/command', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var data = JSON.parse(xhr.responseText);
                        addMessage('Nova', data.response, 'nova');
                        document.getElementById('status').textContent = '● Connected to Nova';
                    } else {
                        document.getElementById('status').textContent = 'Error: ' + xhr.status;
                    }
                }
            };
            
            xhr.send(JSON.stringify({
                command: command,
                password: SECRET
            }));
        }
        
        function sendMessage() {
            var input = document.getElementById('userInput');
            var text = input.value.trim();
            if (!text) return;
            input.value = '';
            sendCommand(text);
        }
        
        document.getElementById('sendBtn').addEventListener('click', sendMessage);
        
        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        setInterval(function() {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/ping', true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    document.getElementById('status').textContent = '● Connected to Nova';
                }
            };
            xhr.send();
        }, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    html = MOBILE_UI.replace('NOVA_PASSWORD_HERE', config.REMOTE_SECRET)
    return html


@app.route('/ping')
def ping():
    return jsonify({"status": "online"})


@app.route('/command', methods=['POST'])
def command():
    data = request.json
    
    if data.get('password') != config.REMOTE_SECRET:
        return jsonify({"error": "Unauthorized!"}), 401
    
    command_text = data.get('command', '')
    if not command_text:
        return jsonify({"error": "No command!"}), 400
    
    if nova_instance:
        response_holder = []
        
        def get_response():
            desktop_result = nova_instance.desktop.process_command(command_text)
            if desktop_result:
                response_holder.append(desktop_result)
                return
            
            email_result = nova_instance.email_system.process_command(command_text)
            if email_result:
                response_holder.append(email_result)
                return
            
            response = nova_instance.brain.think(command_text)
            response_holder.append(response)
        
        t = threading.Thread(target=get_response)
        t.start()
        t.join(timeout=30)
        
        response = response_holder[0] if response_holder else "Command received!"
        
        threading.Thread(
            target=nova_instance.mouth.speak,
            args=(response,),
            daemon=True
        ).start()
        
        return jsonify({"response": response})
    
    return jsonify({"response": "Nova is not running!"})


def start_server(nova=None):
    global nova_instance
    nova_instance = nova
    
    print(f"🌐 Remote server starting...")
    print(f"📱 Open on phone: http://{config.TAILSCALE_IP}:{config.REMOTE_PORT}")
    print(f"🔐 Password: {config.REMOTE_SECRET}")
    
    app.run(
        host='0.0.0.0',
        port=config.REMOTE_PORT,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    start_server()