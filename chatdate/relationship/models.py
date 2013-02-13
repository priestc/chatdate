import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import django.utils.timezone

def has_laugh(text):
    return "hehe" in text or "haha" in text

def has_kissy(text):
    return ":*" in text or ";-*" in text or ":-*" in text or "<3" in text

RELATIONSHIP_STATUSES = (
    (1, 'Contact'),
    (2, 'Acquaintance'),
    (3, 'Friends'),
    (4, 'IRL Friends'),
)

class RelationshipStats(models.Model):
    """
    Represents stats for a user in a relationship.
    `span_detected` gets flipped to True after a mesage has been sent more than
    24 hours apart.
    """
    long_distance_partner = models.BooleanField(default=False)
    high_karma_partner = models.BooleanField(default=False)
    laugh_lines = models.IntegerField(default=0)
    like = models.BooleanField(default=False)
    kissy_lines = models.IntegerField(default=0)
    total_lines = models.IntegerField(default=0)
    span_detected = models.BooleanField(default=False)


class RelationshipManager(models.Manager):
    def my_relationships(self, user):
        return self.filter(models.Q(user1=user) | models.Q(user2=user))

    def get_or_make_relationship(self, email1, email2):
        """
        Make a relationship object from two users, if one doesnt alreasy exist.
        """
        emails = sorted([email1, email2])
        try:
            return Relationship.objects.get(user1__email=emails[0], user2__email=emails[1])
        except Relationship.DoesNotExist:
            User = get_user_model()
            user1 = User.objects.get(email=emails[0])
            user2 = User.objects.get(email=emails[1])
            stat1 = RelationshipStats.objects.create()
            stat2 = RelationshipStats.objects.create()
            Relationship.objects.create(
                user1=user1, user2=user2,
                user1_stats=stat1, user2_stats=stat2
            )

class Relationship(models.Model):
    """
    Represents a connection between two users.
    """
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user2")

    user1_stats = models.ForeignKey(RelationshipStats, related_name="stats1")
    user2_stats = models.ForeignKey(RelationshipStats, related_name="stats2")

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    blocked = models.BooleanField(default=False)
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES, default=0)
    met = models.BooleanField(default=False)

    objects = RelationshipManager()

    def __unicode__(self):
        return "%s + %s (%s)" % (self.user1.nickname, self.user2.nickname, self.get_status_display())

    def process_message(self, text, sent_by):
        """
        When two people in a relationship speak to each other, the text goes
        through this function to keep track of the stages. `message` can be
        sent by either person in the relationship.
        """
        if sent_by == self.user1.email:
            my_stats = self.user1_stats
            their_stats = self.user2_stats
        else:
            my_stats = self.user2_stats
            their_stats = self.user1_stats

        my_stats.total_lines += 1

        if has_laugh(text):
            their_stats.laugh_lines += 1

        if has_kissy(text):
            # If I send a kissy message, it gets recorded in her stats
            their_stats.kissy_lines += 1

        if django.utils.timezone.now() - self.start_date > datetime.timedelta(hours=24):
            my_stats.span_detected = True

        my_stats.save()
        their_stats.save()        
        self.save()

    def evaluate_status(self):
        """
        Look at the relatinship status, and determine what level they are at.
        Returned is a integer representing values in RELATIONSHIP_STATUSES
        """
        if self.status >= 4 and self.have_met:
            return 5 # irl friends

        both_like = self.user1_stats.like and self.user2_stats.like
        if self.status >= 3 and both_line:
            return 4 # more than friends

        both_span_detected = self.user1_stats.span_detected and self.user2_stats.span_detected
        if self.status >= 2 and both_span_detected:
            return 3 # friends

        both_ten_lines = self.user1_stats.total_lines > 10 and self.user2_stats.total_lines > 10
        if self.status >= 1 and both_ten_lines:
            return 2 # acquaintance

        if self.user1_stats.total_lines >= 1 and self.user2_stats.total_lines >= 1:
            return 1 # contact
        
        return 0

    def get_changes(self):
        """
        After each message has been processed, call this function to get any
        changes to the relationship so we can notify the user.
        """
        sender = sent_to = both = {}
        
        new_status = self.evaluate_status()
        if new_status != self.status:
            self.status = new_status
            self.increase_rep(new_status=new_status)
            self.save()
            both = {'type': 'event', 'new_status': self.get_status_display()}

        return sender, sent_to, both

    def increase_rep(self, new_status=None):
        """
        This function handles increasing the users rep after certain events
        """
        increase = 0
        if new_status:
            if new_status == 1:
                # got a response
                increase = 1
            elif new_status == 2:
                # ten chat messages exchanged
                increase = 20
            elif new_status == 3:
                # bridged the 24 hour gap.
                increase = 50
            elif new_status == 4:
                # met IRL
                increase = 100

        self.user1.reputation += increase
        self.user2.reputation += increase
        self.user1.save()
        self.user2.save()