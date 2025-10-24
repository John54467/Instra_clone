import os
import django
import asyncio
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'Instra_clone' package can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Instra_clone.settings')
django.setup()

from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from chats.consumers import ChatConsumer
from asgiref.sync import sync_to_async

# Enable DEBUG logging to stdout so ChatConsumer debug logs are visible
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
handler.setFormatter(formatter)
if not root_logger.handlers:
    root_logger.addHandler(handler)
logger = logging.getLogger('test_websocket')

async def run_test():
    # Ensure a test user exists
    user, created = await sync_to_async(User.objects.get_or_create)(username='test_ws_user')
    if created:
        user.set_password('password')
        await sync_to_async(user.save)()
        logger.info('Created test user')

    # Build a small ASGI wrapper that injects the user and url_route into the scope
    async def app(scope, receive, send):
        scope['user'] = user
        # The consumer expects url_route.kwargs.username
        scope['url_route'] = {'kwargs': {'username': 'luffy'}}
        inner = ChatConsumer.as_asgi()
        await inner(scope, receive, send)

    communicator = WebsocketCommunicator(app, "/ws/direct/luffy/")
    try:
        # Give a longer timeout for the consumer to accept when the test environment is slow
        connected, subprotocol = await asyncio.wait_for(communicator.connect(), timeout=10)
        logger.info(f'Connected: {connected}, subprotocol={subprotocol}')
    except asyncio.TimeoutError:
        logger.exception('Timeout while waiting for WebSocket connection acceptance')
        return
    except Exception:
        logger.exception('Unexpected error during communicator.connect()')
        return
    if not connected:
        await communicator.disconnect()
        return

    # Send a test message
    await communicator.send_json_to({'message': 'hello from test'})
    # wait a bit for group processing; increase timeout to reduce flakes
    receive_timeout = 5
    try:
        response = await communicator.receive_json_from(timeout=receive_timeout)
        logger.info(f'Received: {response}')
    except Exception as e:
        logger.warning(f'No response within {receive_timeout}s, retrying once...')
        try:
            response = await communicator.receive_json_from(timeout=receive_timeout)
            logger.info(f'Received on retry: {response}')
        except Exception:
            logger.exception('No response received after retry')

    await communicator.disconnect()

if __name__ == '__main__':
    asyncio.run(run_test())
