from django.utils import tree
from django.db import models
from django.db import models
from Users.models import Users
from django.utils import  timezone
from CompanyMaster.models import companyinfo

import datetime

# Create your models here.

class PacketMaster(models.Model):
    PacketName = models.CharField(max_length=255,null=True,blank=True)
    is_active = models.BooleanField(default=True)

    company_code = models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.PacketName


class PacketEmployeeMapping(models.Model):
    PacketId = models.CharField(max_length=255,null=True,blank=True)
    EmployeeId = models.CharField(max_length=255,null=True,blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)
    is_active = models.BooleanField(default=True)

class PacketLeaveRules(models.Model):
    PacketId = models.CharField(max_length=255,null=True,blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)
    LeaveTypeId = models.CharField(max_length=255,null=True,blank=True)
    
    #Rule 1
    Rule1 = models.BooleanField(default=False)
    LeaveCount = models.CharField(max_length=255,null=True,blank=True)
    LeaveCarryForwardCount = models.CharField(max_length=255,null=True,blank=True)
    
    
    #Rule 2
    Rule2 = models.BooleanField(default=False)
    ApplicableEmployements = models.CharField(max_length=255,null=True,blank=True)# 0 for all
    

    #Rule 3
    Rule3 = models.BooleanField(default=False)
    WPOLHoliday = models.BooleanField(default=False,null=True, blank=True,)# within the period of leave
    PSHoliday = models.BooleanField(default=False,null=True, blank=True,) #Preceding / Succeeding 
    HAtLeastNoDays = models.CharField(max_length=255,null=True,blank=True)
    WPOLWeeklyOff = models.BooleanField(default=False,null=True, blank=True,)# within the period of leave
    PSWeeklyOff = models.BooleanField(default=False,null=True, blank=True,) #Preceding / Succeeding 
    WOAtLeastNoDays = models.CharField(max_length=255,null=True,blank=True)



    #Rule 4
    Rule4 = models.BooleanField(default=False)
    ApprovalLevels = models.CharField(max_length=255,null=True,blank=True)
    RejectionLevels = models.CharField(default='1',max_length=255,null=True,blank=True)
    IfNoAction = models.CharField(max_length=255,null=True,blank=True)#Approve/Reject
    IfNoActionBefore = models.CharField(max_length=255,null=True,blank=True)#No of days
    IfNoActionFrom = models.CharField(max_length=255,null=True,blank=True)#leave application date/leave start date
    
    
    #Rule 5
    Rule5 = models.BooleanField(default=False)
    ApplyUptoFuture = models.CharField(max_length=255,null=True,blank=True)#No of days

    #Rule 6
    Rule6 = models.BooleanField(default=False)
    ApplyUptoPast = models.CharField(max_length=255,null=True,blank=True)#No of days

    #Rule 7
    Rule7 = models.BooleanField(default=False)
    ApplyBefore = models.CharField(max_length=255,null=True,blank=True)#No of days

    #Rule 8
    Rule8 = models.BooleanField(default=False)
    LeaveLongerThan = models.CharField(max_length=255,null=True,blank=True)#No of consecutive days
    AttachmentRequired = models.BooleanField(default=False,null=True, blank=True,)

    #Rule 9
    Rule9 = models.BooleanField(default=False)
    WeeklyOffConsider = models.CharField(max_length=255,null=True,blank=True)#5/6
    IfWeeklyOff6 = models.BooleanField(default=False,null=True, blank=True,)
    WeeklyOffPattern = models.CharField(max_length=255,null=True,blank=True)#even/Odd
    
    #Rule 10
    Rule10 = models.BooleanField(default=False)
    ProRatedCalculation = models.CharField(max_length=255,null=True,blank=True)#date of joining /date of confirmation
    
    #Rule 11
    Rule11 = models.BooleanField(default=False)
    AutoEncashmentBeyond = models.CharField(max_length=255,null=True,blank=True)

    #Rule 12
    Rule12 = models.BooleanField(default=False)
    EncashmentType = models.CharField(max_length=255,null=True,blank=True)#partial/fully
    EncashmentApplyCount = models.CharField(max_length=255,null=True,blank=True)#in year
    MinEncashmentDays = models.CharField(max_length=255,null=True,blank=True)
    MaxEncashmentDays = models.CharField(max_length=255,null=True,blank=True)

    is_active = models.BooleanField(default=True)


