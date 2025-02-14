from django.utils import tree
from django.db import models
from django.db import models
from Users.models import Users
from django.utils import  timezone
from CompanyMaster.models import companyinfo

import datetime


class LeaveTypeMaster(models.Model):
    TypeName = models.CharField(max_length=255,null=True,blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.TypeName
    
class CarryForwardedLeave(models.Model):
    EmployeeId = models.CharField(max_length=255,null=True,blank=True)
    LeaveTypeId = models.CharField(max_length=255,null=True,blank=True)
    Year = models.CharField(max_length=255,null=True,blank=True)
    LeaveCount = models.CharField(max_length=255,null=True,blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True)










