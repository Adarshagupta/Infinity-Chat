<?php
/*
Plugin Name: WooCommerce Chatbot Integration
Description: Integrates a chatbot with WooCommerce for order management
Version: 1.0
Author: Your Name
*/

function wcbi_enqueue_scripts() {
    wp_enqueue_script('wcbi-chatbot', plugin_dir_url(__FILE__) . 'chatbot.js', array('jquery'), '1.0', true);
    wp_localize_script('wcbi-chatbot', 'wcbi_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('wcbi-nonce')
    ));
}
add_action('wp_enqueue_scripts', 'wcbi_enqueue_scripts');

function wcbi_chatbot_html() {
    echo '<div id="wcbi-chatbot">
        <div id="wcbi-chat-messages"></div>
        <input type="text" id="wcbi-chat-input" placeholder="Type your message...">
        <button id="wcbi-chat-send">Send</button>
    </div>';
}
add_action('wp_footer', 'wcbi_chatbot_html');

function wcbi_process_message() {
    check_ajax_referer('wcbi-nonce', 'nonce');
    
    $message = sanitize_text_field($_POST['message']);
    $user_id = get_current_user_id();

    // Process the message and generate a response
    $response = wcbi_generate_response($message, $user_id);

    wp_send_json_success($response);
}
add_action('wp_ajax_wcbi_process_message', 'wcbi_process_message');
add_action('wp_ajax_nopriv_wcbi_process_message', 'wcbi_process_message');

function wcbi_generate_response($message, $user_id) {
    // Implement your chatbot logic here
    // This is where you'd integrate with your Flask API
    $api_url = 'https://your-flask-api.com/chat';
    $api_key = 'your_api_key_here';

    $response = wp_remote_post($api_url, array(
        'body' => json_encode(array(
            'message' => $message,
            'user_id' => $user_id,
            'api_key' => $api_key
        )),
        'headers' => array('Content-Type' => 'application/json')
    ));

    if (is_wp_error($response)) {
        return 'Sorry, there was an error processing your request.';
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    return $data['response'];
}
