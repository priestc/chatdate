from django.contrib.auth import get_user_model
from .models import ReadyToChat
from relationship.models import Relationship

import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace

class UserNotConnected(Exception):
    pass

@namespace('/chat')
class ChatNamespace(BaseNamespace, BroadcastMixin):
    nicknames = []

    def initialize(self):
        self.session['hash'] = ''

    def send_to_user(self, event, user_hash, *args):
        pkt = dict(type="event",
                   name=event,
                   args=args,
                   endpoint=self.ns_name)

        for sess_id, socket in self.socket.server.sockets.items():
            if 'hash' in socket.session and socket.session['hash'] == user_hash:
                return socket.send_packet(pkt)

        raise UserNotConnected("No such user connected")

    def on_identify(self, hash):
        """
        As soon as a user signs into the site, the browser sends an "identify"
        message.
        """
        self.session['hash'] = hash
        User = get_user_model()
        user = User.objects.get(hash=hash)
        new_user = {'new_user': user.to_json()}
        online_and_nearby = []
        for nearby_user in user.local_users(online=True):
            # notify all neraby users that you have arrived.
            if not nearby_user.cares_about(user):
                continue # don't notify users who are set to ignore my type
            try:
                self.send_to_user("new_user", nearby_user.hash, new_user)
            except UserNotConnected:
                pass #ignore users who are not online
            online_and_nearby.append(nearby_user.to_json())

        self.send_to_user("nearby_users", hash, online_and_nearby) 
        ReadyToChat.objects.set_ready(hash)

    def on_message(self, message):
        """
        Handle all messages being sent between two people.
        """
        sent_by = message['sent_by']['hash']
        sent_to = message['sent_to']['hash']

        relationship = Relationship.objects.get_or_make_relationship(sent_to, sent_by)
        relationship.process_message(message['payload']['chat'], sent_by=sent_by)
        info_for_sent_by, info_for_sent_to, info_for_both = relationship.get_changes()

        sent_to_package = message
        sent_to_package['payload'].update(info_for_sent_to)
        sent_to_package['payload'].update(info_for_both)

        sent_by_package = message
        sent_by_package['payload'].update(info_for_sent_by)
        sent_by_package['payload'].update(info_for_both)

        if not relationship.blocked:
            self.send_to_user("message", sent_to, sent_to_package)
        self.send_to_user("message", sent_by, sent_by_package)

    def on_like(self, message):
        """
        When a user clicks the like button, record the like in the relationship
        table, and then send back a confirmation message.
        """
        hash1 = message['sent_by']['hash']
        hash2 = message['person_i_like']['hash']
        r = Relationship.objects.get_or_make_relationship(hash1, hash2)
        liked = r.record_like(hash1)
        
        if liked:
            self.send_to_user("verify", hash1, {
                "sent_by": {"hash": hash2},
                "sent_to": {"hash": hash1},
                "payload": {"like": message['person_i_like']['nickname']}
            })

    def on_block(self, message):
        hash1 = message['sent_by']['hash']
        hash2 = message['person_i_blocked']['hash']
        r = Relationship.objects.get_or_make_relationship(hash1, hash2)
        blocked = r.record_block(hash1)
        
        if blocked:
            self.send_to_user("verify", hash1, {
                "sent_by": {"hash": hash2},
                "sent_to": {"hash": hash1},
                "payload": {"blocked": message['person_i_blocked']['nickname']}
            })

    def recv_disconnect(self):
        """
        When a user disconnects from the site, this event is fired.
        """
        hash = self.session['hash']
        ReadyToChat.objects.filter(user__hash=hash).delete()
        User = get_user_model()
        user = User.objects.get(hash=hash)
        remove_user = user.to_json()
        for nearby_user in user.local_users(online=True):
            # notify all neraby users that you have left
            try:
                self.send_to_user("remove_user", nearby_user.hash, remove_user)
            except UserNotConnected:
                pass #ignore users who are not online

        self.disconnect(silent=True)