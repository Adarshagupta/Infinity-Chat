(function() {
    // Modern design
    var style = document.createElement('style');
    style.textContent = `
        #ai-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-family: Arial, sans-serif;
        }
        #chatbot-button {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        #chatbot-container {
            display: none;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        #chatbot-header {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            padding: 10px;
            font-weight: bold;
        }
        #chatbot-messages {
            height: 400px;
            overflow-y: auto;
            padding: 10px;
        }
        #chatbot-input {
            display: flex;
            padding: 10px;
        }
        #user-input {
            flex-grow: 1;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 5px 10px;
        }
        #send-button {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            margin-left: 10px;
            cursor: pointer;
        }
    `;
    document.head.appendChild(style);

    var chatbot = document.createElement('div');
    chatbot.id = 'ai-chatbot';
    chatbot.innerHTML = `
        <button id="chatbot-button">💬</button>
        <div id="chatbot-container">
            <div id="chatbot-header">AI Chatbot</div>
            <div id="chatbot-messages"></div>
            <div id="chatbot-input">
                <input type="text" id="user-input" placeholder="Type your message...">
                <button id="send-button">➤</button>
            </div>
        </div>
    `;
    document.body.appendChild(chatbot);

    var button = document.getElementById('chatbot-button');
    var container = document.getElementById('chatbot-container');
    var messages = document.getElementById('chatbot-messages');
    var input = document.getElementById('user-input');
    var send = document.getElementById('send-button');

    button.addEventListener('click', function() {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
    });

    function sendMessage() {
        var message = input.value.trim();
        if (message) {
            addMessage('You', message);
            input.value = '';
            fetch('http://localhost:5410/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input: message,
                    api_key: '{api_key}'
                })
            })
            .then(response => response.json())
            .then(data => {
                addMessage('AI', data.response);
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('AI', 'Sorry, there was an error processing your request.');
            });
        }
    }

    send.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function addMessage(sender, message) {
        var messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        messages.appendChild(messageElement);
        messages.scrollTop = messages.scrollHeight;
    }
})();
