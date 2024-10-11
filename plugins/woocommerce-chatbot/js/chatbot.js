jQuery(document).ready(function($) {
    var chatbotContainer = $('#wc-chatbot-container');
    var chatbotMessages = $('#wc-chatbot-messages');
    var chatbotInput = $('#wc-chatbot-input input');
    var chatbotSendBtn = $('#wc-chatbot-input button');

    chatbotSendBtn.on('click', sendMessage);
    chatbotInput.on('keypress', function(e) {
        if (e.which == 13) {
            sendMessage();
        }
    });

    function sendMessage() {
        var message = chatbotInput.val().trim();
        if (message) {
            appendMessage('You', message);
            chatbotInput.val('');

            // Send message to the Chatcat API
            $.ajax({
                url: 'https://infin8t.onrender.com/chat',
                method: 'POST',
                data: JSON.stringify({
                    input: message,
                    api_key: wc_chatbot_data.api_key
                }),
                contentType: 'application/json',
                success: function(response) {
                    if (response && response.response) {
                        appendMessage('Chatbot', response.response);
                    } else {
                        appendMessage('Chatbot', 'I apologize, but I couldn\'t process your request at the moment.');
                    }
                },
                error: function(xhr, status, error) {
                    console.error("API Error:", error);
                    appendMessage('Chatbot', 'Sorry, I encountered an error. Please try again later.');
                }
            });
        }
    }

    function appendMessage(sender, message) {
        chatbotMessages.append('<p><strong>' + sender + ':</strong> ' + message + '</p>');
        chatbotMessages.scrollTop(chatbotMessages[0].scrollHeight);
    }
});