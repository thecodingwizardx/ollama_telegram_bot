import json
import logging

import aiohttp
from aiohttp import ClientTimeout

from config.config_loader import OLLAMA_BASE_URL


# This function sends the request and yields each line of the streamed response.
async def generate(payload: dict, prompt: str, timeout: int = 60):
    client_timeout = ClientTimeout(
        total=int(timeout)
    )  # Optional timeout for the request
    url = f"http://{OLLAMA_BASE_URL}:11434/api/chat"  # Ollama API URL

    async with aiohttp.ClientSession(timeout=client_timeout) as session:
        try:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        status=response.status, message=response.reason
                    )
                buffer = b""

                # Stream the response chunk by chunk
                async for chunk in response.content.iter_any():
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        line = line.strip()
                        if line:
                            yield json.loads(line)
        except aiohttp.ClientError as e:
            logging.error(f"Error during request: {e}")
