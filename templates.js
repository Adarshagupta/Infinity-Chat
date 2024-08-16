function() {{
    function loadChatbot() {{
        var chatbotDiv = document.createElement('div');
        chatbotDiv.id = 'ai-chatbot';
        chatbotDiv.innerHTML = `
            <div id="chat-header">
                <span>AI Chatbot</span>
                <svg id="chatbot-toggle" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div id="chatbot-content">
                <div id="chat-messages"></div>
                <div id="chat-input">
                    <input type="text" id="user-input" placeholder="Type your message...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        `;
        document.body.appendChild(chatbotDiv);
        
        var style = document.createElement('style');
        style.textContent = `
            #ai-chatbot {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 350px;
                background: rgba(255, 255, 255, 0.25);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 15px 15px 0 0;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transition: all 0.3s ease;
                font-family: Arial, sans-serif;
            }}
            #ai-chatbot:hover {{
                transform: scale(1.02);
            }}
            #chat-header {{
                background-color: #4F46E5;
                color: white;
                padding: 16px;
                font-weight: 600;
                font-size: 18px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
            }}
            #chatbot-toggle {{
                transition: transform 0.3s ease;
            }}
            #chatbot-content {{
                height: 450px;
                display: flex;
                flex-direction: column;
            }}
            #chat-messages {{
                flex-grow: 1;
                overflow-y: auto;
                padding: 24px;
            }}
            #chat-messages::-webkit-scrollbar {{
                width: 8px;
            }}
            #chat-messages::-webkit-scrollbar-track {{
                background: #EDF2F7;
            }}
            #chat-messages::-webkit-scrollbar-thumb {{
                background-color: #CBD5E0;
                border-radius: 20px;
                border: 3px solid #EDF2F7;
            }}
            #chat-input {{
                padding: 16px;
                border-top: 1px solid #E2E8F0;
                display: flex;
            }}
            #user-input {{
                flex-grow: 1;
                padding: 8px 16px;
                border: 1px solid #E2E8F0;
                border-radius: 9999px;
                margin-right: 8px;
                font-size: 14px;
            }}
            #user-input:focus {{
                outline: none;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
            }}
            #chat-input button {{
                background-color: #4F46E5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 9999px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }}
            #chat-input button:hover {{
                background-color: #4338CA;
            }}
            .message {{
                margin-bottom: 12px;
            }}
            .message p {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 18px;
                max-width: 80%;
            }}
            .ai-message p {{
                background-color: #F3F4F6;
            }}
            .user-message {{
                text-align: right;
            }}
            .user-message p {{
                background-color: #EBF8FF;
            }}
        `;
        document.head.appendChild(style);
        
        window.chatWithAI = async function(input) {{
            try {{
                const response = await fetch('https://chatcat-s1ny.onrender.com/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        input: input,
                        api_key: '{api_key}'
                    }})
                }});
                const data = await response.json();
                return data.response;
            }} catch (error) {{
                console.error('Error:', error);
                return `Error: ${{error.message || 'Unknown error occurred'}}`;
            }}
        }};

        window.addMessage = function(sender, message) {{
            const chatMessages = document.getElementById('chat-messages');
            const messageElement = document.createElement('div');
            messageElement.className = `message ${{sender === 'You' ? 'user-message' : 'ai-message'}}`;
            messageElement.innerHTML = `<p>${{message}}</p>`;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }};

        window.sendMessage = async function() {{
            const userInput = document.getElementById('user-input');
            const message = userInput.value.trim();
            if (message) {{
                addMessage('You', message);
                userInput.value = '';
                const response = await chatWithAI(message);
                addMessage('AI', response);
            }}
        }};

        // Add toggle functionality
        document.getElementById('chat-header').addEventListener('click', function() {{
            var content = document.getElementById('chatbot-content');
            var toggle = document.getElementById('chatbot-toggle');
            if (content.style.display === 'none') {{
                content.style.display = 'flex';
                toggle.style.transform = 'rotate(180deg)';
            }} else {{
                content.style.display = 'none';
                toggle.style.transform = 'rotate(0deg)';
            }}
        }});

        // Initialize chat
        addMessage('AI', 'Hello! How can I assist you today?');
    }}

    if (document.readyState === 'complete') {{
        loadChatbot();
    }} else {{
        window.addEventListener('load', loadChatbot);
    }}
}})();