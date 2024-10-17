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

        $response = $this->generate_response($message, $user_id);

        wp_send_json_success($response);
    }

    private function generate_response($message, $user_id) {
        if ($user_id === 0) {
            return "Please log in to manage your orders and access personalized information.";
        }

        $intent = $this->determine_intent($message);

        switch ($intent) {
            case 'order_status':
                return $this->get_order_status($message, $user_id);
            case 'cancel_order':
                return $this->cancel_order($message, $user_id);
            case 'list_orders':
                return $this->list_orders($user_id);
            case 'product_info':
                return $this->get_product_info($message);
            case 'track_order':
                return $this->track_order($message, $user_id);
            case 'return_policy':
                return $this->get_return_policy();
            case 'shipping_info':
                return $this->get_shipping_info();
            case 'modify_order':
                return $this->modify_order($message, $user_id);
            default:
                return $this->fallback_response($message);
        }
    }

    private function determine_intent($message) {
        $message = strtolower($message);
        if (strpos($message, 'status') !== false || strpos($message, 'where is my order') !== false) {
            return 'order_status';
        } elseif (strpos($message, 'cancel') !== false) {
            return 'cancel_order';
        } elseif (strpos($message, 'list') !== false || strpos($message, 'my orders') !== false) {
            return 'list_orders';
        } elseif (strpos($message, 'product') !== false || strpos($message, 'item') !== false || strpos($message, 'buy') !== false) {
            return 'product_info';
        } elseif (strpos($message, 'track') !== false) {
            return 'track_order';
        } elseif (strpos($message, 'return') !== false || strpos($message, 'refund') !== false) {
            return 'return_policy';
        } elseif (strpos($message, 'shipping') !== false || strpos($message, 'delivery') !== false) {
            return 'shipping_info';
        } elseif (strpos($message, 'modify') !== false || strpos($message, 'change') !== false || strpos($message, 'update') !== false) {
            return 'modify_order';
        }
        return 'unknown';
    }

    private function get_order_status($message, $user_id) {
        preg_match('/\d+/', $message, $matches);
        if (empty($matches)) {
            return "I couldn't find an order number in your message. Here are your recent orders:\n" . $this->list_orders($user_id);
        }

        $order_id = $matches[0];
        $order = wc_get_order($order_id);

        if (!$order || $order->get_customer_id() != $user_id) {
            return "I'm sorry, I couldn't find an order with the number $order_id associated with your account.";
        }

        $status = wc_get_order_status_name($order->get_status());
        $total = $order->get_total();
        $date = $order->get_date_created()->format('F j, Y');

        return "Order #$order_id:\nStatus: $status\nTotal: $total\nDate: $date\n\nCan I help you with anything else regarding this order?";
    }

    private function cancel_order($message, $user_id) {
        preg_match('/\d+/', $message, $matches);
        if (empty($matches)) {
            return "I couldn't find an order number in your message. Please provide the order number you want to cancel.";
        }

        $order_id = $matches[0];
        $order = wc_get_order($order_id);

        if (!$order || $order->get_customer_id() != $user_id) {
            return "I'm sorry, I couldn't find an order with the number $order_id associated with your account.";
        }

        if ($order->get_status() == 'cancelled') {
            return "Order #$order_id is already cancelled.";
        }

        if (!$order->has_status(array('pending', 'processing'))) {
            return "I'm sorry, but order #$order_id cannot be cancelled as it has already been " . $order->get_status() . ". Please contact our customer support for assistance.";
        }

        $order->update_status('cancelled', 'Order cancelled by customer via chatbot.');
        return "Order #$order_id has been successfully cancelled. If you need any further assistance or have questions about refunds, please let me know.";
    }

    private function list_orders($user_id) {
        $orders = wc_get_orders(array(
            'customer_id' => $user_id,
            'limit' => 5,
            'orderby' => 'date',
            'order' => 'DESC',
        ));

        if (empty($orders)) {
            return "You don't have any recent orders. Is there anything else I can help you with?";
        }

        $order_list = "Here are your 5 most recent orders:\n";
        foreach ($orders as $order) {
            $order_list .= "Order #{$order->get_id()}: " . wc_get_order_status_name($order->get_status()) . " - " . wc_price($order->get_total()) . " (" . $order->get_date_created()->format('F j, Y') . ")\n";
        }

        return $order_list . "\nWould you like more details about any of these orders?";
    }

    private function get_product_info($message) {
        $products = wc_get_products(array(
            'status' => 'publish',
            'limit' => 5,
            's' => $message,
        ));

        if (empty($products)) {
            return "I'm sorry, I couldn't find any products matching your query. Can you please try rephrasing or provide more details?";
        }

        $response = array(
            'message' => "Here are some products that match your query:",
            'products' => array()
        );

        foreach ($products as $product) {
            $response['products'][] = array(
                'name' => $product->get_name(),
                'price' => wc_price($product->get_price()),
                'sku' => $product->get_sku(),
                'stock' => $product->is_in_stock() ? 'In Stock' : 'Out of Stock',
                'image' => wp_get_attachment_image_url($product->get_image_id(), 'thumbnail'),
                'url' => $product->get_permalink(),
                'description' => wp_trim_words($product->get_short_description(), 20)
            );
        }

        return json_encode($response);
    }

    private function track_order($message, $user_id) {
        preg_match('/\d+/', $message, $matches);
        if (empty($matches)) {
            return "I couldn't find an order number in your message. Please provide the order number you want to track.";
        }

        $order_id = $matches[0];
        $order = wc_get_order($order_id);

        if (!$order || $order->get_customer_id() != $user_id) {
            return "I'm sorry, I couldn't find an order with the number $order_id associated with your account.";
        }

        $tracking_number = $order->get_meta('_tracking_number');
        $tracking_url = $order->get_meta('_tracking_url');

        if (!$tracking_number) {
            return "I'm sorry, but there's no tracking information available for order #$order_id yet. If the order has been shipped recently, please check back in 24-48 hours.";
        }

        $response = "Tracking information for order #$order_id:\n";
        $response .= "Tracking Number: $tracking_number\n";
        if ($tracking_url) { 
            $response .= "You can track your package at: $tracking_url";
        }

        return $response;
    }

    private function get_return_policy() {
        $return_policy = get_option('woocommerce_returns_policy');
        if (!$return_policy) {
            return "I'm sorry, but I couldn't find the return policy information. Please check our website or contact customer support for details about our return policy.";
        }
        return "Here's our return policy:\n\n$return_policy\n\nDo you have any specific questions about returns or refunds?";
    }

    private function get_shipping_info() {
        $shipping_methods = WC()->shipping()->get_shipping_methods();
        $response = "Here's information about our shipping methods:\n\n";

        foreach ($shipping_methods as $method) {
            if ($method->is_enabled()) {
                $response .= "{$method->get_method_title()}: {$method->get_method_description()}\n\n";
            }
        }

        return $response . "Do you have any specific questions about shipping or delivery?";
    }

    private function fallback_response($message) {
        return "I'm sorry, but I'm not sure how to respond to that. Can you please rephrase your question or ask about orders, products, shipping, or returns?";
    }

    private function modify_order($message, $user_id) {
        preg_match('/\d+/', $message, $matches);
        if (empty($matches)) {
            return "I couldn't find an order number in your message. Please provide the order number you want to modify.";
        }

        $order_id = $matches[0];
        $order = wc_get_order($order_id);

        if (!$order || $order->get_customer_id() != $user_id) {
            return "I'm sorry, I couldn't find an order with the number $order_id associated with your account.";
        }

        if (!$order->has_status(array('pending', 'processing'))) {
            return "I'm sorry, but order #$order_id cannot be modified as it has already been " . $order->get_status() . ". Please contact our customer support for assistance.";
        }

        // Determine what the user wants to modify
        if (strpos($message, 'address') !== false || strpos($message, 'shipping') !== false) {
            return $this->modify_shipping_address($order, $message);
        } elseif (strpos($message, 'add') !== false || strpos($message, 'remove') !== false) {
            return $this->modify_order_items($order, $message);
        } else {
            return "What would you like to modify in your order? You can change the shipping address or add/remove items.";
        }
    }

    private function modify_shipping_address($order, $message) {
        // In a real implementation, you'd parse the new address from the message
        // For this example, we'll just acknowledge the request
        return "I understand you want to change the shipping address for order #{$order->get_id()}. Please provide the new shipping address in this format: 'New address: [Full Address]'.";
    }

    private function modify_order_items($order, $message) {
        if (strpos($message, 'add') !== false) {
            // In a real implementation, you'd parse the product details from the message
            return "To add an item to your order, please provide the product name or ID and quantity in this format: 'Add: [Product Name/ID], [Quantity]'.";
        } elseif (strpos($message, 'remove') !== false) {
            // In a real implementation, you'd parse the product details from the message
            return "To remove an item from your order, please provide the product name or ID in this format: 'Remove: [Product Name/ID]'.";
        } else {
            return "I'm not sure if you want to add or remove items. Please specify 'add' or 'remove' followed by the product details.";
        }
    }
}
