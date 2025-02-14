from django.db.models import fields
from rest_framework import serializers
from Users.models import *
from django.utils.dateformat import DateFormat
from datetime import datetime
from Users.static_info import *
from .models import *


class PacketMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacketMaster
        fields = '__all__'

class PacketLeaveRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacketLeaveRules
        fields = '__all__'