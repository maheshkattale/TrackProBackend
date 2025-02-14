from Tasks.models import ProjectTasks,TaskMaster
from Users.models import Users
from rest_framework import serializers
from .models import ProjectMaster
from Project import models

class AllProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMaster
        fields = '__all__'



class ProjectSerializer(serializers.ModelSerializer):
    ProjectBA = serializers.StringRelatedField()
    ProjectCoordinator = serializers.StringRelatedField(many=True)
    CreatedBy = serializers.StringRelatedField()
    UpdatedBy = serializers.StringRelatedField()

    class Meta:
        model = ProjectMaster
        fields = ['id', 'ProjectName', 'ProjectBA', 'ProjectCoordinator',
                  'Active', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn','company_code']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMaster
        fields = ['id', 'ProjectName', 'ProjectBA', 'ProjectCoordinator',
                  'Active', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn','company_code']


class ProjectTasksUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTasks
        fields = ['id', 'StartDate', 'EndDate', 'ParentTask', 'Task','company_code']


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMaster
        fields = ['id', 'ProjectName']




class ProjectTaskSerializer(serializers.ModelSerializer):
    Used = serializers.SerializerMethodField()
    ProjectBA = serializers.StringRelatedField()
    ProjectCoordinator = serializers.StringRelatedField(many=True)
    CreatedBy = serializers.StringRelatedField()
    UpdatedBy = serializers.StringRelatedField()

    class Meta:
        model = ProjectMaster
        fields = ['id', 'ProjectName', 'ProjectBA', 'ProjectCoordinator',
                  'Active', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn','company_code','Used']

    def get_Used(self, project):
        tasks = TaskMaster.objects.filter(Project=project.id, Active=True).first()
        return tasks is not None