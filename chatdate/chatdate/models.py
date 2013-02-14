import datetime
import hashlib
from dateutil import parser

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import django.utils.timezone


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

    relationships = models.ManyToManyField('self', through="relationship.Relationship", symmetrical=False)

    dob = models.DateField("Date of Birth")
    status = models.CharField(max_length=140)
    reputation = models.IntegerField(default=0)

    unique_key = models.CharField(max_length=32, db_index=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dob', 'nickname', 'full_name']

    def age(self):
        today = datetime.date.today()
        born = self.dob
        try: 
            birthday = born.replace(year=today.year)
        except ValueError: # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, day=born.day-1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return True if self.is_superuser else False

    def get_short_name(self):
        return self.nickname

    def save(self, *a, **k):
        if not self.unique_key:
            self.unique_key = hashlib.md5(str(self.id) + settings.SECRET_KEY).hexdigest()
        super(User, self).save(*a, **k)

    def __unicode__(self):
        return "%s(%s)" % (self.full_name, self.reputation)

