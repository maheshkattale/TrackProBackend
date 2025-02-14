from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import *

class Clientserializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields ='__all__'

class ClientsideManagerserializer(serializers.ModelSerializer):
    class Meta:
        model = ClientsideManager
        fields ='__all__'

class createClientserializer(serializers.ModelSerializer):
    class Meta:
        model = CreateClient
        fields ='__all__'

class getcreateClientserializer(serializers.ModelSerializer):
    Team = serializers.StringRelatedField(many=True)
    Client_ManagerId = serializers.StringRelatedField(many=True)
    class Meta:
        model = CreateClient
        fields ='__all__'

class Eventserializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields ='__all__'



class Client_Projectserializer(serializers.ModelSerializer):
    # SerializerMethodField to include client name
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Client_Project
        fields = '__all__'

    def get_client_name(self, obj):
        # Access the related Client instance and return the client name
        client_instance = obj.get_client()  # Assuming you have a get_client method in your Client_Project model
        return client_instance.ClientName if client_instance else None