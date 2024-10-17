<?php
if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class WC_Chatbot {
    private static $instance = null;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'chatbot_html'));
        add_action('wp_ajax_wcbi_process_message', array($this, 'process_message'));
        add_action('wp_ajax_nopriv_wcbi_process_message', array($this, 'process_message'));
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
    }

    public function add_admin_menu() {
        add_options_page('WooCommerce Chatbot Settings', 'WC Chatbot', 'manage_options', 'wc-chatbot', array($this, 'settings_page'));
    }

    public function register_settings() {
        register_setting('wc_chatbot_options', 'wc_chatbot_api_key');
    }

    public function settings_page() {
        ?>
        <div class="wrap">
            <h1>WooCommerce Chatbot Settings</h1>
            <form method="post" action="options.php">
                <?php settings_fields('wc_chatbot_options'); ?>
                <?php do_settings_sections('wc_chatbot_options'); ?>
                <table class="form-table">
                    <tr valign="top">
                        <th scope="row">API Key</th>
                        <td><input type="text" name="wc_chatbot_api_key" value="<?php echo esc_attr(get_option('wc_chatbot_api_key')); ?>" /></td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
            <p>
                <a href="<?php echo admin_url('options-general.php?page=wc-chatbot-tutorial'); ?>" class="button button-secondary">
                    View Tutorial
                </a>
            </p>
        </div>
        <?php
    }

    public function enqueue_scripts() {
        $api_key = get_option('wc_chatbot_api_key');
        wp_enqueue_script('infin8t-chatbot', "https://infin8t.tech/chatbot.js?api_key={$api_key}", array(), null, true);
        wp_enqueue_script('wc-chatbot', WC_CHATBOT_PLUGIN_URL . 'assets/js/chatbot.js', array('jquery', 'infin8t-chatbot'), WC_CHATBOT_VERSION, true);
        wp_localize_script('wc-chatbot', 'wcbi_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('wcbi-nonce')
        ));

        // Add this line to enqueue the CSS
        wp_enqueue_style('wc-chatbot', WC_CHATBOT_PLUGIN_URL . 'assets/css/chatbot.css', array(), WC_CHATBOT_VERSION);
    }

    public function chatbot_html() {
        echo '<div id="wcbi-chatbot" class="wcbi-chatbot-container">
            <div class="wcbi-chatbot-header">
                <h3>Chat with us</h3>
                <button id="wcbi-chatbot-toggle">Toggle</button>
            </div>
            <div class="wcbi-chatbot-body">
                <div id="wcbi-chat-messages"></div>
                <div class="wcbi-chatbot-input">
                    <input type="text" id="wcbi-chat-input" placeholder="Type your message...">
                    <button id="wcbi-chat-send">Send</button>
                </div>
            </div>
        </div>';
    }

    public function process_message() {
        check_ajax_referer('wcbi-nonce', 'nonce');
        
        $message = sanitize_text_field($_POST['message']);
        $user_id = get_current_user_id();

        // Process the message and generate a response
        $response = $this->generate_response($message, $user_id);

        wp_send_json_success($response);
    }

    private function generate_response($message, $user_id) {
        // Implement your chatbot logic here
        // This is where you'd integrate with your Flask API
        $api_url = 'https://your-flask-api.com/wc_chat';
        $api_key = get_option('wc_chatbot_api_key');

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
}
