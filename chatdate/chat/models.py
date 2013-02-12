import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import django.utils.timezone

class ReadyManager(models.Manager):
    def online_users(self, user):
        """
        Return all local users who are online at this time.
        TODO: implement location awareness.
        """
        User = get_user_model()
        five_minutes = django.utils.timezone.now() - datetime.timedelta(minutes=5)
        online = self.filter(last_seen__gt=five_minutes)
        return User.objects.filter(readytochat__in=online).exclude(email=user.email)

    def set_ready(self, user):
        """
        Update the value for last_seen for this user.
        """
        try:
            u = self.get(user=user)
            u.save()
        except ReadyToChat.DoesNotExist:
            self.create(user=user)

class ReadyToChat(models.Model):
    """
    Represents a user who is willing to chat
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    last_seen = models.DateTimeField(auto_now=True)
    objects = ReadyManager()

    def __unicode__(self):
        ago = (django.utils.timezone.now() - self.last_seen)
        return "%s - %s" % (self.user.email, ago)