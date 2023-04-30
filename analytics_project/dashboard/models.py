from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class RealEstateInfoScrape(models.Model):
    # id = models.IntegerField(primary_key=True) # redundant
    padctn_id = models.IntegerField(blank=True, null=True)
    map_parcel = models.CharField(max_length=200, blank=True, null=True)
    mailing_address = models.CharField(max_length=200, blank=True, null=True)
    sale_date = models.CharField(max_length=200, blank=True, null=True)
    sale_price = models.DateField(blank=True, null=True)
    property_use = models.CharField(max_length=200, blank=True, null=True)
    zone = models.CharField(max_length=200, blank=True, null=True)
    neighborhood = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False # false = not managed by django (managed by me)
        db_table = 'real_estate_info_scrape'
