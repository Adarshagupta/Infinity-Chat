jQuery(document).ready(function($) {
    $('#wcbi-chat-send').on('click', function() {
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
                    } else {
                        $('#wcbi-chat-messages').append('<p><strong>Error:</strong> ' + response.data + '</p>');
                    }
                }
            });
        }
    });
});
