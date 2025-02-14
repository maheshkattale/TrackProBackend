
from django.db import models
from Users.models import Users
from CompanyMaster.models import companyinfo

class IntermediateTrackProResult(models.Model):
    Employee = models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True, related_name='Employee')  
    EmpID = models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True, related_name='EmployeeID') 
    Week = models.IntegerField(null=True,blank=True)
    Year = models.IntegerField(null=True,blank=True)
    TotalTask = models.IntegerField(blank=True, null=True)
    Green = models.IntegerField(blank=True, null=True)
    Yellow = models.IntegerField(blank=True, null=True)
    Red = models.IntegerField(blank=True, null=True)
    Bonus = models.IntegerField(blank=True, null=True)
    Cancelled = models.IntegerField(blank=True, null=True)
    Rejected = models.IntegerField(blank=True, null=True)
    NotDone = models.IntegerField(blank=True, null=True)
    Help = models.IntegerField(blank=True, null=True)
    TrackProScore = models.IntegerField(blank=True, null=True)
    TotalScore = models.IntegerField(blank=True, null=True)
    TrackProPercent = models.FloatField(blank=True, null=True)
    CreatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='intermediatetrackproresultcreatedby',null=True, blank=True)
    Rank = models.IntegerField(null=True,blank=True )
    DepartmentwiseRank = models.IntegerField(null=True,blank=True )
    company_code = models.CharField(max_length=50,null=True,blank=True)
    extra_credit = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return str(self.Employee)
