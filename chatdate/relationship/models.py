import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import django.utils.timezone
from badges import BADGES

def has_laugh(text):
    return "hehe" in text or "haha" in text or "lol" in text

def has_kissy(text):
    return ":*" in text or ";-*" in text or ":-*" in text or "<3" in text

class RelationshipBadge(models.Model):
    """
    Represents an achievement between two people in a relationship.
    """
    relationship = models.ForeignKey('Relationship')
    name = models.CharField(max_length=32)
    time_awarded = models.DateTimeField(auto_now_add=True)

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
    blocked = models.BooleanField(default=False)

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
    met = models.BooleanField(default=False)

    objects = RelationshipManager()

    @property
    def blocked(self):
        return self.user1_stats.blocked or self.user2_stats.blocked

    def __unicode__(self):
        return "%s + %s (%s)" % (self.user1.nickname, self.user2.nickname, self.get_status_display())

    def award_badge(self, badge):
        """
        Create the row in the RelationshipBadge table recording this badge,
        and increate each user's karma.
        """
        RelationshipBadge.objects.create(relationship=self, name=badge.name)
        self.user1.reputation += badge.karma_award
        self.user2.reputation += badge.karma_award
        self.user1.save()
        self.user2.save()

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
            'met': self.met,
            'name': name,
            'gender': other_person.gender,
            'pictures': other_person.pics if other_stats.i_gave_away_pictures else []
        }

        return ret

    def record_like(self, sent_by_hash):
        person_who_sent_like = self.user1_stats
        if self.user1.hash == sent_by_hash:
            person_who_sent_like = self.user2_stats

        if not person_who_sent_like.i_like_her:
            person_who_sent_like.i_like_her = True
            person_who_sent_like.save()
            return True
        return False

    def record_block(self, sent_by_hash):
        person_who_sent_block = self.user1_stats
        if self.user1.hash == sent_by_hash:
            person_who_sent_block = self.user2_stats

        if not person_who_sent_block.blocked:
            person_who_sent_block.blocked = True
            person_who_sent_block.save()
            return True
        return False


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

    def get_changes(self):
        """
        After each message has been processed, call this function to get any
        changes to the relationship so we can notify the user.
        """
        sender = sent_to = both = []
        for badge in BADGES:
            if badge.eligible(self):
                self.award_badge(badge)
                both.append({
                    'event': {
                        'new_badge': badge.name,
                        'rep_increase': badge.karma_award,
                    }
                })
        return sender, sent_to, both