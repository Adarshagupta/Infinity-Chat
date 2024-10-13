import asyncio
import base64
import datetime
import os
from dotenv import load_dotenv
from hume.client import AsyncHumeClient
from hume.empathic_voice.chat.socket_client import ChatConnectOptions, ChatWebsocketConnection
from hume.empathic_voice.chat.types import SubscribeEvent
from hume.empathic_voice.types import UserInput
from hume.core.api_error import ApiError
from hume import MicrophoneInterface, Stream

async def main() -> None:
  # Retrieve any environment variables stored in the .env file
  load_dotenv()

  # Retrieve the API key, Secret key, and EVI config id from the environment variables
  HUME_API_KEY = os.getenv("HUME_API_KEY")
  HUME_SECRET_KEY = os.getenv("HUME_SECRET_KEY")
  HUME_CONFIG_ID = os.getenv("HUME_CONFIG_ID")

  # Initialize the asynchronous client, authenticating with your API key
  client = AsyncHumeClient(api_key=HUME_API_KEY)

  # Define options for the WebSocket connection, such as an EVI config id and a secret key for token authentication
  options = ChatConnectOptions(config_id=HUME_CONFIG_ID, secret_key=HUME_SECRET_KEY)
  
  # ...
