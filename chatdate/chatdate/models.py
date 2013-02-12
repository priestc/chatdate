from dateutil import parser

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

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
            Relationship.objects.create(user1=user1, user2=user2)

class Relationship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user1")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user2")

    objects = RelationshipManager()

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    blocked = models.BooleanField(default=False)
    score = models.IntegerField(default=1)

    def __unicode__(self):
        return "%s + %s" % (self.user1.nickname, self.user2.nickname)

SEXUAL_PEFERENCES = ((1, 'heterosexual'), (2, 'homosexual'), (3, 'bisexual'))

class UserManager(BaseUserManager):
    def create_user(self, email, dob, nickname, full_name, password=None):
        dob = parser.parse(dob)
        u = self.create(email=email, dob=dob, nickname=nickname, full_name=full_name)
        u.set_password(password)
        u.save()
        return u

    def create_superuser(self, email, dob, nickname, full_name, password):
        u = self.create_user(email, dob, nickname, full_name, password)
        u.is_superuser = True
        u.save()
        return u


class User(AbstractBaseUser, PermissionsMixin):
    gender = models.CharField(max_length=1, choices=(('M', "Male"), ("F", "Female")), default='M')
    transgendered = models.BooleanField(default=False)
    sexual_preference = models.IntegerField(choices=SEXUAL_PEFERENCES, default=1)

    nickname = models.CharField(max_length=25)
    full_name = models.TextField()
    email = models.EmailField(db_index=True, unique=True)
    zipcode = models.CharField(max_length=5)
    specific_location = models.CharField(max_length=50, blank=True)

    relationships = models.ManyToManyField('self', through=Relationship, symmetrical=False)

    dob = models.DateField("Date of Birth")
    status = models.CharField(max_length=140)
    reputation = models.IntegerField(default=0)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dob', 'nickname', 'full_name']

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return True if self.is_superuser else False

    def get_short_name(self):
        return self.nickname

