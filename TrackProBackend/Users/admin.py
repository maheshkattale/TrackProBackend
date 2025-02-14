from django.contrib import admin

# Register your models here.
from .models import Designation, Role, Users, ErrorLog, UserToManager, Location, FinancialYear , Permissions, MenuItem
from Tasks.models import Status, TaskPriorityMaster, TaskMaster, NotificationTypeMaster, TaskNotification
from Department.models import Department

admin.site.register(Department)
admin.site.register( Designation)
admin.site.register(Role)
admin.site.register(Location)
admin.site.register(FinancialYear)
admin.site.register(Users)
admin.site.register( ErrorLog)
# admin.site.register( Permissions)
# admin.site.register(MenuItem)
# admin.site.register(LevelMaster)
admin.site.register( UserToManager)
admin.site.register(Status)
admin.site.register(TaskPriorityMaster)
admin.site.register(TaskMaster)
admin.site.register(NotificationTypeMaster)
admin.site.register(TaskNotification)