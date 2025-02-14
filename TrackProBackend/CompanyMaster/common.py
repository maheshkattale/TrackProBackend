from Users.models import Users,MenuItem,Permissions
from Users.serializers import GetMenuItemSerializer,PermissionsSerializer
from CompanyMaster.models import companypaymentlog
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from rest_framework.response import Response
from TrackProBackend.settings import EMAIL_HOST_USER

def createadminuser(admin,adminPassword,user_firstname,user_lastname,roleObject,companycode,dob,uid):
    Users.objects.create(
            email=admin,
            password = make_password(adminPassword),
            Firstname = user_firstname,
            Lastname = user_lastname,
            Password = adminPassword,
            RoleID = roleObject,
            company_code = companycode,
            BirthDate = dob,
            uid=uid
        )

def givePermission(companycode,RoleId):      
        menuItemList = []                          
        menuObject = MenuItem.objects.filter(company_code = None)
        menuSerializer = GetMenuItemSerializer(menuObject,many=True)
        for i in menuSerializer.data:
                menuItemList.append(i['MenuID'])
        permissioncreate = Permissions.objects.create(
                                                        RoleID_id = RoleId,
                                                        company_code = companycode
                                )
        permissioncreate.MenuID.set(menuItemList)   
                

def paymentlog(companyId,planperiod,startdate,expirydate,payment):
    companypaymentlog.objects.create(
            companyId = companyId,
            planperiod = planperiod,
            startdate = startdate,
            expirydate = expirydate,
            payment = payment
    )

def send_mail(data, message):
    try:
        msg = EmailMessage(
            data['subject'],
            message,
            EMAIL_HOST_USER,
            [data['email']],
        )
        msg.content_subtype = "html"
        m = msg.send()
        if m:
            print(m)
        data['n'] = 1
        data['Msg'] = 'Email has been sent'
        data['Status'] = "Success"
        return Response(data)
    except Exception as e:
        return Response({'n': 0, 'Msg': 'Email could not be sent', 'Status': 'Failed'})