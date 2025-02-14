from django.db.models import fields
from rest_framework import serializers
from Users.models import *
from django.utils.dateformat import DateFormat
from datetime import datetime
from Users.static_info import *
from .models import *
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

class holidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Holidays
        fields = '__all__'

class leaveserializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

class leaves_extra_feilds_serializer(serializers.ModelSerializer):
    start_date_month = serializers.SerializerMethodField()
    start_date_year = serializers.SerializerMethodField()
    start_date_month_name = serializers.SerializerMethodField()

    class Meta:
        model = Leave
        fields = '__all__'

    def get_start_date_month(self, obj):
        return obj.start_date.month
    def get_start_date_year(self, obj):
        return obj.start_date.year
    def get_start_date_month_name(self, obj):
        return DateFormat(obj.start_date).format('F')

class leaveapprovalserializer(serializers.ModelSerializer):
    class Meta:
        model = leaveApproval
        fields = '__all__'

class leaveMappingserializer(serializers.ModelSerializer):
    class Meta:
        model = leaveMapping
        fields = '__all__'

    
class AttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceList
        fields = '__all__'

class AttendancecountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendancecount
        fields = '__all__'
        
class TeamAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamAttendance
        fields = '__all__'


class GetUserSerializerleavemapping(serializers.ModelSerializer):
    DepartmentID = serializers.StringRelatedField(many=True)
    class Meta:
        model = Users
        fields = ['id', 'Firstname', 'Lastname','DepartmentID',]

class leave_mapping_employee_id_serializer_distinct(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.employeeId for item in data]

class leave_mapping_employee_id_serializer(serializers.ModelSerializer):
    class Meta:
        model = leaveMapping
        fields = ['employeeId']
        list_serializer_class = leave_mapping_employee_id_serializer_distinct




class leave_approvals_leaveid_serializeer(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.leave_id for item in data]

class leave_ids_serializer(serializers.ModelSerializer):
    class Meta:
        model = leaveApproval
        fields = ['leave_id']
        list_serializer_class = leave_approvals_leaveid_serializeer



class applications_serializers(serializers.ModelSerializer):
    applicant_name= serializers.SerializerMethodField()
    created_at=CustomDateField2()
    start_date=CustomDateField2()
    end_date=CustomDateField2()

    def get_applicant_name(self, obj):
        employeeId = obj.employeeId
        if employeeId:
            try:
                user = Users.objects.filter(id=employeeId,is_active=True).first()
                if user is not None:
                    return user.Firstname + " "+user.Lastname
                else:
                    return 'Unknown user'
            except Users.DoesNotExist:
                return None
        return None


    class Meta:
        model = Leave
        fields = '__all__'


class application_approval_serializers(serializers.ModelSerializer):
    manager_name= serializers.SerializerMethodField()
    manager_image= serializers.SerializerMethodField()
    def get_manager_name(self, obj):
        managerId = obj.managerId
        if managerId:
            try:
                manager = Users.objects.filter(id=managerId,is_active=True).first()
                if manager is not None:
                    return manager.Firstname + " "+manager.Lastname
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None




    def get_manager_image(self, obj):
        userId = obj.managerId
        if userId:
            try:
                user = Users.objects.filter(id=userId,is_active=True).first()
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
    




    class Meta:
        model = leaveApproval
        fields = ['manager_name','manager_image','approvedBy','rejectedBy','comment']

class LeaveTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypeMaster
        fields = '__all__'
class CarryForwardedLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarryForwardedLeave
        fields = '__all__'