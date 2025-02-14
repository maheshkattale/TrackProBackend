from django.db import models

# Create your models here.
class Shiftswap(models.Model):
    employeeId =  models.CharField(max_length=150, null=True)
    AttendanceId = models.CharField(max_length=100, null=True)
    Shiftdate =  models.DateField(null=True)
    ShiftId = models.IntegerField(null=True)
    Shiftname =  models.CharField(max_length=50, null=True)
    Reason = models.TextField(null=True,blank=True)
    SwapempId =  models.CharField(max_length=100, null=True)
    Swapshiftdate = models.DateField(null=True)
    SwapShiftId =  models.IntegerField(null=True)
    Swapshiftname = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    Status =  models.CharField(max_length=100, null=True)
    created_by =  models.CharField(max_length=10, null=True)
    Active = models.BooleanField(default=True)


class ShiftswapAction(models.Model):
    RequestId = models.IntegerField(null=True)
    ActionTaken = models.CharField(max_length=50, null=True,default="Pending") #Pending Approved Rejected
    ManagerId = models.CharField(max_length=100, null=True)
    RejectionReason = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    updated_by =  models.CharField(max_length=10, null=True)
    Active = models.BooleanField(default=True)

class shiftmanagers(models.Model):
    employeeId =  models.CharField(max_length=150, null=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    created_by =  models.CharField(max_length=10, null=True)
    Active = models.BooleanField(default=True)
