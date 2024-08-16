# AI Chatbot Creator API Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
    - [User Registration](#user-registration)
    - [User Login](#user-login)
    - [User Logout](#user-logout)
    - [Process URL](#process-url)
    - [Chat Interaction](#chat-interaction)
    - [Get User API Keys](#get-user-api-keys)
    - [Delete API Key](#delete-api-key)
    - [Chatbot Design](#chatbot-design)
    - [Test Together API](#test-together-api)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Conclusion](#conclusion)

## Introduction
The AI Chatbot Creator API provides a set of endpoints to manage user authentication, process URLs to extract text content, interact with the AI chatbot, and manage API keys for chatbot integration. This documentation outlines the available endpoints, request/response formats, and error handling.

## Authentication
All API endpoints require authentication. Users must register and log in to obtain a session token, which should be included in the request headers for authenticated endpoints.

## Endpoints

### User Registration
**Endpoint**: `POST /register`

**Description**: Register a new user.

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "secure_password"
}
```

**Response**:
```json
{
    "message": "User registered successfully"
}
```

### User Login
**Endpoint**: `POST /login`

**Description**: Log in an existing user.

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "secure_password"
}
```

**Response**:
```json
{
    "message": "Logged in successfully"
}
```

### User Logout
**Endpoint**: `POST /logout`

**Description**: Log out the current user.

**Response**:
```json
{
    "message": "Logged out successfully"
}
```

### Process URL
**Endpoint**: `POST /process_url`

**Description**: Process a URL to extract text content and generate an API key for chatbot integration.

**Request Body**:
```json
{
    "url": "https://example.com"
}
```

**Response**:
```json
{
    "message": "Processing complete",
    "api_key": "generated_api_key",
    "integration_code": "<script src='...'></script>"
}
```

### Chat Interaction
**Endpoint**: `POST /chat`

**Description**: Interact with the AI chatbot.

**Request Body**:
```json
{
    "input": "Hello, how are you?",
    "api_key": "your_api_key"
}
```

**Response**:
```json
{
    "response": "I'm doing well, thank you! How can I assist you today?"
}
```

### Get User API Keys
**Endpoint**: `GET /user/api_keys`

**Description**: Get all API keys for the current user.

**Response**:
```json
{
    "api_keys": ["key1", "key2"]
}
```

### Delete API Key
**Endpoint**: `POST /delete_api_key`

**Description**: Delete an API key.

**Request Body**:
```json
{
    "api_key": "key_to_delete"
}
```

**Response**:
```json
{
    "message": "API key deleted successfully"
}
```

### Chatbot Design
**Endpoint**: `GET /chatbot-design`

**Description**: Get the chatbot design HTML.

**Query Parameter**:
```
api_key=your_api_key
```

**Response**:
```html
<div id="ai-chatbot">...</div>
```

### Test Together API
**Endpoint**: `GET /test_together_api`

**Description**: Test the connection to the Together API.

**Response**:
```
Together API connection successful
```

## Error Handling
The API uses standard HTTP status codes to indicate the success or failure of a request. Common status codes include:
- `200 OK`: The request was successful.
- `201 Created`: The resource was successfully created.
- `400 Bad Request`: The request was invalid or malformed.
- `401 Unauthorized`: Authentication failed or user does not have permissions for the requested operation.
- `404 Not Found`: The requested resource was not found.
- `500 Internal Server Error`: An error occurred on the server.

Error responses will include a JSON object with an `error` key describing the issue:
```json
{
    "error": "Invalid API key"
}
```

## Rate Limiting
To prevent abuse and ensure fair usage, the API implements rate limiting. The default limits are set to 2000 requests per day and 1000 requests per hour. Exceeding these limits will result in a `429 Too Many Requests` status code.

## Conclusion
The AI Chatbot Creator API offers a robust set of endpoints to manage user accounts, process URLs, interact with AI chatbots, and manage API keys. By following this documentation, developers can integrate the API into their applications to create, deploy, and manage AI-powered chatbots seamlessly.
