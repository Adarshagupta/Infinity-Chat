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

    // Function to suggest common order-related queries
    function suggestOrderQueries() {
        if (wcbi_ajax.is_user_logged_in) {
            var suggestions = [
                'Check order status',
                'Cancel my order',
                'List my recent orders'
            ];

            var suggestionHtml = '<div class="order-suggestions">';
            suggestions.forEach(function(suggestion) {
                suggestionHtml += '<button class="suggestion-btn">' + suggestion + '</button>';
            });
            suggestionHtml += '</div>';

            $('#wcbi-chat-messages').append(suggestionHtml);
        }
    }

    // Event listener for suggestion buttons
    $(document).on('click', '.suggestion-btn', function() {
        $('#wcbi-chat-input').val($(this).text());
        sendMessage();
    });

    // Call this function when you want to show order-related suggestions
    // For example, you could call it when the chat starts or after certain responses
    suggestOrderQueries();

    // Initialize chat with a greeting and suggestions
    if (wcbi_ajax.is_user_logged_in) {
        $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> Welcome! How can I assist you with your orders today?</p>');
        suggestOrderQueries();
    } else {
        $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> Welcome! Please log in to manage your orders. How else can I assist you?</p>');
    }

    // You can add more WooCommerce-specific functions here
    // For example:
    
    $(document).on('click', '.view-order-btn', function() {
        // This function could open a modal with more order details
        // or redirect to the order page
        alert('View order details functionality to be implemented');
    });
});
