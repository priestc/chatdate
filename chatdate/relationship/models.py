import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import django.utils.timezone

def has_laugh(text):
    return "hehe" in text or "haha" in text or "lol" in text

def has_kissy(text):
    return ":*" in text or ";-*" in text or ":-*" in text or "<3" in text

RELATIONSHIP_STATUSES = (
    (0, "You don't exist"),
    (1, 'Contact'),
    (2, 'Acquaintance'),
    (3, 'Friends'),
    (4, 'IRL Friends'),
)

class RelationshipStats(models.Model):
    """
    Represents stats for a user in a relationship.
    `span_detected` gets flipped to True after a mesage has been sent more than
    24 hours apart. These represent the things Ive done in the relatinship.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="stats")
    im_a_long_distance_partner = models.BooleanField(default=False)
    im_a_high_karma_partner = models.BooleanField(default=False)
    my_laugh_lines = models.IntegerField(default=0)
    i_like_her = models.BooleanField(default=False)
    my_kissy_lines = models.IntegerField(default=0)
    my_total_lines = models.IntegerField(default=0)
    my_span_detected = models.BooleanField(default=False)
    i_gave_away_rl_name = models.BooleanField()
    i_gave_away_pictures = models.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.id, self.user.nickname)

class RelationshipManager(models.Manager):
    def my_relationships(self, user):
        return self.filter(models.Q(user1=user) | models.Q(user2=user))

    def get_or_make_relationship(self, hash1, hash2):
        """
        Make a relationship object from two users, if one doesnt alreasy exist.
        """
        hashes = sorted([hash1, hash2])
        try:
            return Relationship.objects.get(user1__hash=hashes[0], user2__hash=hashes[1])
        except Relationship.DoesNotExist:
            User = get_user_model()
            user1 = User.objects.get(hash=hashes[0])
            user2 = User.objects.get(hash=hashes[1])
            stat1 = RelationshipStats.objects.create(user=user1)
            stat2 = RelationshipStats.objects.create(user=user2)
            return Relationship.objects.create(
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

    def to_json(self, perspective):
        """
        Return a json serializable object that represents the relationship
        from the passed in user's perspective.
        """
        perspective_stats = self.user2_stats
        other_stats = self.user1_stats
        other_person = self.user1
        if perspective == self.user1:
            perspective_stats = self.user1_stats
            other_stats = self.user2_stats
            other_person = self.user2

        if other_stats.i_gave_away_rl_name:
            name = other_person.full_name
        else:
            name = other_person.nickname

        ret = {
            'id': self.pk,
            'start_date': self.start_date.strftime("%B %d, %Y"),
            'status': self.get_status_display(),
            'met': self.met,
            'name': name,
            'gender': other_person.gender,
            'pictures': other_person.pics if other_stats.i_gave_away_pictures else []
        }

        return ret

    def process_message(self, text, sent_by):
        """
        When two people in a relationship speak to each other, the text goes
        through this function to keep track of the stages. `message` can be
        sent by either person in the relationship.
        """
        if sent_by == self.user1.hash:
            my_stats = self.user1_stats
            their_stats = self.user2_stats
        else:
            my_stats = self.user2_stats
            their_stats = self.user1_stats

        my_stats.my_total_lines += 1

        if has_laugh(text):
            their_stats.my_laugh_lines += 1

        if has_kissy(text):
            # If I send a kissy message, it gets recorded in her stats
            their_stats.kissy_lines += 1

        if django.utils.timezone.now() - self.start_date > datetime.timedelta(hours=24):
            my_stats.my_span_detected = True

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

        both_like = self.user1_stats.i_like_her and self.user2_stats.i_like_her
        if self.status >= 3 and both_like:
            return 4 # more than friends

        both_span_detected = self.user1_stats.my_span_detected and self.user2_stats.my_span_detected
        if self.status >= 2 and both_span_detected:
            return 3 # friends

        both_ten_lines = self.user1_stats.my_total_lines >= 10 and self.user2_stats.my_total_lines >= 10
        if self.status >= 1 and both_ten_lines:
            return 2 # acquaintance

        if self.user1_stats.my_total_lines >= 1 and self.user2_stats.my_total_lines >= 1:
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
            increased = self.increase_rep(new_status=new_status)
            self.save()
            both = {
                'event': {
                    'relationship_status': self.get_status_display(),
                    'rep_increase': increased,
                }
            }

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
        return increase