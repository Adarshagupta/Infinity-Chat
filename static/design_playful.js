(function() {
    // Playful design
    var style = document.createElement('style');
    style.textContent = `
        #ai-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-family: 'Comic Sans MS', cursive;
        }
        #chatbot-button {
            background: #ff6b6b;
            color: white;
            border: none;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            font-size: 30px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        #chatbot-button:hover {
            transform: scale(1.1);
        }
        #chatbot-container {
            display: none;
            width: 320px;
            height: 450px;
            background: #ffeaa7;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }
        #chatbot-header {
            background: #ff6b6b;
            color: white;
            padding: 15px;
            font-weight: bold;
            font-size: 18px;
        }
        #chatbot-messages {
            height: 340px;
            overflow-y: auto;
            padding: 15px;
            background: #fff;
        }
        #chatbot-input {
            display: flex;
            padding: 10px;
            background: #fab1a0;
        }
        #user-input {
            flex-grow: 1;
            border: 2px solid #ff6b6b;
            border-radius: 20px;
            padding: 8px 15px;
            font-size: 16px;
        }
        #send-button {
            background: #ff6b6b;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 10px;
            cursor: pointer;
            font-size: 20px;
            transition: transform 0.2s;
        }
        #send-button:hover {
            transform: scale(1.1);
        }
    `;
    document.head.appendChild(style);

    // ... (rest of the code remains the same as modern design)
})();
