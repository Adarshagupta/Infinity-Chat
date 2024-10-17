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
        wp_localize_script('infin8t-chatbot', 'wcbi_ajax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('wcbi-nonce'),
            'is_user_logged_in' => is_user_logged_in()
        ));
    }

    public function chatbot_html() {
        // The chatbot HTML is now handled by the design.txt script
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
        if ($user_id === 0) {
            return "Please log in to manage your orders.";
        }

        // Check if the message is order-related
        if (stripos($message, 'order') !== false || stripos($message, 'cancel') !== false) {
            return $this->handle_order_query($message, $user_id);
        }

        // If not order-related, use the default API response
        $api_url = 'https://infin8t.tech/wp_chat';
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

    private function handle_order_query($message, $user_id) {
        if (stripos($message, 'cancel') !== false) {
            return $this->cancel_order($message, $user_id);
        } elseif (stripos($message, 'status') !== false || stripos($message, 'show') !== false) {
            return $this->get_order_status($message, $user_id);
        } elseif (stripos($message, 'list') !== false || stripos($message, 'my orders') !== false) {
            return $this->list_orders($user_id);
        }

        return "I'm sorry, I couldn't understand your order-related query. You can ask about order status, cancellation, or list your recent orders.";
    }

    private function cancel_order($message, $user_id) {
        preg_match('/\d+/', $message, $matches);
        if (empty($matches)) {
            return "I couldn't find an order number in your message. Please provide the order number you want to cancel.";
        }

        $order_id = $matches[0];
        $order = wc_get_order($order_id);

        if (!$order) {
            return "I'm sorry, I couldn't find an order with the number $order_id.";
        }

        if ($order->get_customer_id() != $user_id) {
            return "I'm sorry, but it seems that order #$order_id doesn't belong to you.";
        }

        if ($order->get_status() == 'cancelled') {
            return "Order #$order_id is already cancelled.";
        }

        $order->update_status('cancelled', 'Order cancelled by customer via chatbot.');
        return "Order #$order_id has been successfully cancelled. If you need any further assistance or have questions about refunds, please let me know.";
    }

    private function get_order_status($message, $user_id) {
        preg_match('/\d+/', $message, $matches);
        if (empty($matches)) {
            return $this->list_orders($user_id);
        }

        $order_id = $matches[0];
        $order = wc_get_order($order_id);

        if (!$order) {
            return "I'm sorry, I couldn't find an order with the number $order_id.";
        }

        if ($order->get_customer_id() != $user_id) {
            return "I'm sorry, but it seems that order #$order_id doesn't belong to you.";
        }

        $status = wc_get_order_status_name($order->get_status());
        return "The status of order #$order_id is: $status.";
    }

    private function list_orders($user_id) {
        $orders = wc_get_orders(array(
            'customer_id' => $user_id,
            'limit' => 5,
            'orderby' => 'date',
            'order' => 'DESC',
        ));

        if (empty($orders)) {
            return "You don't have any recent orders.";
        }

        $order_list = "Here are your 5 most recent orders:\n";
        foreach ($orders as $order) {
            $order_list .= "Order #{$order->get_id()}: " . wc_get_order_status_name($order->get_status()) . " - " . wc_price($order->get_total()) . "\n";
        }

        return $order_list;
    }
}
