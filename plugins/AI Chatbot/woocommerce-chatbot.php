<?php
/*
Plugin Name: AI Chatbot by infin8t
Description: Adds an AI-powered chatbot to your WooCommerce store
Version: 1.0
Author: Prazwol
*/

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Add settings page
function wc_chatbot_add_settings_page() {
    add_options_page('AI Chatbot Settings', 'AI Chatbot', 'manage_options', 'wc-chatbot-settings', 'wc_chatbot_settings_page');
}
add_action('admin_menu', 'wc_chatbot_add_settings_page');

// Settings page content
function wc_chatbot_settings_page() {
    ?>
    <div class="wrap">
        <h1>AI Chatbot by infin8t Settings</h1>
        <div class="notice notice-info">
            <p><strong>How to get your API key:</strong></p>
            <ol>
                <li>Go to <a href="https://chatcat-moo7.onrender.com/" target="_blank">https://chatcat-moo7.onrender.com/</a></li>
                <li>Login or register for an account (it's free)</li>
                <li>Create a new chatbot</li>
                <li>Copy the generated API key</li>
                <li>Paste the API key in the field below</li>
            </ol>
        </div>
        <form method="post" action="options.php">
            <?php
            settings_fields('wc_chatbot_options');
            do_settings_sections('wc_chatbot_settings');
            submit_button();
            ?>
        </form>
    </div>
    <?php
}

// Register settings
function wc_chatbot_register_settings() {
    register_setting('wc_chatbot_options', 'wc_chatbot_api_key');
    add_settings_section('wc_chatbot_main', 'Main Settings', null, 'wc_chatbot_settings');
    add_settings_field('wc_chatbot_api_key', 'API Key', 'wc_chatbot_api_key_callback', 'wc_chatbot_settings', 'wc_chatbot_main');
}
add_action('admin_init', 'wc_chatbot_register_settings');

// API Key field callback
function wc_chatbot_api_key_callback() {
    $api_key = get_option('wc_chatbot_api_key');
    echo "<input type='text' name='wc_chatbot_api_key' value='$api_key' class='regular-text' />";
    echo "<p class='description'>Enter your Chatcat API key here. Don't have one? Follow the instructions above to get your API key.</p>";
}

// Add chatbot script to footer
function wc_chatbot_add_script() {
    $api_key = get_option('wc_chatbot_api_key');
    if (!empty($api_key)) {
        echo "<script src='https://chatcat-moo7.onrender.com/chatbot.js?api_key={$api_key}'></script>";
    }
}
add_action('wp_footer', 'wc_chatbot_add_script');

// Add settings link on plugin page
function wc_chatbot_settings_link($links) {
    $settings_link = '<a href="options-general.php?page=wc-chatbot-settings">Settings</a>';
    array_unshift($links, $settings_link);
    return $links;
}
$plugin = plugin_basename(__FILE__);
add_filter("plugin_action_links_$plugin", 'wc_chatbot_settings_link');