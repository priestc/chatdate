from django.contrib.gis.db import models

class Zipcode(models.Model):
    zipcode = models.CharField(max_length=5)
    state = models.CharField(max_length=2)
    fips_regions = models.CharField(max_length=2)
    city = models.CharField(max_length=64)
    location = models.PointField()

    objects = models.GeoManager()