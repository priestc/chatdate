import datetime
import hashlib
from dateutil import parser

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.gis.db import models
from django.contrib.gis.measure import D
import django.utils.timezone

SEXUAL_PEFERENCES = ((1, 'Heterosexual'), (2, 'Homosexual'), (3, 'Bisexual'))

class Picture(models.Model):
    caption = models.CharField(max_length=256)
    url = models.URLField()

class UserManager(models.GeoManager, BaseUserManager):
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


class User(AbstractBaseUser, PermissionsMixin, models.Model):
    gender = models.CharField("Your Gender", max_length=1, choices=(('M', "Male"), ("F", "Female")), default='M')
    transgendered = models.BooleanField("Transgendered?", default=False)
    sexual_preference = models.IntegerField("Your Sexual Orientation", choices=SEXUAL_PEFERENCES, default=1)
    nickname = models.CharField(max_length=25, help_text="Max 25 characters. Does not need to be unique.")
    full_name = models.TextField("Real Name", help_text="Only shown to those you choose.")
    email = models.EmailField(db_index=True, unique=True)
    relationships = models.ManyToManyField('self', through="relationship.Relationship", symmetrical=False)
    dob = models.DateField("Date of Birth", help_text="Format: YYYY-MM-DD")
    status = models.CharField(max_length=140)
    reputation = models.IntegerField(default=0)
    hash = models.CharField(max_length=32, db_index=True)
    location = models.PointField(help_text="Click and drag the marker to where you are located. Your exact coordinates will never be revealed to anyone.")
    specific_location = models.CharField("Location Description", help_text="You can be as spefific or vague as you wish. Example: Chelsea, Kentucky, South Miami.", max_length=50, blank=True)
    connection_distance = models.IntegerField(default=15, help_text="Users further than this amount of miles away from you will be ignored.")
    karma_threshold = models.IntegerField(default=0, help_text="Users with less karma than this value will be ignored")
    pics = models.ManyToManyField(Picture)

    show_straight_males = models.BooleanField(default=False)
    show_gay_males = models.BooleanField(default=False)
    show_bisexual_males = models.BooleanField(default=False)
    show_gay_females = models.BooleanField(default=False)
    show_straight_females = models.BooleanField(default=False)
    show_bisexual_females = models.BooleanField(default=False)

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

    def to_json(self):
        return {
            'nickname': self.nickname,
            'age': self.age(),
            'reputation': self.reputation,
            'hash': self.hash,
            'location': self.specific_location,
            'status': self.status,
            'gender': self.gender,
            'sexual_preference': self.sexual_preference
        } 

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return True if self.is_superuser else False

    def get_short_name(self):
        return self.nickname

    def is_authenticated(self):
        return True

    def set_default_prefs(self):
        """
        When a user first signs up, set their hiding preferences up based on their
        declared sexual preferences and gender.
        """
        if self.gender == 'M':
            self.show_gay_females = False
            self.show_straight_males = False
            
            if self.sexual_preference == 3: # bisexual male
                self.show_straight_females = True
                self.show_gay_males = True
                self.show_bisexual_females = True
                self.show_bisexual_males = True
            elif self.sexual_preference == 2: # gay male
                self.show_straight_females = False
                self.show_gay_males = True
                self.show_bisexual_females = False
                self.show_bisexual_males = True
            elif self.sexual_preference == 1: # straight male
                self.show_straight_females = True
                self.show_gay_males = False
                self.show_bisexual_females = True
                self.show_bisexual_males = False
        else: # a female
            self.show_gay_males = False
            self.show_straight_females = False
            
            if self.sexual_preference == 3: # bisexual female
                self.show_straight_males = True
                self.show_gay_females = True
                self.show_bisexual_females = True
                self.show_bisexual_males = True
            elif self.sexual_preference == 2: # gay female
                self.show_straight_males = False
                self.show_gay_females = True
                self.show_bisexual_females = True
                self.show_bisexual_males = False
            elif self.sexual_preference == 1: # straight female
                self.show_straight_males = True
                self.show_gay_females = False
                self.show_bisexual_females = False
                self.show_bisexual_males = True


    def apply_preference_excludes(self, qs):
        """
        Exclude users from a User queryset based on this user's hiding preferences.
        """
        if not self.show_gay_females:
            qs = qs.exclude(gender='F', sexual_preference=2)
        if not self.show_straight_males:
            qs = qs.exclude(gender='M', sexual_preference=1)
        if not self.show_straight_females:
            qs = qs.exclude(gender='F', sexual_preference=1)
        if not self.show_gay_males:
            qs = qs.exclude(gender='M', sexual_preference=2)
        if not self.show_bisexual_females:
            qs = qs.exclude(gender='F', sexual_preference=3)
        if not self.show_bisexual_males:
            qs = qs.exclude(gender='M', sexual_preference=3)

        return qs

    def cares_about(self, user):
        """
        Does this user care about chatting with the passed in user?
        """
        if user.gender == 'F':
            if user.sexual_preference == 1:
                return self.show_straight_females
            if user.sexual_preference == 2:
                return self.show_gay_females
            if user.sexual_preference == 3:
                return self.show_bisexual_females
        else:
            if user.sexual_preference == 1:
                return self.show_straight_males
            if user.sexual_preference == 2:
                return self.show_gay_males
            if user.sexual_preference == 3:
                return self.show_bisexual_males

    def save(self, *a, **k):
        if not self.hash:
            self.hash = hashlib.md5(self.email + settings.SECRET_KEY).hexdigest()

        hide_all = all([
            not self.show_straight_females, not self.show_gay_males,
            not self.show_gay_females, not self.show_straight_males,
            not self.show_bisexual_males, not self.show_bisexual_females
        ])

        if hide_all:
            # this should only happen when first signing up.
            self.set_default_prefs()

        super(User, self).save(*a, **k)

    def __unicode__(self):
        return "%s %s" % (self.get_sexual_preference_display(), self.get_gender_display())

    def local_users(self, online=False):
        """
        Return all users within my matching diatance preference.
        """
        #return User.objects.all()
        tup = (self.location, D(mi=9000)) #self.connection_distance))
        # .exclude(location__distance_lt=(self.location, models.F('connection_distance')))
        nearby = User.objects.filter(location__distance_lt=tup).exclude(id=self.id)

        nearby = self.apply_preference_excludes(nearby)

        if online:
            return nearby.filter(readytochat__isnull=False)
        else:
            return nearby