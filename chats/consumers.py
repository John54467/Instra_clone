import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Avoid importing Django models at module import time. Importing ORM classes
# (like User or Message) at the top-level triggers Django to access
# settings.INSTALLED_APPS which fails if DJANGO_SETTINGS_MODULE isn't set
# yet (for example when an ASGI server imports the module before env is set).
# Import the models lazily inside methods where they're actually used.

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Debug logging for connection attempts
        import logging
        logger = logging.getLogger('chats.consumers')
        from django.contrib.auth.models import User
        from .models import Message  
        # Ensure user is authenticated before proceeding
        user = self.scope.get('user')
        # Log scope keys and basic info to help diagnose connect timeouts
        try:
            logger.debug('Connect called. scope keys=%s', list(self.scope.keys()))
            logger.debug('Connect scope user repr: %r', getattr(user, 'username', None))
            logger.debug('Channel layer present: %s', hasattr(self, 'channel_layer') and self.channel_layer is not None)
        except Exception:
            logger.exception('Error logging connect scope info')
        if not user or not getattr(user, 'is_authenticated', False):
            logger.warning(f"WebSocket connection rejected: anonymous user. scope={self.scope}")
            await self.close()
            return

        try:
            self.username = self.scope['url_route']['kwargs']['username']
            self.other_user = self.username
            # Build a deterministic room name based on usernames
            self.room_name = f"chat_{min(user.username, self.other_user)}_{max(user.username, self.other_user)}"
            self.room_group_name = f"chat_{self.room_name}"
            try:
                # Accept first so clients don't block waiting for acceptance.
                # Schedule group_add in the background to avoid a stalled channel layer
                # from preventing the WebSocket from becoming connected.
                await self.accept()
                logger.debug('Connection accepted; scheduling group_add for group: %s', self.room_group_name)
                # schedule background task to add channel to group
                asyncio.create_task(self._add_to_group(self.room_group_name, self.channel_name, user.username, logger))
                logger.info(f"WebSocket connect accepted: user={user.username}, room_group={self.room_group_name}")
            except Exception:
                logger.exception('Error during accept or scheduling group_add in connect')
                try:
                    await self.close()
                except Exception:
                    logger.exception('Error closing connection after failed connect')
                return
        except Exception:
            logger.exception("Error during WebSocket connect")
            try:
                await self.close()
            except Exception:
                logger.exception('Error closing connection after unexpected connect exception')

    async def _add_to_group(self, group_name, channel_name, username, logger):
        try:
            logger.debug('Adding channel to group (background): %s (channel=%s)', group_name, channel_name)
            await self.channel_layer.group_add(group_name, channel_name)
            logger.debug('Background group_add complete for user=%s group=%s', username, group_name)
        except Exception:
            logger.exception('Error in background group_add for user=%s group=%s', username, group_name)

    async def disconnect(self, close_code):
        import logging
        logger = logging.getLogger('chats.consumers')
        user = self.scope.get('user')
        username = getattr(user, 'username', None)
        chan = getattr(self, 'channel_name', None)
        room = getattr(self, 'room_group_name', None)
        try:
            if hasattr(self, 'channel_layer') and room:
                await self.channel_layer.group_discard(room, chan)
        except Exception:
            logger.exception('Error discarding channel from group during disconnect')

        # Log detailed disconnect info for diagnostics
        if close_code and close_code != 1000:
            # non-normal closure
            logger.warning(f"WebSocket disconnect (abnormal): user={username} channel={chan} room={room} code={close_code}")
        else:
            logger.info(f"WebSocket disconnect: user={username} channel={chan} room={room} code={close_code}")

    async def receive(self, text_data):
        import logging
        logger = logging.getLogger('chats.consumers')
        logger.info(f"WebSocket receive raw: {text_data}")

        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            if not message:
                logger.warning('Empty message received; ignoring')
                return

            sender = self.scope.get('user')
            if not sender or not getattr(sender, 'is_authenticated', False):
                logger.warning('Receive called for anonymous user; ignoring')
                return

            # Import ORM here
            from django.contrib.auth.models import User
            from .models import Message

            # Use async wrappers for ORM operations
            recipient = await sync_to_async(User.objects.get)(username=self.other_user)

            # Save message to DB (use sync_to_async for the helper)
            saved = await sync_to_async(Message.sender_message)(sender, recipient, message)

            try:
                sender_image_url = sender.profile.image.url
            except Exception:
                sender_image_url = ''
            try:
                message_date = saved.date.isoformat()
            except Exception:
                message_date = ''

            # Broadcast message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username,
                    'sender_image_url': sender_image_url,
                    'date': message_date,
                }
            )
        except Exception:
            logger.exception('Error handling incoming WebSocket message')

    async def chat_message(self, event):
        # Forward the same payload to the WebSocket client
        payload = {
            'message': event.get('message'),
            'sender': event.get('sender'),
            'sender_image_url': event.get('sender_image_url', ''),
            'date': event.get('date', ''),
        }
        await self.send(text_data=json.dumps(payload))
    
    async def receiver(self, event):
        try:
            payload = {
                'message': event.get('message'),
                'sender': event.get('sender'),
                'sender_image_url': event.get('sender_image_url', ''),
                'date': event.get('date', ''),
            }
            await self.send(text_data=json.dumps(payload))
        except Exception:
            import logging
            logging.getLogger('chats.consumers').exception('Error forwarding receiver event')
        
