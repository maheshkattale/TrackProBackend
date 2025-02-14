from django.db import models

# Create your models here.

class companyinfo(models.Model):
    companyName = models.CharField(max_length=100, null=True)
    companylogos =  models.ImageField(upload_to='companyImages', blank=True, null=True,verbose_name='Company Photo')
    gstcertificate =  models.ImageField(upload_to='gstcertificate', blank=True, null=True,verbose_name='Company Gst certificate')
    companyAddress = models.TextField(max_length=254, null=True)
    companycode = models.CharField(max_length=100,null=True, blank=True)
    gstNumber = models.CharField(max_length=55,null=True, blank=True)
    adhaarNumber = models.CharField(max_length=55,null=True, blank=True)
    panNumber = models.CharField(max_length=55,null=True, blank=True)
    memberadmin = models.CharField(max_length=55,null=True, blank=True)
    payment = models.CharField(max_length=55,null=True, blank=True)
    period = models.CharField(max_length=155,null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    companyType = models.CharField(max_length=155,null=True, blank=True)
    expirydate = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=155,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    isactive = models.BooleanField(default=True)

class paymentslip(models.Model):
    userId = models.IntegerField()
    name = models.CharField(max_length=156)
    amount = models.FloatField()
    month = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    company_code = models.CharField(max_length=50,null=True,blank=True)

class BillingPeriod(models.Model):
    isActive = models.BooleanField(default=True)
    period = models.CharField(max_length=100,blank=True,null=True)
    duration = models.BigIntegerField(null=True,blank=True)
    amount = models.CharField(max_length=50,null=True,blank=True)

class CompanyType(models.Model):
    isActive =  models.BooleanField(default=True)
    companyType = models.CharField(max_length=100,blank=True,null=True)

class companypaymentlog(models.Model):
    companyId = models.IntegerField(blank=True,null=True)
    planperiod = models.CharField(max_length=156,null=True,blank=True)
    startdate = models.DateField(null=True,blank=True)
    expirydate = models.DateField(null=True,blank=True)
    payment = models.CharField(max_length=150,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    isActive = models.BooleanField(default=True)