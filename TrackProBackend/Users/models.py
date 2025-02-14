from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from CompanyMaster.models import companyinfo

class Designation(models.Model):
    DesignationName = models.CharField(max_length=51)
    isactive = models.BooleanField(default=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self):
        return self.DesignationName
    
class Location(models.Model):
    LocationName = models.CharField(max_length=50)
    Active = models.BooleanField(default=True)
    CreatedBy = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='locationCreatedBy',null=True, blank=True,)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.ForeignKey('Users', on_delete=models.CASCADE, null=True, blank=True, related_name='locationUpdatedBy')
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    lattitude = models.CharField(max_length=255,null=True, blank=True)
    longitude = models.CharField(max_length=255,null=True, blank=True)
    meter = models.CharField(max_length=255,null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.LocationName

class FinancialYear(models.Model):
    financialYear = models.CharField(max_length=15)
    YearCode = models.CharField(max_length=10, null=True, blank=True)  #remove null=True
    Active = models.BooleanField(default=True)
    CreatedBy = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='FinancialYearCreatedBy',null=True, blank=True,)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.ForeignKey('Users', on_delete=models.CASCADE, null=True, blank=True, related_name='FinancialYearUpdatedBy')
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self):
        return self.financialYear

class Role(models.Model):
    RoleName = models.CharField(max_length=50)
    Active = models.BooleanField(default=True,null=True, blank=True,)
    CreatedBy = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='RoleCreatedBy',null=True, blank=True,)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.ForeignKey('Users', on_delete=models.CASCADE, null=True, blank=True, related_name='RoleUpdatedBy')
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True)  #will get updated everytime model is saved
    company_code = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self):
        return self.RoleName
    
class employeetypemaster(models.Model):
    employeetype = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)
   
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, is_staff=True, is_active=True):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        # if not Username:
        #     raise ValueError("User must have a Username")
 
        user = self.model(
            email=self.normalize_email(email)
        )
        # user.Username = Username
        user.set_password(password)  # change password to hash
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password, is_staff=True, is_active=True,is_superuser=True):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        # if not Username:
        #     raise ValueError("User must have a Username")

        user = self.model(
            email=self.normalize_email(email)
        )

        
        # user.Username = Username
        user.set_password(password)
        user.is_admin = True
        user.is_superuser= True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

        # return self.create_user(email, password, **other_fields)


class Users(AbstractBaseUser,PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('T', 'Transgender'),
    )
    TYPEOFWORK_CHOICES = (
        ('1', 'work_from_home'),
        ('2', 'work_from_office'),
        ('3', 'field'),
        ('4', 'Hybrid'),
    )
    uid= models.CharField(max_length=100, unique=True,blank=True,null=True)
    Firstname = models.CharField(max_length=58,null=True, blank=True)
    Lastname = models.CharField(max_length=50,null=True, blank=True)
    Password = models.CharField(max_length=50,null=True, blank=True )
    Address= models.CharField(max_length=255,null=True, blank=True)
    Addressline2 = models.CharField(max_length=255,null=True, blank=True)
    Gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    email = models.EmailField(verbose_name='email', max_length=60,null=True,blank=True)
    personal_email = models.EmailField(verbose_name='personal_email',max_length=60,null=True,blank=True)
    onboarding = models.BooleanField(default=False,null=True,blank=True)
    BirthDate = models.DateField(null=True)
    DateofJoining = models.DateField(null=True)
    DateofLeaving = models.DateField( null=True, blank=True)
    DesignationId = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    Photo =  models.ImageField(upload_to='profileImages/', blank=True, null=True,verbose_name='Profile Photo')
    RoleID = models.ForeignKey(Role, on_delete=models.SET_NULL,  null=True, blank=True)
    employeetype = models.ForeignKey(employeetypemaster, on_delete=models.SET_NULL,  null=True, blank=True)
    DepartmentID = models.ManyToManyField('Department.Department', blank=True)
    locationId = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    Phone = models.CharField(max_length=10,null=True, blank=True )
    PasswordChanged = models.BooleanField(default=False)
    FirebaseID = models.TextField(null=True, blank=True)
    CreatedBy = models.ForeignKey('self',on_delete=models.SET_NULL, related_name='UserCreatedBy',null=True, blank=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.ForeignKey('self',on_delete=models.SET_NULL, related_name='UserUpdatedBy',null=True, blank=True)
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    employeeId = models.CharField(max_length=255, null=True,blank=True)    
    employeementStatus=models.CharField(max_length=255,null=True)
    typeofwork=models.CharField(max_length=25,choices=TYPEOFWORK_CHOICES, null=True)
    secondary_info = models.BooleanField(default=False,null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    masters = models.BooleanField(default=False,null=True)
    rules = models.BooleanField(default=False,null=True)
    documentverified = models.BooleanField(default=False,null=True)
    onboarding_get_mail= models.BooleanField(default=False,null=True,blank=True)
    linkdatetime = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    desktopToken = models.TextField(null=True, blank=True)
    objects = CustomUserManager()    

    res_lattitude= models.CharField(max_length=255,null=True, blank=True)
    res_longitude= models.CharField(max_length=255,null=True, blank=True)
    res_radius= models.CharField(max_length=255,null=True, blank=True)

    
    reason_of_rejection_documents = models.TextField(null=True) 

    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.Firstname)+' '+ str(self.Lastname)


class ErrorLog(models.Model):
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE)
    ExceptionMsg = models.TextField(null=True) 
    ExceptionType = models.TextField(null=True) 
    ExceptionSource = models.TextField(null=True) 
    ExceptionUrl = models.CharField(max_length=500, null=True) 
    ActionName = models.CharField(max_length=500, null=True) 
    IPAddress = models.CharField(max_length=500, null=True) 
    LogDate = models.DateTimeField(auto_now_add=True, null=True)
    ControllerName = models.CharField(max_length=500, null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self):
        return self.ExceptionMsg

 
