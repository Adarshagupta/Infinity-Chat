<?php
/*
Plugin Name: WooCommerce Chatbot
Description: Integrates a chatbot with WooCommerce for order management
Version: 1.0
Author: Your Name
*/

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Check if WooCommerce is active
if (!in_array('woocommerce/woocommerce.php', apply_filters('active_plugins', get_option('active_plugins')))) {
    add_action('admin_notices', 'wc_chatbot_woocommerce_missing_notice');
    return;
}

function wc_chatbot_woocommerce_missing_notice() {
    ?>
    <div class="error">
        <p><?php _e('WooCommerce Chatbot requires WooCommerce to be installed and active.', 'wc-chatbot'); ?></p>
    </div>
    <?php
}

// Define plugin constants
define('WC_CHATBOT_VERSION', '1.0.0');
define('WC_CHATBOT_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('WC_CHATBOT_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include the main WC_Chatbot class
if (!class_exists('WC_Chatbot')) {
    include_once dirname(__FILE__) . '/includes/class-wc-chatbot.php';
}

// Include the tutorial class
include_once dirname(__FILE__) . '/includes/class-wc-chatbot-tutorial.php';

// Initialization
function wc_chatbot_init() {
    $GLOBALS['wc_chatbot'] = WC_Chatbot::get_instance();
}

add_action('plugins_loaded', 'wc_chatbot_init');

// Add tutorial page
function wc_chatbot_add_tutorial_page() {
    add_submenu_page(
        'options-general.php',
        'WC Chatbot Tutorial',
        'WC Chatbot Tutorial',
        'manage_options',
        'wc-chatbot-tutorial',
        array('WC_Chatbot_Tutorial', 'display_tutorial')
    );
}
add_action('admin_menu', 'wc_chatbot_add_tutorial_page');
