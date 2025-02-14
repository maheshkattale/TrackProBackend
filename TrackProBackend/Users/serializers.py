from django.db.models import fields
from rest_framework import serializers
from .models import *
from django.utils.dateformat import DateFormat
from datetime import date,datetime,timedelta,time
from .static_info import *

class UserSerializer(serializers.ModelSerializer):
    DesignationId = serializers.StringRelatedField()
    RoleID = serializers.StringRelatedField()

    class Meta:
        model = Users
        fields = ['id', 'uid', 'Firstname', 'Lastname', 'Address','Addressline2', 'Gender', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId', 'locationId','Photo', 'RoleID', 'DepartmentID', 'Phone',
                  'FirebaseID', 'Password', 'CreatedBy', 'CreatedOn', 'employeementStatus','UpdatedBy', 'UpdatedOn', 'is_staff', 'is_superuser', 'is_active', 'is_admin','employeeId','typeofwork','linkdatetime',
                  'personal_email','onboarding','password','company_code','documentverified','desktopToken','res_radius','res_longitude','res_lattitude','employeetype']
        ordering = ['-CreatedOn']
        
class UserAllInfoSerializer(serializers.ModelSerializer):
    Designation_id = serializers.PrimaryKeyRelatedField(source='DesignationId', queryset=Designation.objects.all())
    Role_id = serializers.PrimaryKeyRelatedField(source='RoleID', queryset=Role.objects.all())
    
    
    DesignationId = serializers.StringRelatedField()
    RoleID = serializers.StringRelatedField()
    
    
    class Meta:
        model = Users
        fields = ['id', 'uid', 'Firstname', 'Lastname', 'Address','Addressline2', 'Gender', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId','Designation_id', 'Role_id','locationId','Photo', 'RoleID', 'DepartmentID', 'Phone',
                  'FirebaseID', 'Password', 'CreatedBy', 'CreatedOn', 'employeementStatus','UpdatedBy', 'UpdatedOn', 'is_staff', 'is_superuser', 'is_active', 'is_admin','employeeId','typeofwork','linkdatetime',
                  'personal_email','onboarding','password','company_code','documentverified','desktopToken','res_radius','res_longitude','res_lattitude','employeetype']
        ordering = ['-CreatedOn']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class GetUserSerializerleavemapping(serializers.ModelSerializer):
    DepartmentID = serializers.StringRelatedField(many=True)
    class Meta:
        model = Users
        fields = ['id', 'Firstname', 'Lastname','DepartmentID',]

class UsersSerializer(serializers.ModelSerializer): 
    DepartmentID = serializers.StringRelatedField(many=True)
    DesignationId = serializers.StringRelatedField()
    RoleID = serializers.StringRelatedField()
    locationId = serializers.StringRelatedField()

    class Meta:
        model = Users
        fields = ['id', 'uid', 'Firstname', 'Lastname', 'Address', 'Gender', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId', 'Photo', 'RoleID', 'DepartmentID', 'Phone',
                  'FirebaseID', 'Password', 'CreatedBy', 'employeementStatus','CreatedOn', 'UpdatedBy', 'UpdatedOn', 'is_staff', 'is_superuser', 'is_active', 'is_admin','typeofwork','locationId','employeeId','secondary_info',
                  'personal_email','documentverified','onboarding','reason_of_rejection_documents','onboarding_get_mail','employeetype','company_code']
        ordering = ['-CreatedOn']

class UsersdashboardSerializer(serializers.ModelSerializer): 

    class Meta:
        model = Users
        fields = ['id', 'Firstname', 'Lastname','typeofwork','DepartmentID','employeeId']





class AttendanceSerializerAttendanceDate(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.date.strftime("%Y-%m-%d") for item in data]
    
class AttendanceSerializerAttendanceWeekDate(serializers.ModelSerializer):
    class Meta:
        model = attendance
        fields = ['date']
        list_serializer_class = AttendanceSerializerAttendanceDate
        
        
class AttendanceSerializer_id(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.id.strftime("%Y-%m-%d") for item in data]
    