class UserToManager(models.Model):
    UserID = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='UserID', null=True) #remove null=True
    ManagerID = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='ManagerID')
    UserIDStr = models.CharField(max_length=100, null=True,blank=True)
    ManagerIDStr = models.CharField(max_length=100, null=True,blank=True)
    FixedMapping = models.BooleanField(null=True)
    Active = models.BooleanField(default=False)
    CreatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='UserManagerMappingCreatedBy', null=True, blank=True)
    CreatedOn = models.DateTimeField(auto_now_add=True)
    UpdatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, related_name='UserManagerMappingUpdatedBy')
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True) 
    company_code = models.CharField(max_length=100,null=True, blank=True)
    
    
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def createAuthToken(sender, instance = None, created =False, **kwargs):
    if created:
        Token.objects.create(user = instance)

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def createProfile(sender, instance = None, created =False, **kwargs):
    if created:
        Profile.objects.create(user = instance)

class MenuItem(models.Model):
    MenuID = models.IntegerField(primary_key=True)
    MenuName = models.CharField(max_length=50)
    MenuDescription = models.CharField(max_length=50, null=True, blank=True)
    MenuPath = models.CharField(max_length=50, null=True, blank=True)
    MenuIcon = models.CharField(max_length=50, null=True, blank=True)
    Active = models.BooleanField(default=True)
    ParentID =  models.IntegerField(null=True, blank=True)
    MenuPosition = models.IntegerField(null=True, blank=True)
    SortOrder = models.IntegerField(null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

class Permissions(models.Model):
    RoleID = models.ForeignKey(Role,on_delete=models.CASCADE,related_name="Permission_RoleID")
    # UserID = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='Permissions_UserID')
    MenuID = models.ManyToManyField(MenuItem, related_name='Permissions_MenuID')
    Active = models.BooleanField(default=True)
    CreatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='Permissions_CreatedBy', null=True, blank=True)
    CreatedOn = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    UpdatedBy = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, related_name='Permissions_UpdatedBy')
    UpdatedOn =  models.DateTimeField(auto_now=True, null=True, blank=True) 
    company_code = models.CharField(max_length=100,null=True, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(Users,on_delete=models.CASCADE)
    forget_password_token=models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    updatedOn = models.DateTimeField(null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.user.email

class attendance(models.Model):
    employeeId = models.CharField(max_length=10, null=True)
    date = models.DateField(null=True)
    time =  models.CharField(max_length=50,null=True, blank=True)
    filename = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    Week = models.IntegerField(null=True, blank=True)
    Month =  models.IntegerField(null=True, blank=True)
    Year =  models.IntegerField(null=True, blank=True)
    deviceId = models.IntegerField(null=True, blank=True)
    emailsent = models.BooleanField(default=False)
    checkout = models.BooleanField(default=False)
    Remote_Reason = models.TextField(null=True,blank=True)
    remote_latitude =models.TextField(null=True,blank=True)
    remote_longitude =models.TextField(null=True,blank=True)
    attendance_type= models.CharField(max_length=550,null=True, blank=True)


class Holidays(models.Model):
    HolidayYear = models.IntegerField()
    Date = models.DateField()
    Festival = models.CharField(max_length=550, null=True, blank=True)
    HolidayMonth = models.IntegerField(null=True, blank=True)
    Holidayweek_of_month = models.IntegerField(null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    Active = models.BooleanField(default=True)
    


class UserSecondaryInfo(models.Model):
    userId = models.CharField(max_length=10, null=True,blank=True)
    alternatemail = models.CharField(max_length=255, null=True,blank=True)

    bloodgroup = models.CharField(max_length=10, null=True,blank=True)
    maritalstatus = models.CharField(max_length=100, null=True,blank=True)

    relationname1 = models.CharField(max_length=255,null=True,blank=True)
    relation1 = models.CharField(max_length=255,null=True,blank=True)
    relation1number = models.CharField(max_length=15,null=True,blank=True)

    relationname2 = models.CharField(max_length=255,null=True,blank=True)
    relation2 = models.CharField(max_length=255,null=True,blank=True)
    relation2number = models.CharField(max_length=15,null=True,blank=True)

    refname1 = models.CharField(max_length=50,null=True,blank=True)
    refdesg1 = models.CharField(max_length=50,null=True,blank=True)

    refnumber1 = models.CharField(max_length=50,null=True,blank=True)
    refemail1 = models.CharField(max_length=50,null=True,blank=True)
    refname2 = models.CharField(max_length=50,null=True,blank=True)
    refdesg2 = models.CharField(max_length=50,null=True,blank=True)
    refnumber2 = models.CharField(max_length=50,null=True,blank=True)
    refemail2 = models.CharField(max_length=50,null=True,blank=True)
    bankname = models.CharField(max_length=50,null=True,blank=True)
    ifsccode = models.CharField(max_length=50,null=True,blank=True)
    accountnumber = models.CharField(max_length=50,null=True,blank=True)
    confirmaccountnumber = models.CharField(max_length=50,null=True,blank=True)
    adhaarcard = models.CharField(max_length=50,null=True,blank=True)
    pancard = models.CharField(max_length=50,null=True,blank=True)
    adhaarcardimage = models.TextField(null=True,blank=True)
    pancardimage = models.TextField(null=True,blank=True)
    passportimage = models.TextField(null=True,blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    # passportimage = models.FileField(upload_to='passportimage/', blank=True, null=True,verbose_name='passportimage Image')
    # adhaarcardimage = models.FileField(upload_to='adhaarcard/', blank=True, null=True,verbose_name='adhaar Image')
    # pancardimage = models.FileField(upload_to='pancard/', blank=True, null=True,verbose_name='pancard Image')
    accountholdername = models.CharField(max_length=250,null=True,blank=True)
    branchname = models.CharField(max_length=250,null=True,blank=True)
    previous_pf_accountno = models.CharField(max_length=100, null=True,blank=True)
    esic_number = models.CharField(max_length=101, null=True,blank=True)
    permanentaddress = models.CharField(max_length=255, null=True,blank=True)
    permanentaddressLine2 = models.CharField(max_length=255, null=True,blank=True)


    residentialaddresscountry= models.IntegerField(null=True, blank=True)
    residentialaddressstate= models.IntegerField(null=True, blank=True)
    residentialaddresscity= models.IntegerField(null=True, blank=True)
    residentialaddresspincode= models.IntegerField(null=True, blank=True)

    permanantaddresscountry= models.IntegerField(null=True, blank=True)
    permanantaddressstate= models.IntegerField(null=True, blank=True)
    permanantaddresscity= models.IntegerField(null=True, blank=True)
    permanantaddresspincode= models.IntegerField(null=True, blank=True)

    finalsubmit=models.BooleanField(default=False)




class educational_qualifications(models.Model):
    userid = models.IntegerField()
    qualification_name = models.CharField(max_length=500)
    university = models.CharField(max_length=500,blank=True,null=True)
    obtain_marks = models.CharField(max_length=50, null=True, blank=True)
    Active = models.BooleanField(default=True)
    fromdate = models.CharField(max_length=100,null=True, blank=True)
    todate = models.CharField(max_length=100,null=True, blank=True)
    marksheet = models.TextField(null=True,blank=True)
    # marksheet = models.FileField(upload_to='marksheet/', blank=True, null=True,verbose_name='marksheet Image')

class Previous_Company_Details(models.Model):
    userid = models.IntegerField()
    companyname = models.CharField(max_length=500,null=True, blank=True)
    companyaddress =models.TextField(null=True,blank=True)
    designation = models.CharField(max_length=50, null=True, blank=True)
    Active = models.BooleanField(default=True)
    joinDate = models.CharField(max_length=100,null=True, blank=True)
    leaveDate = models.CharField(max_length=100,null=True, blank=True)
    salaryslip = models.TextField(null=True,blank=True)
    relieving = models.TextField(null=True,blank=True)



class UserStatus(models.Model):
    employeeId=models.IntegerField()
    employeementStatus=models.CharField(max_length=255,null=True)
    start_date=models.DateField(null=True)
    end_date=models.DateField(null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

class Leave(models.Model):
    employeeId =  models.CharField(max_length=10, null=True)
    start_date =  models.DateField(null=True)
    end_date = models.DateField(null=True)  
    startdayleavetype = models.CharField(max_length=50,null=True)#Fullday/FirstHalf/SecondHalf
    enddayleavetype = models.CharField(max_length=50,null=True)#Fullday/FirstHalf/SecondHalf
    leave_status =  models.CharField(max_length=50,null=True)
    reason =  models.TextField(null=True,blank=True)
    leavetype = models.CharField(max_length=50,null=True)#full day/first half/ second half
    LeaveTypeId = models.CharField(max_length=50,null=True)#leave type master id
    created_at = models.DateTimeField(auto_now=True, null=True)
    Active = models.BooleanField(default=True)
    WorkFromHome = models.BooleanField(default=False)
    ApplicationId = models.CharField(max_length=50,null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    number_of_days = models.DecimalField(max_digits=5, decimal_places=1,null=True,blank=True)
    attachment =  models.ImageField(upload_to='attachment/', blank=True, null=True,verbose_name='attachment')

    
class leaveApproval(models.Model):
    employeeId = models.CharField(max_length=10, null=True)
    leave_id =  models.CharField(max_length=10, null=True)
    managerId =  models.CharField(max_length=10, null=True)
    ApplicationId = models.CharField(max_length=50, null=True)
    approvedBy = models.BooleanField(default=False)
    rejectedBy = models.BooleanField(default=False)
    comment =  models.CharField(max_length=255, null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

class leaveMapping(models.Model):
    employeeId =  models.CharField(max_length=10, null=True)
    managerId = models.CharField(max_length=10, null=True)
    position = models.CharField(max_length=10, null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

class adminAttendanceRequest(models.Model):
    employeeId = models.IntegerField()
    adminId = models.IntegerField(null=True)
    date = models.CharField(max_length=50)
    comment = models.TextField()
    company_code = models.CharField(max_length=100,null=True, blank=True)
 
 

class AttendanceRequest(models.Model):
    UserId = models.IntegerField(null=True,blank=True)
    Date = models.DateField(null=True)
    AttendanceId = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    actiontakenby = models.IntegerField(null=True,blank=True)
    Action =  models.CharField(max_length=255,null=True,blank=True)
    Reason = models.TextField(null=True,blank=True)
    CheckInTime = models.CharField(max_length=255,null=True,blank=True)
    manager_ids = models.ManyToManyField(Users, related_name='Manager')
    company_code = models.CharField(max_length=100,null=True, blank=True)
    Active = models.BooleanField(default=True)
    


class trackprorules(models.Model):
    colorcode = models.CharField(max_length=50, null=True)
    trackpropoints = models.IntegerField(null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

class ApiKey(models.Model):
    api_key = models.CharField(max_length=256,null=True, blank=True)
    company_code = models.CharField(max_length=100,null=True, blank=True) 
    expiry_date = models.DateField(null=True,blank=True) 
    isActive = models.BooleanField(default=True)

class AttendanceList(models.Model):
    Empcode = models.CharField(max_length=100, unique=True,blank=True,null=True)
    Firstname = models.CharField(max_length=50,null=True, blank=True)
    Lastname = models.CharField(max_length=50,null=True, blank=True)
    userId = models.IntegerField(null=True)
    AttendanceId =  models.CharField(max_length=255, null=True,blank=True) 
    Ontimecount =  models.IntegerField(null=True)
    Latecount =  models.IntegerField(null=True)
    Leavecount = models.IntegerField(null=True)
    Designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    Week =  models.IntegerField(null=True)
    Month = models.IntegerField(null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)



class Attendancecount(models.Model):
    Date = models.DateField()
    Year =  models.IntegerField(null=True)
    Week =  models.IntegerField(null=True)
    Month = models.IntegerField(null=True)
    CheckIn  =  models.IntegerField(null=True)
    checkOut =  models.IntegerField(null=True)
    overtime = models.IntegerField(null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)

class TeamAttendance(models.Model):
    managerid = models.CharField(max_length=255)
    team_hold_by = models.CharField(max_length=255)
    date = models.DateField()
    present_count = models.IntegerField(null=True)
    on_leave_count = models.IntegerField(null=True)
    on_wfh_count = models.IntegerField(null=True)
    not_found_count = models.IntegerField(null=True)
    total_count = models.IntegerField(null=True)
    without_attendanceid_total_count= models.IntegerField(null=True)
    with_attendanceid_total_count= models.IntegerField(null=True)
    company_code = models.CharField(max_length=100,null=True, blank=True)
    present_employees = models.TextField(null=True, blank=True)
    on_leave_employees = models.TextField(null=True, blank=True)
    on_wfh_employees = models.TextField(null=True, blank=True)
    not_found_employees = models.TextField(null=True, blank=True)
    total_employees = models.TextField(null=True, blank=True)
    without_attendanceid_employees = models.TextField(null=True, blank=True)
    with_attendanceid_employees = models.TextField(null=True, blank=True)

class Country(models.Model):
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=255)
    numeric_code = models.CharField(max_length=255)
    iso2 = models.CharField(max_length=255)
    phonecode = models.CharField(max_length=255)
    capital = models.CharField(max_length=255,null=True)
    currency = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=255)
    tld = models.CharField(max_length=255)
    native = models.CharField(max_length=255)
    region = models.CharField(max_length=255,null=True)
    subregion = models.CharField(max_length=255,null=True)
    timezones = models.TextField()
    translations = models.TextField()
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    emoji = models.CharField(max_length=255)
    emojiU =models.CharField(max_length=255)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)
    sequence = models.CharField(max_length=255)
    wikiDataId = models.CharField(max_length=255)

    def __str__(self):

        return self.name

class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country,on_delete=models.CASCADE)
    country_code = models.CharField(max_length=255)
    state_code = models.CharField(max_length=255,null=True)
    TIN = models.CharField(max_length=255)
    iso2 = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)
    wikiDataId = models.CharField(max_length=255)
 

    def __str__(self):

        return self.name

class Cities(models.Model):
    name = models.CharField(max_length=255)
    state_code = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)
    wikiDataId = models.CharField(max_length=255,null=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    country = models.ForeignKey(Country,on_delete=models.CASCADE)

 

    def __str__(self):

        return self.name

class Checkotp(models.Model):
    userid = models.BigIntegerField()
    otp = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now=True, null=True,blank=True)
    Active = models.BooleanField(default=True)


class DeviceVerification(models.Model):
    userid = models.BigIntegerField()
    employee_code = models.CharField(max_length=255,null=True)
    app_version = models.CharField(max_length=255,null=True)
    unique_device_id = models.CharField(max_length=255,null=True)
    device_name = models.CharField(max_length=255,null=True)
    is_active = models.BooleanField(default=True)




class DeviceChangeRequest(models.Model):
    userid = models.BigIntegerField()
    employee_code = models.CharField(max_length=255,null=True)
    remark = models.TextField(null=True, blank=True)
    app_version = models.CharField(max_length=255,null=True)
    unique_device_id = models.CharField(max_length=255,null=True)
    device_name = models.CharField(max_length=255,null=True)
    status = models.CharField(max_length=255,null=True,default='Pending')
    is_active = models.BooleanField(default=True)
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, null=True)


class ShiftMaster(models.Model):
    shiftname = models.CharField(max_length=255,null=True)
    intime = models.CharField(max_length=255,null=True)
    outtime = models.CharField(max_length=255,null=True)
    is_active = models.BooleanField(default=True)


class EmployeeShiftDetails(models.Model):
    employee_name = models.CharField(max_length=255,null=True)
    employeeId = models.CharField(max_length=255,null=True)
    is_active = models.BooleanField(default=True)


class ShiftAllotment(models.Model):
    employee_name = models.CharField(max_length=255,null=True)
    employeeId = models.CharField(max_length=255,null=True)
    attendanceId = models.CharField(max_length=255,null=True)
    date = models.CharField(max_length=255,null=True)
    shift_name = models.CharField(max_length=255,null=True)
    shiftId = models.CharField(max_length=255,null=True)
    is_active = models.BooleanField(default=True)
    is_swaped = models.BooleanField(default=False)
    swapper = models.BooleanField(null=True,blank=True)
    swap_request_id = models.CharField(max_length=255,null=True)
    
class TypeRules(models.Model):
    TypeId =  models.CharField(max_length=255,null=True)
    Shifts =  models.ManyToManyField(ShiftMaster, related_name='shift')
    CompOff = models.BooleanField(default=False)
    CompOffTime = models.CharField(max_length=255,null=True,blank=True)
    CompOffValidity = models.CharField(max_length=255,null=True,blank=True)
    is_active = models.BooleanField(default=True)


class warninglog(models.Model):
    mail_time = models.CharField(max_length=255,null=True)
    mail_date = models.DateField()
    mailType = models.CharField(max_length=255,null=True)
    mailsubject = models.TextField(null=True, blank=True)
    mailcontent = models.TextField(null=True, blank=True)
    mailFrom = models.CharField(max_length=255,null=True)
    mailTo = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now=True, null=True,blank=True)
    CreatedBy = models.CharField(max_length=255,null=True)


class ManagerPinedDepartmentMaster(models.Model):
    department_id =  models.CharField(max_length=255,null=True)
    department_name =  models.CharField(max_length=255,null=True)
    user_id =  models.CharField(max_length=255,null=True)
    is_active = models.BooleanField(default=True)
    pined = models.BooleanField(default=False)



class CompOffGrantedMaster(models.Model):
    employeeId =  models.CharField(max_length=255,null=True,blank=True)
    employee_name =  models.CharField(max_length=255,null=True,blank=True)
    compoff_date = models.CharField(max_length=255,null=True,blank=True)
    compoff_time = models.CharField(max_length=255,null=True,blank=True)
    compoff_valid_days = models.CharField(max_length=255,null=True,blank=True)
    status = models.CharField(max_length=255,null=True,blank=True,default='Approved')
    created_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    claim = models.BooleanField(default=False)
    



class EligibleCompOffMaster(models.Model):
    user_id =  models.CharField(max_length=255,null=True,blank=True)
    user_name =  models.CharField(max_length=255,null=True,blank=True)
    date = models.DateTimeField(null=True)
    valid_date = models.DateTimeField(null=True)
    working_hrs = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True) #compoff normal delete
    claim = models.BooleanField(default=False)
    shift_name = models.CharField(max_length=255,null=True,blank=True)
    reschedule = models.BooleanField(default=False) 

