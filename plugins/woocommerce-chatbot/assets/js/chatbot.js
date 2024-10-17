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
                        if (response.data.includes("change the shipping address") || 
                            response.data.includes("add an item to your order") || 
                            response.data.includes("remove an item from your order")) {
                            handleOrderModification(response.data);
                        } else {
                            $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response.data + '</p>');
                        }
                        
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

    function displayProductCards(data) {
        var productCardsHtml = '<div class="product-cards">';
        productCardsHtml += '<p><strong>Chatbot:</strong> ' + data.message + '</p>';
        
        data.products.forEach(function(product) {
            productCardsHtml += `
                <div class="product-card">
                    <img src="${product.image}" alt="${product.name}" class="product-image">
                    <h3>${product.name}</h3>
                    <p class="price">${product.price}</p>
                    <p class="sku">SKU: ${product.sku}</p>
                    <p class="stock">${product.stock}</p>
                    <p class="description">${product.description}</p>
                    <a href="${product.url}" class="shop-button" target="_blank">Shop Now</a>
                </div>
            `;
        });
        
        productCardsHtml += '</div>';
        $('#wcbi-chat-messages').append(productCardsHtml);
    }

    // Function to suggest common order-related queries
    function suggestOrderQueries() {
        if (wcbi_ajax.is_user_logged_in) {
            var suggestions = [
                'Check order status',
                'Cancel my order',
                'List my recent orders',
                'Modify my order'
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

    function handleOrderModification(response) {
        if (response.includes("change the shipping address")) {
            $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response + '</p>');
            $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> Please enter the new address below:</p>');
            $('#wcbi-chat-input').attr('placeholder', 'New address: [Full Address]');
        } else if (response.includes("add an item to your order")) {
            $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response + '</p>');
            $('#wcbi-chat-input').attr('placeholder', 'Add: [Product Name/ID], [Quantity]');
        } else if (response.includes("remove an item from your order")) {
            $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response + '</p>');
            $('#wcbi-chat-input').attr('placeholder', 'Remove: [Product Name/ID]');
        } else {
            $('#wcbi-chat-messages').append('<p><strong>Chatbot:</strong> ' + response + '</p>');
        }
    }
});
