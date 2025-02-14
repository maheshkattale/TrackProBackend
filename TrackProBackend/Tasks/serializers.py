from rest_framework import serializers
from .models import TaskMaster, Zone,NotificationTypeMaster,TaskNotification,ProjectTasks,TaskRemark
from Users.models import Users
from rest_framework import serializers

class GetTaskSerializer(serializers.ModelSerializer):
    class Meta:
      model=TaskMaster
      fields="__all__"

class GetTaskScoreSerializer(serializers.ModelSerializer):
    class Meta:
      model=TaskMaster
      fields=['id','Active','Status_id','AssignTo','AssignBy','AssignDate','Week','Year','Bonus','Zone']

class GetuserTaskdataSerializer(serializers.ModelSerializer):
    class Meta:
      model=TaskMaster
      fields=['id','Active','ProjectName','TaskTitle','AssignDate']

class GetTaskMasterSerializer(serializers.ModelSerializer):
    AssignBy = serializers.StringRelatedField()
    Status = serializers.StringRelatedField()
    TaskPriority = serializers.StringRelatedField()
    CreatedBy = serializers.StringRelatedField()
    UpdatedBy = serializers.StringRelatedField()
    
    # AssignTo = serializers.StringRelatedField()
    class Meta:
        model = TaskMaster
        fields = "__all__"


class GetPendingTaskMasterSerializer(serializers.ModelSerializer):
    AssignBy = serializers.StringRelatedField()
    TaskPriority = serializers.StringRelatedField()
    CreatedBy = serializers.StringRelatedField()
    UpdatedBy = serializers.StringRelatedField()
    
    # AssignTo = serializers.StringRelatedField()
    class Meta:
        model = TaskMaster
        fields = "__all__"


class GetTaskMasterProjectTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = ['id','Project','ProjectName']


class SearchTaskMasterSerializer(serializers.ModelSerializer):
    Status = serializers.StringRelatedField()
    TaskPriority = serializers.StringRelatedField()
    CreatedBy = serializers.StringRelatedField()
    UpdatedBy = serializers.StringRelatedField()
    
    # AssignTo = serializers.StringRelatedField()
    class Meta:
        model = TaskMaster
        fields = "__all__"


class PostTaskMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = "__all__"

class PostTaskMasterSerializerStatus(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = ['Active','Status_id']

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = "__all__"

class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = ['Year']
 
class WeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = ['Week']
class YearWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = ['Year','Week']
class TaskMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMaster
        fields = ['Year','Week','AssignBy','AssignByStr']

class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTypeMaster
        fields = "__all__"

class TaskNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskNotification
        fields = "__all__"


class ProjectTasksSerializer(serializers.ModelSerializer):
    class Meta:
      model= ProjectTasks
      fields="__all__"

class TaskRemarkSerializer(serializers.ModelSerializer):
    class Meta:
      model= TaskRemark
      fields="__all__"