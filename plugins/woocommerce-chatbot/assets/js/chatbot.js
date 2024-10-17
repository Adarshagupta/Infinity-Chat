jQuery(document).ready(function($) {
    // Check if the Infin8t chatbot is loaded
    if (typeof chatWithAI !== 'function') {
        console.error('Infin8t chatbot not loaded. Please check your API key.');
        return;
    }

    // Toggle chatbot
    $('#wcbi-chatbot-toggle').on('click', function() {
        $('.wcbi-chatbot-container').toggleClass('collapsed');
    });

    $('#wcbi-chat-send').on('click', function() {
        sendMessage();
    });

    $('#wcbi-chat-input').on('keypress', function(e) {
        if (e.which == 13) {
            sendMessage();
        }
    });

    function sendMessage() {
        var message = $('#wcbi-chat-input').val();
        if (message) {
            $('#wcbi-chat-messages').append('<p><strong>You:</strong> ' + message + '</p>');
            $('#wcbi-chat-input').val('');

            chatWithAI(message).then(function(response) {
                $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response.response + '</p>');
                $('#wcbi-chat-messages').scrollTop($('#wcbi-chat-messages')[0].scrollHeight);
            }).catch(function(error) {
                console.error('Error:', error);
                $('#wcbi-chat-messages').append('<p><strong>Error:</strong> Sorry, there was an error processing your request.</p>');
            });
        }
    }
});
