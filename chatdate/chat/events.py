from django_socketio import events, broadcast_channel
from .models import ReadyToChat
from relationship.models import Relationship

def emails_from_channel_name(channel_name):
    """
    Turn a channel name into a list of emails.
    chat://foo@bar.com/todd@foo.com -> ['foo@bar.com', 'todd@foo.com']
    """
    return channel_name[7:].split('/')

@events.on_message(channel="^chat://")
def message(request, socket, context, message):
    """
    Handle 'authentication' messages between two people, including chat requests
    and chat confirms.
    """
    type = message['type']

    if type == 'request':
        from_email = message['from_email']
        from_nickname = message['from_nickname']
        channel = "chat://" + message['to']
        data = {
            'type': 'request',
            'from_email': from_email,
            'from_nickname': from_nickname,
        }
        broadcast_channel(data, channel)
    elif type == 'confirm':
        # user conformed chat request, relay this confirmation to the requesting user.
        channel = "chat://" + message['requesting_email']
        data = {
            'type': 'confirm',
            'who_confirmed_email': message['who_confirmed_email'],
            'who_confirmed_nickname': message['who_confirmed_nickname']
        }
        broadcast_channel(data, channel)
        emails = [message['who_confirmed_email'], message['requesting_email']]
        Relationship.objects.get_or_make_relationship(*emails)

@events.on_message(channel="^chat://.*@.*/.*@.*")
def chat_message(request, socket, context, message):
    """
    Handle chat messages between two people.
    """
    channel_name = [x for x in socket.channels if len(x.split('@')) > 2][0]
    emails = emails_from_channel_name(channel_name)
    relationship = Relationship.objects.get_or_make_relationship(*emails)

    if message['type'] == 'chat':
        text = message['message']
        sent_by = message['sent_by_email']
        relationship.process_message(text, sent_by=sent_by)
        sender, sent_to, both = relationship.get_changes()
        if both:
            socket.send_and_broadcast_channel(both)
        if sender:
            channel = "email of sender"
            broadcast_channel(sender, channel)
        if sent_to:
            channel = "email of sent_to"
            broadcast_channel(sent_to, channel)
        socket.send_and_broadcast_channel(message)
    elif type == 'action':
        # user sent action such as 'facebook request', 'real life meeting', etc.
        # TODO: implement this at some point
        action = relationship.grant_action(message['action'])
        socket.send_and_broadcast_channel(action.as_dict())


@events.on_message(channel="^[a-z0-9]{32}")
def handle_message(request, socket, context, message):
    sent_by = message['sent_by']['hash']
    sent_to = message['sent_to']['hash']

    relationship = Relationship.objects.get_or_make_relationship(sent_to, sent_by)
    relationship.process_message(message['message'], sent_by=sent_by)
    info_for_sender, info_for_sent_to, info_for_both = relationship.get_changes()

    broadcast_channel(message, sent_to)
    broadcast_channel(message, sent_by)



