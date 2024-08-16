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
The AI Chatbot Creator is a web application that allows users to create and integrate AI chatbots into their websites. The chatbots are powered by the Together API and can be trained on content extracted from any given URL. This documentation provides a detailed guide on how to use the application, its features, and the underlying technologies.

## Features
- **User Authentication**: Register, login, and logout functionality.
- **API Key Management**: Generate and manage API keys for chatbot integration.
- **URL Processing**: Extract text content from any URL to train the chatbot.
- **Chatbot Integration**: Generate integration code to embed the chatbot on any website.
- **Real-time Chat**: Chat with the AI-powered chatbot in real-time.
- **Rate Limiting**: Protect API endpoints from abuse with rate limiting.

## Technologies Used
- **Flask**: Python web framework for backend development.
- **SQLAlchemy**: SQL toolkit and ORM for database management.
- **Together API**: AI model for generating chatbot responses.
- **BeautifulSoup**: Python library for extracting text from HTML.
- **Flask-Limiter**: Rate limiting for Flask routes.
- **Flask-CORS**: Cross-Origin Resource Sharing for Flask.
- **HTML/CSS/JavaScript**: Frontend development.

## Installation
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
- **POST /register**: Register a new user.
- **POST /login**: Log in an existing user.
- **POST /logout**: Log out the current user.
- **POST /process_url**: Process a URL to extract text content.
- **POST /chat**: Interact with the AI chatbot.
- **GET /user/api_keys**: Get all API keys for the current user.
- **POST /delete_api_key**: Delete an API key.
- **GET /chatbot-design**: Get the chatbot design HTML.
- **GET /test_together_api**: Test the connection to the Together API.

## Frontend Implementation
The frontend is built using HTML, CSS, and JavaScript. The chatbot integration script is dynamically generated and can be embedded on any website using the provided API key.

### Example Chatbot Integration Script
```html
<script src="https://chatcat-s1ny.onrender.com/chatbot.js?api_key=your_api_key"></script>
```

### Chatbot Design
The chatbot design can be customized using CSS. The default design includes a header, chat messages area, and input field.

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
- **addMessage(sender, message)**: Adds a message to the chat messages area.
- **sendMessage()**: Sends the user's input to the chatbot and displays the response.

## Backend Implementation
The backend is built using Flask and SQLAlchemy. It handles user authentication, API key management, URL processing, and chatbot interactions.

### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_keys = db.Column(db.Text)  # Store as JSON string
```

### URL Processing
```python
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return ' '.join([p.text for p in soup.find_all('p')])
```

### Chatbot Interaction
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
The AI Chatbot Creator provides a powerful and flexible solution for integrating AI-powered chatbots into any website. With its user-friendly interface and robust backend, users can easily create, manage, and integrate chatbots tailored to their specific needs. By following this documentation, you can leverage the full potential of the application and enhance your website's user experience.
