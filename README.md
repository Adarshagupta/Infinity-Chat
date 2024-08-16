# AI Chatbot Creator Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [API Endpoints](#api-endpoints)
6. [Frontend Implementation](#frontend-implementation)
7. [Backend Implementation](#backend-implementation)
8. [Tutorials](#tutorials)
9. [Troubleshooting](#troubleshooting)
10. [Conclusion](#conclusion)

## Introduction
The AI Chatbot Creator is a web application designed to empower users to create, deploy, and manage AI-powered chatbots seamlessly. These chatbots are trained on content extracted from user-provided URLs and are capable of delivering real-time, context-aware responses. The application leverages the Together API for advanced AI capabilities, ensuring high-quality interactions.

## Features
- **User Authentication**: Secure registration, login, and logout functionalities to manage user accounts.
- **API Key Management**: Users can generate, view, and delete API keys for chatbot integration.
- **URL Processing**: Extract text content from any URL to train the chatbot, ensuring it understands the context of the website.
- **Chatbot Integration**: Generate custom integration code snippets to embed the chatbot on any website.
- **Real-time Chat**: Engage in real-time conversations with the AI-powered chatbot directly through the web interface.
- **Rate Limiting**: Protect API endpoints from abuse with configurable rate limits to ensure system stability.

## Technologies Used
- **Flask**: A lightweight WSGI web application framework in Python, used for backend development.
- **SQLAlchemy**: A SQL toolkit and Object-Relational Mapping (ORM) library for Python, used for database management.
- **Together API**: An advanced AI model that powers the chatbot's conversational capabilities.
- **BeautifulSoup**: A Python library used for parsing HTML and extracting text content from web pages.
- **Flask-Limiter**: A Flask extension for rate limiting API endpoints to prevent abuse.
- **Flask-CORS**: A Flask extension to handle Cross-Origin Resource Sharing (CORS), making cross-origin AJAX possible.
- **HTML/CSS/JavaScript**: Standard web technologies for frontend development.

## Installation
### Prerequisites
- Python 3.7+
- pip (Python package installer)
- Virtualenv (optional but recommended)

### Steps
1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/ai-chatbot-creator.git
    cd ai-chatbot-creator
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

4. **Set environment variables**:
    Create a `.env` file in the root directory and add the following:
    ```
    SECRET_KEY=your_secret_key
    DATABASE_URL=sqlite:///users.db
    TOGETHER_API_KEY=your_together_api_key
    ```

5. **Initialize the database**:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. **Run the application**:
    ```bash
    flask run
    ```

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
<script src="https://chatcat-s1ny.onrender.com/chatbot.js?api_key=your_api_key"></script>
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
            const response = await axios.post('https://chatcat-s1ny.onrender.com/chat', {
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
### How to Register and Log In
1. **Register**:
    - Navigate to the registration page.
    - Enter your email and password.
    - Click the "Register" button.

2. **Log In**:
    - Navigate to the login page.
    - Enter your email and password.
    - Click the "Log In" button.

### How to Process a URL and Generate an API Key
1. **Log In**: Ensure you are logged in to your account.
2. **Process URL**:
    - Navigate to the URL processing page.
    - Enter the URL you want to process.
    - Click the "Process URL" button.
    - Copy the generated API key and integration code.

### How to Integrate the Chatbot on Your Website
1. **Copy Integration Code**:
    - From the URL processing page, copy the integration code.
2. **Embed on Website**:
    - Paste the integration code into the HTML of your website.
    - Ensure the script is loaded correctly.

### How to Chat with the AI Chatbot
1. **Open Chatbot**:
    - On your website, open the chatbot interface.
2. **Send Messages**:
    - Type your message in the input field.
    - Click the "Send" button or press Enter.
    - View the AI-generated response.

## Troubleshooting
### Common Issues
- **API Key Not Working**: Ensure the API key is correctly copied and used in the integration script.
- **Chatbot Not Responding**: Check the browser console for errors and ensure the Together API is accessible.
- **Registration/Login Issues**: Ensure the email and password are correct and the server is running.

### Debugging Tips
- **Check Network Requests**: Use browser developer tools to inspect network requests and responses.
- **Review Server Logs**: Check the server logs for any errors or exceptions.
- **Test Together API**: Use the `/test_together_api` endpoint to test the connection to the Together API.

## Conclusion
The AI Chatbot Creator offers a comprehensive solution for integrating AI-powered chatbots into any website. With its intuitive frontend, robust backend, and advanced AI capabilities, users can create, manage, and deploy chatbots tailored to their specific needs. By following this detailed documentation, you can harness the full potential of the application and enhance your website's user experience.
