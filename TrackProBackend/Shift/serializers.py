from rest_framework import serializers
from .models import *
from Users.models import *
from Users.static_info import *
from datetime import datetime


class CustomDateField2(serializers.DateField):
    def to_representation(self, value):
        # Converts the date to the desired format for output
        return value.strftime('%d %b %Y')
    
    def to_internal_value(self, data):
        # Converts the input date string into a date object
        try:
            return datetime.datetime.strptime(data, '%d %b %Y').date()
        except ValueError:
            raise serializers.ValidationError("Date format should be 'dd Mon yyyy'")

class ShiftswapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shiftswap
        fields = '__all__'


class ShiftswapActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftswapAction
        fields = '__all__'

class shiftmanagersSerializer(serializers.ModelSerializer):
    class Meta:
        model = shiftmanagers
        fields = '__all__'


class shift_approvals_shiftid_serializeer(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.RequestId for item in data]

class shift_id_serializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftswapAction
        fields = ['RequestId']
        list_serializer_class = shift_approvals_shiftid_serializeer








class CustomShiftswapActionSerializer(serializers.ModelSerializer):
    manager_name= serializers.SerializerMethodField()
    manager_image= serializers.SerializerMethodField()
    manager_base_image= serializers.SerializerMethodField()
    manager_email= serializers.SerializerMethodField()
    def get_manager_name(self, obj):
        ManagerId = obj.ManagerId
        if ManagerId:
            try:
                manager = Users.objects.filter(id=ManagerId,is_active=True).first()
                if manager is not None:
                    return manager.Firstname + " "+manager.Lastname
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None
    
    def get_manager_email(self, obj):
        ManagerId = obj.ManagerId
        if ManagerId:
            try:
                manager = Users.objects.filter(id=ManagerId,is_active=True).first()
                if manager is not None:
                    return manager.email
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None

    def get_manager_image(self, obj):
        user_id = obj.ManagerId
        if user_id:
            try:
                user = Users.objects.filter(id=user_id,is_active=True).first()
                if user is not None:
                    if user.Photo is not None and user.Photo !='':
                        return imageUrl+'/media/'+str(user.Photo) 
                    else:
                        return imageUrl+'/static/assets/images/profile.png'
                else:
                    return imageUrl+'/static/assets/images/profile.png'
                    
            except Users.DoesNotExist:
                return None
        return None
    
    def get_manager_base_image(self, obj):
        user_id = obj.ManagerId
        if user_id:
            try:
                user = Users.objects.filter(id=user_id,is_active=True).first()
                if user is not None:
                    if user.Photo is not None and user.Photo !='':
                        return '/media/'+str(user.Photo) 
                    else:
                        return '/static/assets/images/profile.png'
                else:
                    return '/static/assets/images/profile.png'
                    
            except Users.DoesNotExist:
                return None
        return None

    class Meta:
        model = ShiftswapAction 
        fields = ['id','ManagerId','RequestId','ActionTaken','RejectionReason','manager_image','manager_name','manager_email','manager_base_image']

class CustomShiftswapSerializer(serializers.ModelSerializer):
    Swapshiftdate=CustomDateField2()
    Shiftdate=CustomDateField2()
    first_employee_name= serializers.SerializerMethodField()
    created_at=CustomDateField2()

    def get_first_employee_name(self, obj):
        employeeId = obj.employeeId
        if employeeId:
            try:
                employee = Users.objects.filter(id=employeeId,is_active=True).first()
                if employee is not None:
                    return employee.Firstname + " "+employee.Lastname
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None
    second_employee_name= serializers.SerializerMethodField()
    def get_second_employee_name(self, obj):
        employeeId = obj.SwapempId
        if employeeId:
            try:
                employee = Users.objects.filter(id=employeeId,is_active=True).first()
                if employee is not None:
                    return employee.Firstname + " "+employee.Lastname
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None


    class Meta:
        model = Shiftswap
        fields = '__all__'