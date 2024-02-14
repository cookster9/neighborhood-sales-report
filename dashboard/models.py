from django.db import models
class Neighborhoods(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    visible = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'neighborhoods'


class TnDavidsonAddresses(models.Model):
    longitude = models.CharField(max_length=200, db_column='Longitude', blank=True, null=True)  # Field name made lowercase.
    latitude = models.CharField(max_length=200, db_column='Latitude', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tn_davidson_addresses'


class RealEstateProperties(models.Model):
    id = models.IntegerField(primary_key=True)
    padctn_id = models.IntegerField(unique=True, blank=True, null=True)
    map_parcel = models.CharField(max_length=200, blank=True, null=True)
    map_parcel_trimmed = models.CharField(max_length=200, blank=True, null=True)
    mailing_address = models.CharField(max_length=200, blank=True, null=True)
    property_use = models.CharField(max_length=200, blank=True, null=True)
    zone = models.CharField(max_length=200, blank=True, null=True)
    neighborhoods = models.ForeignKey(Neighborhoods, models.DO_NOTHING, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    tn_davidson_addresses = models.ForeignKey('TnDavidsonAddresses', models.DO_NOTHING, blank=True, null=True)
    neighborhood = models.IntegerField(blank=True, null=True)
    square_footage = models.CharField(max_length=50, blank=True, null=True)
    last_update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'real_estate_properties'


class RealEstateSales(models.Model):
    sale_date = models.DateField(blank=True, null=True)
    sale_price = models.CharField(max_length=50, db_collation='utf8_general_ci', blank=True, null=True)
    real_estate_properties = models.ForeignKey(RealEstateProperties, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'real_estate_sales'
