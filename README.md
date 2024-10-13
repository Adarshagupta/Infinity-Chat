# Infin8t.tech | Customer Support Infrastructure for Businesses
![Infin8t.tech Dashboard](https://aadarsha.onrender.com/static/uploads/Screenshot_2024-10-13_at_8.43.25_AM.png)

*Infin8t.tech Dashboard: Empowering businesses with AI-driven customer support*


## Introduction
Infin8t.tech is a state-of-the-art customer support infrastructure designed for businesses of all sizes. Our platform leverages cutting-edge AI technology to provide seamless, context-aware customer interactions through intelligent chatbots. By allowing businesses to create, deploy, and manage chatbots trained on their specific content, Infin8t.tech ensures personalized and efficient customer support that scales with your business needs.

## Features
- **User Authentication**: Secure registration, login, and logout functionalities for business accounts.
- **API Key Management**: Generate, view, and delete API keys for chatbot integration across multiple platforms.
- **URL Content Processing**: Extract and process content from business websites to train chatbots with relevant information.
- **Chatbot Integration**: Easy-to-use integration code snippe`ts for embedding chatbots on any website.
- **Real-time Chat Interface**: Engage customers with AI-powered chatbots through a user-friendly interface.
- **Analytics Dashboard**: Track chatbot performance, user interactions, and key metrics.
- **Multi-model AI Support**: Utilize various AI models including OpenAI GPT and Together AI for diverse capabilities.
- **Custom Prompts**: Create and manage custom prompts to guide AI responses for specific use cases.
- **E-commerce Integration**: Connect with popular e-commerce platforms for order and product-related queries.
- **Team Collaboration**: Manage team access and roles for collaborative chatbot management.
- **Voice Chat**: Process voice inputs and perform emotion analysis using Hume AI integration.
- **Multilingual Support**: AI-powered translation for global customer support.
- **Sentiment Analysis**: Real-time analysis of customer sentiment during interactions.
- **Customizable Chat Widgets**: Tailor the look and feel of your chatbot to match your brand.
- **Integration with CRM Systems**: Seamlessly connect with popular CRM platforms for comprehensive customer data management.
- **Advanced Analytics**: Gain deep insights into customer interactions, frequently asked questions, and support trends.

## Technologies Used
- **Flask**: Backend web application framework
- **SQLAlchemy**: Database ORM for efficient data management
- **Together AI & OpenAI**: Advanced AI models for chatbot intelligence
- **BeautifulSoup**: Web scraping for content extraction
- **Flask-Limiter**: API rate limiting for system stability
- **Flask-CORS**: Cross-Origin Resource Sharing support
- **Hume AI**: Voice processing and emotion analysis
- **APScheduler**: Background task scheduling
- **SQLite/PostgreSQL**: Database options for data storage
- **HTML/CSS/JavaScript**: Frontend technologies for user interface
- **Redis**: For caching and improving response times
- **Celery**: For handling background tasks and scheduled jobs
- **Docker**: For containerization and easy deployment
- **Nginx**: As a reverse proxy server
- **Elasticsearch**: For powerful full-text search capabilities

## Installation
### Prerequisites
- Python 3.7+
- pip (Python package installer)
- Virtual environment (recommended)

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/infin8t-tech.git
   cd infin8t-tech
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following:
   ```
   TOGETHER_API_KEY=your_together_api_key
   OPENAI_API_KEY=your_openai_api_key
   HUME_API_KEY=your_hume_api_key
   HUME_SECRET_KEY=your_hume_secret_key
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=your_smtp_port
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   ```

5. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

The application will be accessible at `http://localhost:5410`.

## API Endpoints
### User Authentication
- **POST /register**: Register a new user.
    - **Request Body**:
        ```json
        {
            "email": "user@example.com",
            "password": "secure_password"
        }
        ```
    - **Response**:
        ```json
        {
            "message": "User registered successfully"
        }
        ```

- **POST /login**: Log in an existing user.
    - **Request Body**:
        ```json
        {
            "email": "user@example.com",
            "password": "secure_password"
        }
        ```
    - **Response**:
        ```json
        {
            "message": "Logged in successfully"
        }
        ```

- **POST /logout**: Log out the current user.
    - **Response**:
        ```json
        {
            "message": "Logged out successfully"
        }
        ```

### URL Processing
- **POST /process_url**: Process a URL to extract text content.
    - **Request Body**:
        ```json
        {
            "url": "https://example.com"
        }
        ```
    - **Response**:
        ```json
        {
            "message": "Processing complete",
            "api_key": "generated_api_key",
            "integration_code": "<script src='...'></script>"
        }
        ```

### Chatbot Interaction
- **POST /chat**: Interact with the AI chatbot.
    - **Request Body**:
        ```json
        {
            "input": "Hello, how are you?",
            "api_key": "your_api_key"
        }
        ```
    - **Response**:
        ```json
        {
            "response": "I'm doing well, thank you! How can I assist you today?"
        }
        ```

### API Key Management
- **GET /user/api_keys**: Get all API keys for the current user.
    - **Response**:
        ```json
        {
            "api_keys": ["key1", "key2"]
        }
        ```

- **POST /delete_api_key**: Delete an API key.
    - **Request Body**:
        ```json
        {
            "api_key": "key_to_delete"
        }
        ```
    - **Response**:
        ```json
        {
            "message": "API key deleted successfully"
        }
        ```

### Chatbot Design
- **GET /chatbot-design**: Get the chatbot design HTML.
    - **Query Parameter**:
        ```
        api_key=your_api_key
        ```
    - **Response**:
        ```html
        <div id="ai-chatbot">...</div>
        ```

### Testing Together API
- **GET /test_together_api**: Test the connection to the Together API.
    - **Response**:
        ```
        Together API connection successful
        ```

## Frontend Implementation
The frontend is developed using HTML, CSS, and JavaScript, providing a user-friendly interface for interacting with the backend services.

### Example Chatbot Integration Script
To embed the chatbot on your website, include the following script in your HTML:
```html
<script src="https://infin8t.tech/chatbot.js?api_key=your_api_key"></script>
```

### Chatbot Design
The chatbot interface is designed to be intuitive and visually appealing. The default design includes:
- A header displaying the chatbot title.
- A chat messages area where messages are displayed.
- An input field for users to type their messages.
- A send button to submit messages.

```html
<div id="ai-chatbot">
    <div id="chat-header">AI Chatbot</div>
    <div id="chat-body">
        <div id="chat-messages"></div>
        <div id="chat-input">
            <input type="text" id="user-input" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
</div>
```

### JavaScript Functions
- **chatWithAI(input)**: Sends a message to the AI chatbot and returns the response.
    ```javascript
    async function chatWithAI(input) {
        try {
            const response = await axios.post('https://infin8t.tech/chat', {
                input: input,
                api_key: 'your_api_key'
            });
            return response.data.response;
        } catch (error) {
            console.error('Error:', error);
            return 'Error: Unable to get a response from the AI';
        }
    }
    ```

- **addMessage(sender, message)**: Adds a message to the chat messages area.
    ```javascript
    function addMessage(sender, message) {
        const chatMessages = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    ```

- **sendMessage()**: Sends the user's input to the chatbot and displays the response.
    ```javascript
    async function sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        if (message) {
            addMessage('You', message);
            userInput.value = '';
            const response = await chatWithAI(message);
            addMessage('AI', response);
        }
    }
    ```

## Backend Implementation
The backend is built using Flask, providing robust APIs for user management, chatbot training, and real-time chat interactions.

### User Model
The `User` model is defined using SQLAlchemy to manage user data, including email, password, and API keys.
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_keys = db.Column(db.Text)  # Store as JSON string
```

### URL Processing
The `extract_text_from_url` function uses BeautifulSoup to parse HTML and extract text content from web pages.
```python
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])
```

### Chatbot Interaction
The `/chat` endpoint interacts with the Together API to generate responses based on the extracted text content.
```python
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')
    api_key = request.json.get('api_key')

    context = extracted_texts.get(api_key, "No context available for this API key.")

    messages = [{
        "role": "system",
        "content": f"You are a helpful AI assistant trained on the following website content: {context}"
    }, {
        "role": "user",
        "content": user_input
    }]

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=messages,
        max_tokens=512,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"])

    return jsonify({"response": response.choices[0].message.content})
