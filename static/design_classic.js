(function() {
    // Classic design
    var style = document.createElement('style');
    style.textContent = `
        #ai-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-family: Times New Roman, serif;
        }
        #chatbot-button {
            background: #4a4a4a;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        #chatbot-container {
            display: none;
            width: 300px;
            height: 400px;
            background: #f0f0f0;
            border: 2px solid #4a4a4a;
            overflow: hidden;
        }
        #chatbot-header {
            background: #4a4a4a;
            color: white;
            padding: 10px;
            font-weight: bold;
        }
        #chatbot-messages {
            height: 300px;
            overflow-y: auto;
            padding: 10px;
            background: white;
        }
        #chatbot-input {
            display: flex;
            padding: 10px;
            background: #e0e0e0;
        }
        #user-input {
            flex-grow: 1;
            border: 1px solid #999;
            padding: 5px;
        }
        #send-button {
            background: #4a4a4a;
            color: white;
            border: none;
            padding: 5px 10px;
            margin-left: 5px;
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
            fetch('https://infin8t.tech/chat', {
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
