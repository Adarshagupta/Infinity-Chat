(function() {
    // Minimalist design
    var style = document.createElement('style');
    style.textContent = `
        #ai-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-family: Arial, sans-serif;
        }
        #chatbot-button {
            background: #333;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 20px;
            cursor: pointer;
        }
        #chatbot-container {
            display: none;
            width: 300px;
            height: 400px;
            background: white;
            border: 1px solid #ddd;
            overflow: hidden;
        }
        #chatbot-header {
            background: #333;
            color: white;
            padding: 10px;
            font-weight: bold;
        }
        #chatbot-messages {
            height: 320px;
            overflow-y: auto;
            padding: 10px;
        }
        #chatbot-input {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
        }
        #user-input {
            flex-grow: 1;
            border: none;
            padding: 5px;
            outline: none;
        }
        #send-button {
            background: none;
            border: none;
            color: #333;
            cursor: pointer;
            font-size: 20px;
        }
    `;
    document.head.appendChild(style);

    // ... (rest of the code remains the same as modern design)
})();