class AttendanceSerializer_only_id(serializers.ModelSerializer):
    class Meta:
        model = attendance
        fields = ['id']
        list_serializer_class = AttendanceSerializer_id


class UsersSerializerAttendanceId(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.employeeId for item in data]

class UsersSerializeronlyattendance(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['employeeId']
        list_serializer_class = UsersSerializerAttendanceId


class UsersSerializerUserId(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.id for item in data]

class UsersSerializeronlyid(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id']
        list_serializer_class = UsersSerializerUserId



class UsersSerializerdesktoptokenfilter(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.desktopToken for item in data]

class UserSerializerDesktopToken(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['desktopToken']
        list_serializer_class = UsersSerializerdesktoptokenfilter



class userRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['Photo', 'Firstname', 'Lastname', 'password', 'Password', 'Address', 'Gender', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId', 'RoleID', 'DepartmentID', 'Phone',
                  'FirebaseID', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 'UpdatedOn', 'is_staff', 'is_superuser', 'is_active', 'is_admin','typeofwork','company_code',
                  'employeeId','employeetype']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = Users(
            Firstname=self.validated_data['Firstname'],
            Lastname=self.validated_data['Lastname'],
            # Address=self.validated_data['Address'],
            # Gender=self.validated_data['Gender'],
            # typeofwork=self.validated_data['typeofwork'],
            # employeeId=self.validated_data['employeeId'],
            company_code=self.validated_data['company_code'],
            email=self.validated_data['email'],
            # BirthDate=self.validated_data['BirthDate'],
            # DateofJoining=self.validated_data['DateofJoining'],
            # DateofLeaving=self.validated_data['DateofLeaving'],
            # DesignationId=self.validated_data['DesignationId'],
            # Photo=self.validated_data['Photo'],
            RoleID=self.validated_data['RoleID'],
            Phone=self.validated_data['Phone'],
            is_staff=self.validated_data['is_staff'],
            is_superuser=self.validated_data['is_superuser'],
            is_active=self.validated_data['is_active'],
            is_admin=self.validated_data['is_admin'],
            Password=self.validated_data['password']
        )
        password = self.validated_data['password']
        user.set_password(password)
        user.CreatedBy = self.context['request'].user
        user.save()
        if self.validated_data['DepartmentID'] is not None:
            DepartmentID = self.validated_data['DepartmentID']
            user.DepartmentID.set(DepartmentID)
        return user


class userUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id','Firstname', 'Lastname', 'Address', 'Gender','personal_email', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId', 'Photo', 'RoleID', 'DepartmentID', 'Phone',
                  'FirebaseID', 'CreatedBy', 'employeementStatus','CreatedOn', 'UpdatedBy', 'UpdatedOn', 'is_admin','typeofwork','is_superuser','employeeId','locationId','documentverified','company_code','linkdatetime','employeetype','password','Password']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        
class RoleIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id']

class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = '__all__'

class UserSecondarySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserSecondaryInfo
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class FinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = '__all__'


class MappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToManager
        fields = '__all__'

class usernameSerializer(serializers.ModelSerializer):  # for many to many field
    class Meta:
        model = UserToManager
        fields = ['Firstname', 'Lastname']


class GetMappingSerializer(serializers.ModelSerializer):
    # UserID = usernameSerializer(read_only=True, many=True)
    UserID = serializers.StringRelatedField()
    ManagerID = serializers.StringRelatedField()

    class Meta:
        model = UserToManager
        fields = '__all__'


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = ['id', 'RoleID', 'MenuID', 'Active','company_code']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['MenuID', 'MenuName', 'Active', 'ParentID','company_code']

class GetMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class passwordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['password']

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'Firstname', 'Lastname']

class monthlydataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['employeeId']

class attendanceserializer(serializers.ModelSerializer):
    class Meta:
        model = attendance
        fields = '__all__'

class attendancerequestserializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRequest
        fields = '__all__'


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

class BasicInfoSerializer(serializers.ModelSerializer):
    DepartmentID = serializers.StringRelatedField(many=True)
    DesignationId = serializers.StringRelatedField()
    RoleID = serializers.StringRelatedField()
    locationId = serializers.StringRelatedField()

    class Meta:
        model = Users
        fields = [ 'id','uid', 'Firstname', 'Lastname', 'Address', 'Gender', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId', 'Photo', 'RoleID', 'DepartmentID', 'Phone',
                  'employeementStatus','typeofwork','locationId','employeetype']
       
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

class educational_qualificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = educational_qualifications
        fields = '__all__'

class Previous_Company_Details_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Previous_Company_Details
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'

class GetUserSerializerleavemapping(serializers.ModelSerializer):
    DepartmentID = serializers.StringRelatedField(many=True)
    class Meta:
        model = Users
        fields = ['id', 'Firstname', 'Lastname','DepartmentID',]

class DeviceChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceChangeRequest
        fields = '__all__'

class ShiftMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftMaster
        fields = '__all__'


class EmployeeShiftDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShiftDetails
        fields = '__all__'


class ShiftAllotmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAllotment
        fields = '__all__'
        
        
def group_shifts(shiftallotments):
    grouped_data = {}
    for shift in shiftallotments:

        key = (shift['employeeId'], shift['is_active'], shift['date'])
        if key not in grouped_data:
            grouped_data[key] = {
                'id': shift['id'],
                'employeeId': shift['employeeId'],
                'is_active': shift['is_active'],
                'date': shift['date'],
                'shiftlist': [],
            }
        grouped_data[key]['shiftlist'].append({"shift_name":shift['shift_name']})

    return list(grouped_data.values())
        
        
        
        
class ShiftAllotmentEmployeeSerializerfilter(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.employee_name for item in data]

class ShiftAllotmentEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAllotment
        fields = ['employee_name']
        list_serializer_class = ShiftAllotmentEmployeeSerializerfilter        




        
class ShiftAllotmentshiftIdSerializerfilter(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.shiftId for item in data]

class ShiftAllotmentshiftIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAllotment
        fields = ['shiftId']
        list_serializer_class = ShiftAllotmentshiftIdSerializerfilter   
        
        
        
class UserSerializerDesignationId(serializers.ModelSerializer):
    RoleID = serializers.StringRelatedField()

    class Meta:
        model = Users
        fields = ['id', 'uid', 'Firstname', 'Lastname', 'Address','Addressline2', 'Gender', 'email', 'BirthDate', 'DateofJoining', 'DateofLeaving', 'DesignationId', 'locationId','Photo', 'RoleID', 'DepartmentID', 'Phone',
                  'FirebaseID', 'Password', 'CreatedBy', 'CreatedOn', 'employeementStatus','UpdatedBy', 'UpdatedOn', 'is_staff', 'is_superuser', 'is_active', 'is_admin','employeeId','typeofwork','linkdatetime',
                  'personal_email','onboarding','password','company_code','documentverified','desktopToken','employeetype']
        ordering = ['-CreatedOn']
        
class employeetypemasterserializer(serializers.ModelSerializer):
    class Meta:
        model = employeetypemaster
        fields = '__all__'

class TypeRulesserializer(serializers.ModelSerializer):
    class Meta:
        model = TypeRules
        fields = '__all__'
        
        
class L1L2Serializeridfilter(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.employeeId for item in data]

class L1L2Serializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShiftDetails
        fields = ['employeeId']
        list_serializer_class = L1L2Serializeridfilter
        
        
class DeviceVerificationSerializer(serializers.ModelSerializer):
    # userid = serializers.StringRelatedField()
    class Meta:
        model = DeviceVerification
        fields = ['userid','app_version','unique_device_id','device_name']

class warninglogserializer(serializers.ModelSerializer):
    class Meta:
        model = warninglog
        fields = '__all__'
        
        
class ManagerPinedDepartmentMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPinedDepartmentMaster
        fields = '__all__'
        
     
class CompOffGrantedMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOffGrantedMaster
        fields = '__all__'
        
        
class CustomDateField(serializers.DateField):
    def to_representation(self, value):
        # Converts the date to the desired format for output
        return value.strftime('%d %B %Y')
    
    def to_internal_value(self, data):
        # Converts the input date string into a date object
        try:
            return datetime.datetime.strptime(data, '%d %B %Y').date()
        except ValueError:
            raise serializers.ValidationError("Date format should be 'dd Month yyyy'")
        
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
        

class attendance_user_serializer(serializers.ModelSerializer):
    
    user_name = serializers.SerializerMethodField()
    get_ontime = serializers.SerializerMethodField()
    date=CustomDateField()
    
    
    def get_user_name(self, obj):
        user_id = obj.employeeId
        if user_id:
            try:
                user = Users.objects.filter(employeeId=user_id,is_active=True).first()
                if user is not None:
                    return user.Firstname + " "+user.Lastname
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None
    


    def get_get_ontime(self, obj):
        user_id = obj.employeeId
        date = obj.date
        com_code=obj.company_code

        if user_id:
            try:
                ontime_obj = attendance.objects.filter(employeeId=user_id,date=date,time__lt=time(10, 0, 0),company_code=com_code).first()
                if ontime_obj is not None:
                    return True
                else:
                    return False
                    
            except attendance.DoesNotExist:
                return None
        return None
    
    class Meta:
        model = attendance
        fields = ['employeeId','date','time','company_code','id','user_name','get_ontime']

class save_compoff_serializers(serializers.ModelSerializer):

    class Meta:
        model = EligibleCompOffMaster
        fields = '__all__'
class save_claimed_compoff_serializers(serializers.ModelSerializer):

    class Meta:
        model = ClaimedCompOffMaster
        fields = '__all__'

class compoff_approval_serializers(serializers.ModelSerializer):
    # user_name= serializers.SerializerMethodField()
    manager_name= serializers.SerializerMethodField()
    manager_image= serializers.SerializerMethodField()
    manager_base_image= serializers.SerializerMethodField()
    manager_email= serializers.SerializerMethodField()
    def get_manager_name(self, obj):
        manager_id = obj.manager_id
        if manager_id:
            try:
                manager = Users.objects.filter(id=manager_id,is_active=True).first()
                if manager is not None:
                    return manager.Firstname + " "+manager.Lastname
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None
    def get_manager_email(self, obj):
        manager_id = obj.manager_id
        if manager_id:
            try:
                manager = Users.objects.filter(id=manager_id,is_active=True).first()
                if manager is not None:
                    return manager.email
                else:
                    return 'Unknown user'
                    
            except Users.DoesNotExist:
                return None
        return None



    def get_manager_image(self, obj):
        user_id = obj.manager_id
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
        user_id = obj.manager_id
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
        model = CompoffApproval
        fields = ['id','user_id','manager_name','manager_id','claimed_compoff_id','status','manager_image','manager_email','manager_base_image']



class compoff_serializers(serializers.ModelSerializer):

    date=CustomDateField2()
    valid_date=CustomDateField2()
    created_at=CustomDateField2()


    class Meta:
        model = EligibleCompOffMaster
        fields = '__all__'

class claimed_compoff_serializers(serializers.ModelSerializer):

    date=CustomDateField2()
    valid_date=CustomDateField2()
    created_at=CustomDateField2()
    claim_date=CustomDateField2()


    class Meta:
        model = ClaimedCompOffMaster
        fields = '__all__'

class compoff_approvals_compoffid_serializeer(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.claimed_compoff_id for item in data]

class compoff_id_serializer(serializers.ModelSerializer):
    class Meta:
        model = CompoffApproval
        fields = ['claimed_compoff_id']
        list_serializer_class = compoff_approvals_compoffid_serializeer



class claimed_eligiliblecompoffid_serializeer(serializers.ListSerializer):
    def to_representation(self, data):
        return [item.eligible_compoff_id for item in data]

class claimed_eligiliblecompoff_id_serializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimedCompOffMaster
        fields = ['eligible_compoff_id']
        list_serializer_class = claimed_eligiliblecompoffid_serializeer

