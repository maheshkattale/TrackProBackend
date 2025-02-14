from django.db import models
from Users.models import Users

# Create your models here.
class Client(models.Model):
    ClientName = models.CharField(max_length=100,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True) 
    company_code = models.CharField(max_length=100,null=True, blank=True)

class ClientsideManager(models.Model):
    ClientId = models.IntegerField(null=True, blank=True)
    ManagerName = models.CharField(max_length=100,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True) 
    company_code = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self):
        return str(self.ManagerName)

class CreateClient(models.Model):
    ClientId = models.IntegerField(null=True, blank=True)
    Team = models.ManyToManyField(Users,blank=True)
    Client_ManagerId = models.ManyToManyField(ClientsideManager,blank=True)
    SPOC_Person = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True) 
    company_code = models.CharField(max_length=100,null=True, blank=True)
    
class Event(models.Model):
    ClientId = models.IntegerField(null=True, blank=True)
    Project = models.IntegerField(null=True, blank=True)
    Assign_To = models.IntegerField(null=True, blank=True)
    Assign_By = models.IntegerField(null=True, blank=True)
    TaskDescription = models.TextField(null=True, blank=True)
    AddNote = models.TextField(null=True, blank=True)
    TaskValidation = models.IntegerField(null=True, blank=True)
    Bonus =  models.BooleanField(default=False)
    FilledBy = models.IntegerField(null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_by =  models.IntegerField(null=True, blank=True)


class Client_Project(models.Model):
    ClientId = models.IntegerField(null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    is_active = models.BooleanField(default=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True) 
    created_by = models.CharField(max_length=100,null=True, blank=True)
    updated_by =  models.CharField(max_length=100,null=True, blank=True)
    ProjectName = models.CharField(max_length=255,null=True, blank=True)

    def get_client(self):
        # Method to retrieve the associated Client instance
        try:
            return Client.objects.get(id=self.ClientId)
        except Client.DoesNotExist:
            return None