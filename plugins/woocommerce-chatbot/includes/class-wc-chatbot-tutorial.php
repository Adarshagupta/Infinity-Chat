<?php
if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class WC_Chatbot_Tutorial {
    public static function display_tutorial() {
        ?>
        <div class="wrap">
            <h1>WooCommerce Chatbot Tutorial</h1>
            <div class="card">
                <h2>Getting Started</h2>
                <ol>
                    <li>Ensure that WooCommerce is installed and activated on your WordPress site.</li>
                    <li>Go to the WooCommerce Chatbot settings page (WC Chatbot in the sidebar).</li>
                    <li>Enter your Infin8t API key in the provided field and save the settings.</li>
                </ol>
            </div>
            <div class="card">
                <h2>Customizing the Chatbot</h2>
                <ol>
                    <li>The chatbot will automatically appear on your WooCommerce store pages.</li>
                    <li>You can customize the appearance of the chatbot by modifying the CSS in your theme.</li>
                    <li>The chatbot uses the following HTML structure:
                        <pre>
&lt;div id="wcbi-chatbot"&gt;
    &lt;div id="wcbi-chat-messages"&gt;&lt;/div&gt;
    &lt;input type="text" id="wcbi-chat-input" placeholder="Type your message..."&gt;
    &lt;button id="wcbi-chat-send"&gt;Send&lt;/button&gt;
&lt;/div&gt;
                        </pre>
                    </li>
                </ol>
            </div>
            <div class="card">
                <h2>Using the Chatbot</h2>
                <ol>
                    <li>Customers can interact with the chatbot by typing messages in the input field.</li>
                    <li>The chatbot can handle various queries related to your WooCommerce store, such as:
                        <ul>
                            <li>Checking order status</li>
                            <li>Getting product information</li>
                            <li>Answering frequently asked questions</li>
                        </ul>
                    </li>
                    <li>The chatbot uses AI to understand and respond to customer queries based on your store's data.</li>
                </ol>
            </div>
            <div class="card">
                <h2>Troubleshooting</h2>
                <ul>
                    <li>If the chatbot doesn't appear, ensure that your theme is properly loading WordPress footer scripts.</li>
                    <li>Check the browser console for any JavaScript errors.</li>
                    <li>Verify that your Infin8t API key is correct in the settings page.</li>
                    <li>If you're experiencing issues, try disabling other plugins to check for conflicts.</li>
                </ul>
            </div>
        </div>
        <?php
    }
}