```

## Tutorials
### Setting Up Your Business Account
1. Register for an Infin8t.tech account using your business email.
2. Verify your email and complete the business profile setup.

### Creating Your First AI Chatbot
1. Log in to your Infin8t.tech dashboard.
2. Navigate to "Create New Chatbot" and enter your website URL.
3. Choose the AI model (OpenAI GPT or Together AI) for your chatbot.
4. Customize the chatbot's appearance and behavior.
5. Generate and copy the integration code.

### Integrating the Chatbot on Your Website
1. Copy the generated integration code from your dashboard.
2. Paste the code into your website's HTML, preferably just before the closing `</body>` tag.
3. Test the chatbot on your website to ensure proper functionality.

### Managing Team Access
1. Go to the "Team Management" section in your dashboard.
2. Click "Invite Team Member" and enter their email address.
3. Assign appropriate roles and permissions.
4. Team members will receive an invitation to join your Infin8t.tech workspace.

### Implementing Voice Chat
1. Navigate to the "Voice Chat" section in your dashboard.
2. Enable voice chat functionality for your chatbot.
3. Customize voice recognition settings and emotion analysis thresholds.
4. Test the voice chat feature using the provided playground.

### Setting Up E-commerce Integration
1. Go to the "Integrations" page in your dashboard.
2. Select your e-commerce platform (e.g., Shopify, WooCommerce).
3. Follow the step-by-step guide to connect your store.
4. Configure product catalog sync and order status integration.

## Advanced Features
### Custom AI Model Training
Infin8t.tech offers the ability to fine-tune AI models on your specific business data:
1. Prepare a dataset of past customer interactions.
2. Upload the dataset through the "Custom Training" interface.
3. Configure training parameters and initiate the fine-tuning process.
4. Monitor training progress and deploy the custom model when ready.

### Webhook Integration
Set up webhooks to receive real-time notifications:
1. Go to the "Webhooks" section in your settings.
2. Add a new webhook endpoint URL.
3. Select the events you want to be notified about (e.g., new conversations, resolved issues).
4. Test the webhook to ensure proper configuration.

## Security and Compliance
Infin8t.tech takes security and data privacy seriously:
- **Data Encryption**: All data is encrypted in transit and at rest.
- **GDPR Compliance**: Tools for data management and user consent in accordance with GDPR.
- **SOC 2 Certification**: Our infrastructure adheres to SOC 2 security standards.
- **Regular Security Audits**: We conduct frequent penetration testing and security assessments.

## Pricing and Plans
Infin8t.tech offers flexible pricing to suit businesses of all sizes:
- **Starter**: Perfect for small businesses, includes basic chatbot functionality.
- **Professional**: Ideal for growing companies, includes advanced AI features and integrations.
- **Enterprise**: Customized solutions for large organizations with dedicated support.

Visit our [pricing page](https://infin8t.tech/pricing) for detailed information and to choose the right plan for your business.

## FAQs
1. **Q: How long does it take to set up a chatbot?**
   A: Basic setup can be done in minutes, but for a fully customized solution, it may take a few hours to a few days depending on your requirements.

2. **Q: Can I integrate Infin8t.tech with my existing customer support tools?**
   A: Yes, we offer integrations with many popular CRM and helpdesk systems. Check our integrations page for a full list.

3. **Q: Is my data safe with Infin8t.tech?**
   A: Absolutely. We employ industry-standard security measures and are fully compliant with data protection regulations.

## Roadmap
Our upcoming features and improvements:
- AI-powered customer feedback analysis
- Enhanced multi-channel support (SMS, social media platforms)
- Advanced chatbot personality customization
- Improved self-learning capabilities for chatbots

## Contributing
We welcome contributions from the community. Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## License
Infin8t.tech is proprietary software. All rights reserved. See [LICENSE.md](LICENSE.md) for details.

## Contact and Support
- **Email**: support@infin8t.tech
- **Phone**: +1 (800) 123-4567
- **Live Chat**: Available on our website
- **Documentation**: [https://docs.infin8t.tech](https://docs.infin8t.tech)

For enterprise support, please contact our sales team at sales@infin8t.tech.

## Conclusion
Infin8t.tech is more than just a chatbot platform; it's a comprehensive customer support ecosystem designed to elevate your business's customer service capabilities. By harnessing the power of advanced AI, voice processing, and seamless integrations, Infin8t.tech empowers businesses to offer personalized, efficient, and scalable customer support. Whether you're a startup looking to streamline your support processes or an enterprise aiming to enhance customer experiences, Infin8t.tech has the tools, features, and expertise to transform your customer support infrastructure.

Join the future of customer support with Infin8t.tech and experience the difference that intelligent, AI-powered interactions can make for your business and your customers.