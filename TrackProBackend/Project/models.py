from django.db import models
from Users.models import Users
from CompanyMaster.models import companyinfo

class ProjectMaster(models.Model):
    ProjectName = models.CharField(max_length=150, null=True, blank=True)
    ProjectDescription = models.TextField(null=True, blank=True)
    ProjectBA = models.ForeignKey('Users.Users', on_delete=models.CASCADE, related_name='projectBA', blank=True)
    ProjectCoordinator = models.ManyToManyField(Users, blank=True)
    Active = models.BooleanField(default=True,null=True, blank=True)
    CreatedBy = models.ForeignKey('Users.Users', on_delete=models.SET_NULL,related_name='projectCreatedBy',null=True, blank=True)
    CreatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    UpdatedBy = models.ForeignKey('Users.Users', on_delete=models.SET_NULL, related_name='projectUpdatedBy',null=True, blank=True)
    UpdatedOn = models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return self.ProjectName