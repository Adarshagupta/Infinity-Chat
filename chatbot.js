jQuery(document).ready(function($) {
    $('#wcbi-chat-send').on('click', function() {
        sendMessage();
    });

    function sendMessage() {
        var message = $('#wcbi-chat-input').val();
        if (message) {
            $('#wcbi-chat-messages').append('<p><strong>You:</strong> ' + message + '</p>');
            $('#wcbi-chat-input').val('');

            $.ajax({
                url: wcbi_ajax.ajax_url,
                type: 'POST',
                data: {
                    action: 'wcbi_process_message',
                    nonce: wcbi_ajax.nonce,
                    message: message
                },
                success: function(response) {
                    if (response.success) {
                        $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response.data + '</p>');
                        
                        // Check if the response contains order information
                        if (response.data.includes("Order #")) {
                            suggestOrderQueries();
                        }
                    } else {
                        $('#wcbi-chat-messages').append('<p><strong>Error:</strong> ' + response.data + '</p>');
                    }
                    $('#wcbi-chat-messages').scrollTop($('#wcbi-chat-messages')[0].scrollHeight);
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                    $('#wcbi-chat-messages').append('<p><strong>Error:</strong> Sorry, there was an error processing your request.</p>');
                }
            });
        }
    }

    // Initialize chat with a greeting and suggestions
    if (wcbi_ajax.is_user_logged_in) {
        $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> Welcome! How can I assist you with your orders today?</p>');
        suggestOrderQueries();
    } else {
        $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> Welcome! Please log in to manage your orders. How else can I assist you?</p>');
    }
});