class ClaimedCompOffMaster(models.Model):
    user_id =  models.CharField(max_length=255,null=True,blank=True)
    user_name =  models.CharField(max_length=255,null=True,blank=True)
    date = models.DateTimeField(null=True)
    valid_date = models.DateTimeField(null=True)
    working_hrs = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True) #compoff normal delete
    claim_date = models.DateTimeField(null=True)
    eligible_compoff_id =  models.CharField(max_length=10, null=True)
    shift_name = models.CharField(max_length=255,null=True,blank=True)
    status = models.CharField(max_length=255,null=True,default='Pending')#Pending,Rejected,Expired,Approved,Withdrawn,Reschedule
    earlier_reschedule = models.BooleanField(default=False) 
    earlier_reschedule_id = models.CharField(max_length=255,null=True,blank=True)



class CompoffApproval(models.Model):
    user_id = models.CharField(max_length=10, null=True)
    claimed_compoff_id =  models.CharField(max_length=10, null=True)
    eligible_compoff_id =  models.CharField(max_length=10, null=True)
    manager_id =  models.CharField(max_length=10, null=True)
    status = models.BooleanField(null=True) # status of approved=True,rejected =False and Pending = None
    rejected_reason = models.TextField(null=True, blank=True)
    reschedule_reason = models.TextField(null=True, blank=True)
    reschedule = models.BooleanField(default=False) 
