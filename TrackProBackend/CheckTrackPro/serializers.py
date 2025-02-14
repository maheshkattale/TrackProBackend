from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import IntermediateTrackProResult
from Users.models import Users

class IntermediateGetTrackProResultSerializer(serializers.ModelSerializer):    
    Employee = serializers.StringRelatedField()
    class Meta:
        model = IntermediateTrackProResult
        fields = "__all__"

class IntermediatePostTrackProResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntermediateTrackProResult
        fields = "__all__"

# class FinalGetTrackProResultSerializer(serializers.ModelSerializer):    
#     Employee = serializers.StringRelatedField()
#     class Meta:
#         model = FinalTrackProResult
#         fields = "__all__"

# class FianlPostTrackProResultSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FinalTrackProResult
#         fields = "__all__"
   