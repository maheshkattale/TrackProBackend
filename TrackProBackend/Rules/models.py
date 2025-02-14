from django.db import models

# Create your models here.
class Leaverule(models.Model):
    Periodof_L = models.CharField(max_length=50,null=True, blank=True)
    Assignedleaves = models.IntegerField(null=True, blank=True)
    maxleaves = models.IntegerField(null=True, blank=True)
    lapsestatus = models.CharField(max_length=50)
    carryforward = models.FloatField(max_length=50,null=True, blank=True)
    encashment = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True,null=True)
    CreatedBy = models.CharField(max_length=50,null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)



class Attendancerule(models.Model):
    Fulldayhrs = models.CharField(max_length=50,null=True,blank=True)
    Halfdayhrs =  models.CharField(max_length=50,null=True,blank=True)
    In_timehrs =  models.CharField(max_length=50,null=True,blank=True)
    time_extension =  models.CharField(max_length=50,null=True,blank=True)
    leverages =  models.IntegerField(null=True,blank=True)
    is_active = models.BooleanField(default=True,null=True)
    CreatedBy = models.CharField(max_length=50,null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)

class rulestrackpro(models.Model):
    color =  models.CharField(max_length=50,null=True,blank=True)
    points =  models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True,null=True)
    CreatedBy = models.CharField(max_length=50,null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)

class AnnounceMent(models.Model):
    announcementText = models.TextField(default=True,null=True)
    date = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    CreatedBy = models.CharField(max_length=50,null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)

class NewsMaster(models.Model):
    newsText = models.TextField(default=True,null=True)
    date = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    CreatedBy = models.CharField(max_length=50,null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)