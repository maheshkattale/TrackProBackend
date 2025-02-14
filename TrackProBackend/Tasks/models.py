from django.utils import tree
from Project.models import ProjectMaster
from django.db import models
from django.db import models
from Users.models import Users
from django.utils import  timezone
from CompanyMaster.models import companyinfo

import datetime
my_date = datetime.date.today()
year, week_num, day_of_week = my_date.isocalendar()
week = week_num
year_num = year
day = day_of_week

class Status(models.Model):
    StatusName = models.CharField(max_length=25) #Pending, completed, reopen
    company_code = models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.StatusName
 
class TaskPriorityMaster(models.Model):
    PriorityName = models.CharField(max_length= 25) #high, medium, low
    company_code = models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.PriorityName

class Zone(models.Model):
    ZoneName = models.CharField(max_length=25)
    company_code = models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.ZoneName
    

class TaskMaster(models.Model):
    LoggedUser = models.ForeignKey(Users,on_delete=models.CASCADE, blank=True, null=True ,related_name='loggeduser')
    AssignTo = models.ForeignKey(Users,on_delete=models.CASCADE, blank=True, null=True ,related_name='taskassignto')
    AssignBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='taskassignby', null=True, blank=True)
    AssignByStr = models.CharField(max_length=100, null=True, blank=True)
    AssignDate = models.DateField(null=True, blank=True)
    Status = models.ForeignKey(Status, on_delete=models.CASCADE,default=1, null=True, blank=True)
    Day = models.CharField(default=day,max_length=10, null=True, blank=True)
    Week = models.IntegerField(default=week, null=True)
    Year = models.IntegerField(default=year_num, null=True,blank=True)
    Project = models.ForeignKey(ProjectMaster, on_delete=models.CASCADE, related_name='project_id', null=True, blank=True)   
    ProjectName = models.CharField(max_length=1000,null=True, blank=True)   
    TaskTitle = models.TextField(max_length=1000)   
    TaskDescription = models.CharField(max_length=500, null=True)
    Zone = models.ForeignKey(Zone,on_delete=models.CASCADE, null=True, blank=True)
    Bonus = models.BooleanField(default=False)
    HelpTaken = models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True,related_name='helptaken')
    DueDateTime = models.DateField( null=True)
    TaskPriority = models.ForeignKey(TaskPriorityMaster, on_delete=models.CASCADE,null=True, blank=True)   
    Active = models.BooleanField(default=True)
    CheckedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='taskcheckedby',null=True, blank=True)
    ReCheckedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='taskrecheckedby',null=True, blank=True)
    CreatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='taskcreatedby',null=True, blank=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='taskupdatedby', null=True, blank=True)
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True,blank=True)
    AddedByManager = models.BooleanField(default=False)
    ParentTaskId = models.IntegerField(null=True, blank=True)
    IsParent = models.BooleanField(default=False)

    
    def __str__(self):
        return self.TaskTitle
 

 
class ProjectTasks(models.Model):
    Task = models.ForeignKey(TaskMaster, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    StartDate = models.DateTimeField(default=timezone.now,null=True,blank=True)
    EndDate = models.DateTimeField(null=True, blank=True)
    ParentTask = models.ForeignKey(TaskMaster, on_delete=models.CASCADE, null=True, blank=True, related_name='parent_task')
    company_code = models.CharField(max_length=50,null=True,blank=True)

class NotificationTypeMaster(models.Model):
    Type = models.CharField(max_length=50)   #InApp, Firebase, SMS
    company_code = models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.Type
 
class TaskNotification(models.Model):
    NotificationTitle = models.CharField(max_length=51)   
    NotificationMsg= models.CharField(max_length=500, null=True)
    UserID = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='idUser', null=True, blank=True)
    ReadMsg = models.BooleanField(default=False)
    NotificationTypeId = models.ForeignKey(NotificationTypeMaster, on_delete=models.CASCADE)
    created_by = models.BigIntegerField(null=True,blank=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    company_code = models.CharField(max_length=50,null=True,blank=True)
    leaveID = models.IntegerField(null=True, blank=True,default=0)
    To_manager = models.BooleanField(default=False,null=True, blank=True)
    action_Taken =  models.BooleanField(default=False,null=True, blank=True)




    



class TaskRemark(models.Model):
    created_by = models.BigIntegerField(null=True,blank=True)
    created_by_str = models.CharField(max_length=500, null=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    ismanager = models.BooleanField(default=False)
    remark_comment = models.TextField()
    user_id = models.BigIntegerField()
    user_str = models.CharField(max_length=500, null=True)
    task_id = models.BigIntegerField(null=True)
    Active = models.BooleanField(default=True)
    IsRead = models.BooleanField(default=False)


    
 
