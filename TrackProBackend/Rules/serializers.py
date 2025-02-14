from Tasks.models import ProjectTasks
from Users.models import Users
from rest_framework import serializers
from .models import *



class leaveruleserializer(serializers.ModelSerializer):
  
    class Meta:
        model = Leaverule
        fields ='__all__'

class attendanceruleserializer(serializers.ModelSerializer):
  
    class Meta:
        model = Attendancerule
        fields ='__all__'


class trackproruleserializer(serializers.ModelSerializer):
  
    class Meta:
        model = rulestrackpro
        fields ='__all__'

class annoucementserializer(serializers.ModelSerializer):
  
    class Meta:
        model = AnnounceMent
        fields ='__all__'

class Newsserializer(serializers.ModelSerializer):
  
    class Meta:
        model = NewsMaster
        fields ='__all__'
