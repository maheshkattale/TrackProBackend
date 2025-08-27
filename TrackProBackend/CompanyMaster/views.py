from functools import partial
from genericpath import exists
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.template.loader import get_template, render_to_string
from CompanyMaster.serializers import companyserializer,paymentslipserializer,BillingPeriodSerializer,CompanytypeSerializer,CompanypaymentlogSerializer
from CompanyMaster.models import companyinfo,paymentslip,BillingPeriod,CompanyType,companypaymentlog
from Users.models import Designation,Location,ApiKey
from Users.serializers import userUpdateSerializer
from Department.models import Department
from Project.models import ProjectMaster
from tablib import Dataset
from Users.models import Users,Role,Designation,ApiKey,Permissions
from Tasks.models import TaskNotification,NotificationTypeMaster
from Department.models import Department
from django.contrib.auth.hashers import make_password
from datetime import datetime, date, timedelta
from .common import createadminuser,paymentlog,givePermission,send_mail
import string
import random
import secrets
import datetime

from Users.static_info import imageUrl,frontUrl



FCM_SERVER_KEY = "AAAATfkm0ng:APA91bHUOgZDv1TsIez3h5tL7VjdztdM5ZTDaaaje3oohFYXxVTbOQhKRb61VLOX-AbI94gSBSPqmn2p3AlxG6y5PPK-ar2h4PmwQAVoHbSXBSlOJSkaS9VfLWM7IVs4FnktsNrJwHET"
Desktop_key = "AAAAHo7KAlo:APA91bFceCCAOb7o_ZTnRI76Zy8Zx9kCY3KBTcPc9zTFzGWviC4PMn8gmu_4blzDH7_RWo1wgpyGPYQtTiqJZ9OiyuFT9tkP1X5rb6DGbICJC0VdfOtNzi4cMvZDq4Ze-popUPhKAd9U"


# Create your views here.\

def EmployeeCode(company_code):
    
    firstemplyeestrt = company_code + "/"
    object = Users.objects.filter(company_code = company_code).exclude(uid__isnull=True).last()
    emp = 0
    if object is None:
        emp = 0
        firstSale = firstemplyeestrt +"1001"
        return firstSale
    else:
        emp = str(object.uid)
        place_emp_str =int(str(emp[-4:])) + 1
        newempstr = "%04d" % (place_emp_str)
        newempId = firstemplyeestrt+str(newempstr)
        return newempId


def companyUniqueCode(companyname):
    company = [s[0].upper() for s in companyname.split()]
    companyJoin = "".join(company)
    firstCompany = companyJoin + "001"
    companyobject = companyinfo.objects.filter(isactive=True).order_by('-created_at').first()
    if companyobject is None:
        companycode = firstCompany
        return companycode
    else:
        stripcompany = companyobject.companycode[-3:]
        increementCompany = int(stripcompany) + 1
        placeCompany = "%03d" % (increementCompany)
        newcompanycode = companyJoin + str(placeCompany)
        return newcompanycode



@api_view(['POST'])
def addcompanyAPI(request):
    data={}
    data['companyName']=request.POST.get('companyname')
    data['companylogos']=request.FILES.get('companylogos')
    data['gstcertificate']=request.FILES.get('gstcertificate')
    data['companyAddress']=request.data.get('caddress')
    data['contact']=request.data.get('contact')
    data['gstNumber']=request.data.get('gstNumber')
    data['adhaarNumber']=request.data.get('adhaarNumber')
    data['panNumber']=request.data.get('panNumber')
    data['memberadmin']=request.data.get('memberadmin')
    data['companyType'] = request.data.get('companyType')
    period = request.POST.get('period')
    current_date = date.today()
    if period is not None and period != None:
        data['payment'] = request.POST.get('payment')
        data['period'] = request.POST.get('period')
        billobject = BillingPeriod.objects.filter(isActive=True)
        billSer = BillingPeriodSerializer(billobject,many=True)
        for b in billSer.data:        
            if period == b['period']:
                data['expirydate'] = current_date + timedelta(days=int(b['duration']))
                data['status'] = 'Done'
                data['startdate'] = current_date
           
    else:
        data['period'] = request.POST.get('period')
        data['status'] = 'Not Done'
        
    membersplit = data['memberadmin']
    user_firstname = membersplit.split('@')[0]
    user_lastname = membersplit.split('@')[1].split('.')[0]
    data['companyDomain']=request.data.get('companyDomain')
    companyName = request.POST.get('companyname')
    data['companycode'] = companyUniqueCode(companyName)
    companyObject = companyinfo.objects.filter(isactive=True,companyName__in = [companyName.strip().capitalize(),companyName.strip(),companyName.title(),companyName.strip().upper()]).first()
    if companyObject is not None:        
        return Response({
        "data": {},
        "response": {
            "n": 0,
            "msg": "Comapany with this name already exists",
            "status": "failure"
        }
        })
    userObject = Users.objects.filter(is_active=True,email = data['memberadmin']).first()
    if userObject is not None:
        return Response({
        "data": {},
        "response": {
            "n": 0,
            "msg": "Admin with this email id already exists",
            "status": "failure"
        }
        })
    current_date = date.today()
    serializer = companyserializer(data=data)
    dob = current_date - timedelta(days=10)
    if serializer.is_valid():
        serializer.save()
        adminPassword = str(data['panNumber'])
        roleObject = Role.objects.create(Active=True,RoleName='Admin',company_code= data['companycode'])
        employeeRoleObject = Role.objects.create(Active=True,RoleName='Employee',company_code= data['companycode'])
        givePermission(data['companycode'],roleObject.id)
        uid = EmployeeCode(data['companycode'])
        # permissionObject = Permissions.objects.f
        createadminuser(data['memberadmin'],adminPassword,user_firstname,user_lastname,roleObject,data['companycode'],dob,uid)
        if period is not None and period != None and period != "":
            paymentlog(serializer.data['id'],period,current_date,serializer.data['expirydate'],serializer.data['payment'])
            N = 60
            res = ''.join(secrets.choice(str('!@#$%^&*') + string.ascii_lowercase + string.digits )
                    for i in range(N))
            apikeyObject = ApiKey.objects.create(api_key = res,company_code = data['companycode'],expiry_date=data['expirydate'])
        return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Company has been added successfully",
            "status": "success"
        }
    })


    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg": "Error adding Company",
            "status": "failure"
        }
    })

   
@api_view(['GET'])
@permission_classes((AllowAny,))
def companylistAPI(request):
    listdata = companyinfo.objects.filter(isactive=True).order_by('id')
    serializer = companyserializer(listdata,many=True)
    for i in serializer.data:
        if i['companylogos'] is not None:
            i['companylogos'] = imageUrl+i['companylogos']
        
        if i['gstcertificate'] is not None:
            i['gstcertificate'] = imageUrl+i['gstcertificate']

    return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "SUCCESS",
            "status": "success"
        }
    })


@api_view(['POST'])
def companybyidAPI(request):
    id = request.data.get('id')
    companylist = []
    comdata = companyinfo.objects.filter(isactive=True,id=id).first()
    companyUniqueCode(comdata.companyName)
    if comdata is not None:
        
        serializer = companyserializer(comdata)
        for i in [serializer.data]:
            if i['companylogos'] is not None:
                # i['actualpathlogo'] =  i['companylogos']
                i['companylogos'] = imageUrl+i['companylogos']
            
            if i['gstcertificate'] is not None:
                i['gstcertificate'] = imageUrl+i['gstcertificate']
           
            companylist.append(i)

            return Response({
            "data": companylist[0],
            "response": {
                "n": 1,
                "msg": "SUCCESS",
                "status": "success"
            }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "failed",
                "status": "id Not Found"
            }
            })


@api_view(['POST'])
def companybyidupdateAPI(request):
    data={}
    id = request.data.get('id')
    comdata = companyinfo.objects.filter(isactive=True,id=id).first()
    if comdata is not None:
        objserializer = companyserializer(comdata)
        if request.FILES != {}:
            if objserializer.data['companylogos'] is None or objserializer.data['companylogos'] == "":
                data['companylogos'] = request.FILES.get('companylogos')
            elif request.FILES.get('companylogos') is None:
                pass
            else:
                data['companylogos'] = request.FILES.get('companylogos')
            if objserializer.data['gstcertificate'] is None or objserializer.data['gstcertificate'] == "":
                data['gstcertificate'] = request.FILES.get('gstcertificate')
            elif request.FILES.get('gstcertificate') is None:
                pass
            else:
                data['gstcertificate'] = request.FILES.get('gstcertificate')
        data['companyName']=request.data.get('companyname')
        companyName = request.POST.get('companyname')
        data['companyAddress']=request.data.get('caddress')
        data['contact']=request.data.get('contact')
        data['gstNumber']=request.data.get('gstNumber')
        data['adhaarNumber']=request.data.get('adhaarNumber')
        data['panNumber']=request.data.get('panNumber')
        data['memberadmin']=request.data.get('memberadmin')
        data['companyType'] = request.data.get('companyType')
        period = request.POST.get('period')
        current_date = date.today()
        if period is not None:
            data['payment'] = request.POST.get('payment')
            data['period'] = request.POST.get('period')
            billobject = BillingPeriod.objects.filter(isActive=True)
            billSer = BillingPeriodSerializer(billobject,many=True)
            for b in billSer.data:        
                if period == b['period']:
                    data['expirydate'] = current_date + timedelta(days=int(b['duration']))
                    data['status'] = 'Done'
                    data['startdate'] = current_date
            # elif period == 'quaterly':
            #     data['expirydate'] = current_date + timedelta(days=90)
            #     data['status'] = 'Done'
            # elif period == 'half yearly':
            #     data['expirydate'] = current_date + timedelta(days=180)
            #     data['status'] = 'Done'
            # elif period == 'yearly':
            #     data['expirydate'] = current_date + timedelta(days=365)
            #     data['status'] = 'Done'            
        else:
            data['period'] = request.POST.get('period')
            data['status'] = 'Not Done'
        
        companyObject = companyinfo.objects.filter(isactive=True,companyName__in = [companyName.strip().capitalize(),companyName.strip(),companyName.title(),companyName.strip().upper()]).first() 
        # if companyObject.startdate is None:
        #     data['startdate'] = current_date
        if comdata.companyName != data['companyName'] and companyObject is not None:
            return Response({
            "data": {},
            "response": {
                "n": 0,
                "msg": "Comapany with this name already exists",
                "status": "failure"
            }
            })
        userObject = Users.objects.filter(is_active=True,email = data['memberadmin']).first()
        if userObject is not None and comdata.memberadmin != data['memberadmin']:
            return Response({
            "data": {},
            "response": {
                "n": 0,
                "msg": "Admin with this email id already exists",
                "status": "failure"
            }
            })

        serializer = companyserializer(comdata,data=data,partial=True)

        if serializer.is_valid():
            serializer.save()
            if period is not None and period != None and period != "":
                paymentlog(serializer.data['id'],period,current_date,serializer.data['expirydate'],serializer.data['payment'])
                N = 60
                res = ''.join(secrets.choice(str('!@#$%^&*') + string.ascii_lowercase + string.digits )
                        for i in range(N))
                apikeyObject = ApiKey.objects.create(api_key = res,company_code = serializer.data['companycode'],expiry_date=data['expirydate'])
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Company updated successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "could not update",
                "status": "failure"
            }
        })


@api_view(['POST'])
@permission_classes((AllowAny,))
def deletecompanyAPI(request):
    data={}
    id = request.data.get('id')
    comdata = companyinfo.objects.filter(isactive=True,id=id).first()
    if comdata is not None:
        data['isactive'] = False
        serializer = companyserializer(comdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "deleted successfully",
                "status": "success"
             }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "failure",
                    "status": "could nt delete"
                }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "failure",
                "status": "could nt delete"
            }
        })

@api_view(['POST'])
@permission_classes((AllowAny,))
def uploadpayslip(request):
    dataset = Dataset()
    new_product = request.FILES.get('myfile')
    imported_data = dataset.load(new_product.read(), format='xlsx')
    for data in imported_data:
        userId = data[0]
        name = data[1]
        amount = data [2]
        month = data [3]
        year = data[4]
        
        paymentslipobj = paymentslip.objects.filter(userId=userId,month=month,year=year).first()
        if paymentslipobj is None:
            paymentslip.objects.create(
                userId = userId,
                name = name,
                amount = amount,
                month = month,
                year=year
            )
        else:
            paymentslip.objects.filter(userId=userId,month=month,year=year).update(             
                amount = amount,
                name = name,
            )
    return Response({
    "data": '',
    "response": {
        "n": 1,
        "msg": "Success",
        "status": "File uploaded suucessfully"
        }
    })
        # else:
        #     paymentslip.objects.filter(userId=userId,month=month,year=year).update(             
        #         amount = amount,
        #     )
        #     return Response({
        #     "data": '',
        #     "response": {
        #         "n": 1,
        #         "msg": "Success",
        #         "status": "File uploaded suucessfully."
        #         }
        #     })


@api_view(['GET'])
@permission_classes((AllowAny,))
def getpaymentslip(request):
    userId = request.GET.get('userId')
    userObject = paymentslip.objects.filter(userId = userId) 
    if userObject.exists():
        userSerializer = paymentslipserializer(userObject,many=True)
        return Response({
                        "data": userSerializer.data,
                        "response": {
                            "n": 1,
                            "msg": "Success",
                            "status": "Data found succefully"
                            }
                        })
    return Response({
                    "data": '',
                    "response": {
                        "n": 0,
                        "msg": "Failed",
                        "status": "Data not found"
                        }
                    })

@api_view(['POST'])
def designationfileapi(request):
    try:
        dataset = Dataset()
        companycode = request.user.company_code
        new_designation_file = request.FILES.get('file')

        with new_designation_file.open('rb') as file_content:
            imported_data = dataset.load(file_content.read(), format='xlsx')

        uploadeddesignationlist = []
        notuploadeddesignationlist = []

        for data in imported_data:
            designation_name = data[0]
            desigexistobj = Designation.objects.filter(DesignationName=designation_name, company_code=companycode).first()

            if desigexistobj:
                notuploadeddesignationlist.append(desigexistobj.DesignationName)
            else:
                Designation.objects.create(
                    DesignationName=designation_name,
                    company_code=companycode
                )
                uploadeddesignationlist.append(designation_name)

        if notuploadeddesignationlist:
            return Response({
                "data": notuploadeddesignationlist,
                "response": {
                    "n": 0,
                    "status": "Failure",
                    "msg": "Designation File not uploaded"
                }
            })
        else:
            return Response({
                "data": uploadeddesignationlist,
                "response": {
                    "n": 1,
                    "status": "Success",
                    "msg": "Designation File uploaded successfully"
                }
            })
    except Exception as e:
        return Response({
            "data": str(e),
            "response": {
                "n": 0,
                "status": "Error",
                "msg": "An error occurred during file processing"
            }
        })    

@api_view(['POST'])
def departmentfileapi(request):
    dataset = Dataset()
    companycode = request.user.company_code
    new_department_file = request.FILES.get('file')
    notuploadeddeptlist = []
    imported_data = dataset.load(new_department_file.read(), format='xlsx')
    counter=0
    for data in imported_data:
        department_name = data[0]
        
        desigexistobj = Department.objects.filter(DepartmentName = department_name,company_code = companycode ).first()
        if desigexistobj:
            counter += 1
            notuploadeddeptlist.append(desigexistobj.DepartmentName)

    if counter == 0:
        for data in imported_data:
            department_name = data[0]
            Department.objects.create(
                DepartmentName = department_name,
                company_code = companycode 
            )
    else:
        return Response({
            "data": notuploadeddeptlist,
            "response": {
                "n": 0,
                "msg": "Failed",
                "status": "Department File not uploaded"
                }
            })

    return Response({
    "data": '',
    "response": {
        "n": 1,
        "msg": "Success",
        "status": "Department File uploaded suucessfully"
        }
    })

@api_view(['POST'])
def locationfileapi(request):
    dataset = Dataset()
    companycode = request.user.company_code
    new_location_file = request.FILES.get('file')
    notuploadeddeptlist = []
    imported_data = dataset.load(new_location_file.read(), format='xlsx')
    counter=0
    for data in imported_data:
        Location_Name = data[0]
        locationexistobj = Location.objects.filter(LocationName = Location_Name,company_code = companycode ).first()
        if locationexistobj :
            counter += 1
            notuploadeddeptlist.append(locationexistobj.LocationName)

    if counter == 0:
        for data in imported_data:
            Location_Name = data[0]
            Location.objects.create(
                LocationName = Location_Name,
                company_code = companycode
            )
    else:
        return Response({
            "data": notuploadeddeptlist,
            "response": {
                "n": 0,
                "msg": "Failed",
                "status": "Location File not uploaded suucessfully"
                }
            })

    return Response({
    "data": '',
    "response": {
        "n": 1,
        "msg": "Success",
        "status": "Location File uploaded suucessfully"
        }
    })

@api_view(['POST'])
def addEmployeeExcel(request):
    dataset = Dataset()
    companycode = request.user.company_code
    new_product = request.FILES.get('employeefile')
    if new_product is not None and new_product !="":
        imported_data = dataset.load(new_product.read(), format='xlsx')

        userid=request.user.id
        userlist = []
        rolelist=[]
        designationlist = []
        departmentlist = []
        locationlist=[]


        counter = 0
        existcounter =0
        for data in imported_data:
            email = data[4]
            firstname = data[0]
            lastName = data[1]
            fullname = firstname + " "+ lastName
            empexist =Users.objects.filter(email=data[4],is_active=True,company_code = companycode).first()
            if empexist:
                counter += 1
                userlist.append(fullname)

            role = data[7]
            roleObject = Role.objects.filter(RoleName=role,Active=True,company_code = companycode ).first()
            if roleObject is None:
                existcounter += 1
                rolelist.append(role)

            department = data[9]
            departmentObject = Department.objects.filter(DepartmentName=department,Active=True,company_code = companycode ).first()
            if departmentObject is None:
                existcounter += 1
                departmentlist.append(department)


            designation = data[8]
            designationObject = Designation.objects.filter(DesignationName=designation,company_code = companycode ).first()
            if designationObject is None:
                existcounter += 1
                designationlist.append(designation)

            location = data[11]
            locationObject = Location.objects.filter(LocationName = location,Active=True,company_code = companycode ).first()
            if locationObject is None:
                existcounter += 1
                locationlist.append(location)


        if counter != 0:
            return Response({
            "data":userlist,
            "response": {
                "n": 0,
                "status": "Failed ",
                "msg": "Employees File not uploaded ",
                }
            })  
        elif existcounter !=0:
            return Response({
                "data":rolelist + designationlist + departmentlist + locationlist,
                "response": {
                    "n": 2,
                    "status": "Failed ",
                    "msg": "Employees File not uploaded",
                    }
            })
        else:
            for data in imported_data:
                firstName = data[0]
                lastName = data[1]
                phoneNumber = data[2]
                dob = str(data[3]).split(" ")[0]
                birthDateSplit = dob.split("-")
                birth_date = birthDateSplit[0] +"-" + birthDateSplit [1] +"-" + birthDateSplit[2]
                email = data[4]
                address = data[5]
                gender = data[6]
                empgender = ""
                if gender == "Male" or gender == "male" or gender == "M" or gender == "MALE":
                    empgender = "M"
                else:
                    empgender = "F" 
                role = data[7]
                roleObject = Role.objects.filter(RoleName__in=[role.strip().capitalize(),role.strip(),role.title(),role.lower()],Active=True,company_code = companycode ).first()
                if roleObject is None:
                    rolemsg = 'Add this Role ('+role+") first"
                designation = data[8]
                designationObject = Designation.objects.filter(DesignationName__in=[designation.strip().capitalize(),designation.strip(),designation.title(),designation.lower()],company_code = companycode ).first()
                if designationObject is None:
                    desgmsg = 'Add this Designation ('+designation+") first"
                department = data[9]
                departmentObject = Department.objects.filter(DepartmentName__in=[department.strip().capitalize(),department.strip(),department.title(),department.lower()],Active=True,company_code = companycode ).first()
                if departmentObject is None:
                    deptmsg = 'Add this Department ('+department+") first"
                doj = str(data[10]).split(" ")[0]
                joiningDateSplit = doj.split("-")
                joining_date = joiningDateSplit[0] +"-" + joiningDateSplit [1] +"-" + joiningDateSplit[2]

                location = data[11]
                locationObject = Location.objects.filter(LocationName = location,Active=True,company_code = companycode ).first()
                if locationObject is None:
                    locmsg = 'Add this location ('+location+") first"

                userPassword = "123"
            
                user_save = Users.objects.create(
                                            Firstname = firstName,
                                            Lastname = lastName,
                                            Phone = phoneNumber,
                                            BirthDate = birth_date,
                                            email = email,
                                            Address = address,
                                            Gender = empgender,
                                            RoleID = roleObject,
                                            DesignationId=designationObject,                                            
                                            DateofJoining = joining_date,
                                            password = make_password(userPassword),
                                            Password = "123",
                                            company_code=companycode,
                                            locationId = locationObject
                    )
                user_save.DepartmentID.set([departmentObject])
            userobj=Users.objects.filter(id=userid).update(masters=True)
            return Response({
            "data":userlist,
            "response": {
                "n": 1,
                "status": "Success ",
                "msg":"Employee Added successfully",
                }
            })       
    else:
        return Response({
                "data":{},
                "response": {
                    "n": 0,
                    "status": "failed ",
                    "msg":"please provide valid excel file",
                    }
                }) 
        

@api_view(['POST'])
def AddBillingPeriod(request):
    data = {}
    period = request.POST.get('period')
    data['period'] = period.strip().lower()
    data['amount'] = request.POST.get('amount')
    data['duration'] = request.POST.get('duration')
    billingObject = BillingPeriod.objects.filter(isActive=True,period = data['period']).first()
    if billingObject is None:
        serializer = BillingPeriodSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Plan period added successfully",
                "status": "success"
             }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "Error saving data",
                    "status": "Failed"
                }
            })
    else:
        serializer = BillingPeriodSerializer(billingObject,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Plan period updated successfully",
                "status": "success"
             }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "Error updating data",
                    "status": "Failed"
                }
            })

@api_view(['GET'])
def BillingPeriodlist(request):
    billingperiodobject = BillingPeriod.objects.filter(isActive=True).order_by('id')
    if billingperiodobject is not None:
        serializer = BillingPeriodSerializer(billingperiodobject,many=True)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Plan period list found successfully",
                "status": "success"
             }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "No period yet",
                "status": "Failed"
            }
        })

@api_view(['POST'])
def updatePlanPeriod(request):
    data = {}
    data['id'] = request.POST.get('id')    
    period = request.POST.get('period')
    data['period'] = period.lower().strip()
    data['amount'] = request.POST.get('amount')
    data['duration'] = request.POST.get('duration')
    periodnameObject = BillingPeriod.objects.filter(isActive=True,period = data['period']).first()
    periodObject = BillingPeriod.objects.filter(isActive=True,id = data['id']).first()
    if periodObject.period != data['period'] and periodnameObject is not None :
        return Response({
                "data": '',
                "response": {
                    "n": 0,
                    "msg": "Plan type already exists",
                    "status": "Failed"
                }
            })

    if periodObject is not None:
        serializer = BillingPeriodSerializer(periodObject,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Plan updated successfully",
                "status": "success"
                }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "Error updating data",
                    "status": "Failed"
                }
            })
    else:
        return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Error founding data",
                    "status": "Failed"
                }
            })

@api_view(['POST'])
def BillingPeriodbyid(request):
    period = request.POST.get('period')
    billingperiodobject = BillingPeriod.objects.filter(isActive=True,period = period).first()
    if billingperiodobject is not None:
        serializer = BillingPeriodSerializer(billingperiodobject)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Plan period found successfully",
                "status": "success"
             }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "No period yet",
                "status": "Failed"
            }
        })

@api_view(['GET'])
def billingPerioddetails(request): 
    period_id = request.GET.get('period_id')
    billingperiodobject = BillingPeriod.objects.filter(isActive=True,id = period_id).first()
    if billingperiodobject is not None:
        serializer = BillingPeriodSerializer(billingperiodobject)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Plan period found successfully",
                "status": "success"
             }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "No period yet",
                "status": "Failed"
            }
        })


@api_view(['POST'])
def AddCompanytype(request):
    data = {}
    companyType = request.POST.get('companyType')
    data['companyType'] = companyType.strip().lower()
    comtypeObject = CompanyType.objects.filter(isActive=True,companyType = data['companyType']).first()
    if comtypeObject is None:
        serializer = CompanytypeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Company Type added successfully",
                "status": "success"
             }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "Error saving data",
                    "status": "Failed"
                }
            })
    else:
        serializer = CompanytypeSerializer(comtypeObject,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Company Type updated successfully",
                "status": "success"
             }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "Error updating data",
                    "status": "Failed"
                }
            })



@api_view(['POST'])
def updateCompanyType(request):
    data = {}
    data['id'] = request.POST.get('id')    
    companytype = request.POST.get('companyType')
    data['companyType'] = companytype.lower().strip()
    companyTypenameObject = CompanyType.objects.filter(isActive=True,companyType = data['companyType']).first()
    comtypeObject = CompanyType.objects.filter(isActive=True,id = data['id']).first()
    if comtypeObject.companyType != data['companyType'] and companyTypenameObject is not None :
        return Response({
                "data": '',
                "response": {
                    "n": 0,
                    "msg": "Company type already exists",
                    "status": "Failed"
                }
            })

    if comtypeObject is not None:
        serializer = CompanytypeSerializer(comtypeObject,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Company Type updated successfully",
                "status": "success"
                }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "Error updating data",
                    "status": "Failed"
                }
            })
    else:
        return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Error founding data",
                    "status": "Failed"
                }
            })



@api_view(['GET'])
def Companytypelist(request):
    companytypeobject = CompanyType.objects.filter(isActive=True).order_by('id')
    CompanyTypeList=[]
    if companytypeobject is not None:
                



        serializer = CompanytypeSerializer(companytypeobject,many=True)
        for i in serializer.data:
            company_obj = companyinfo.objects.filter(companyType=i['companyType'],isactive=True)
            companys_serializer=companyserializer(company_obj,many=True)
            if len(companys_serializer.data) > 0:
                i['Used']=True
            else:
                i['Used']=False
            CompanyTypeList.append(i)

        return Response({
            "data": CompanyTypeList,
            "response": {
                "n": 1,
                "msg": "Comapany Type list found successfully",
                "status": "success"
             }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "No period yet",
                "status": "Failed"
            }
        })



@api_view(['GET'])
def Companyleadlist(request):
    activeCompanyList = []
    inactiveCompanyList = []
    current_date = date.today()
    companyincompleteobject = companyinfo.objects.filter(isactive=True,startdate=None).order_by('id')
    incompleteSerializer = companyserializer(companyincompleteobject,many=True)
    for i in incompleteSerializer.data:
        i['created_at'] = i['created_at'].split('T')[0]
    companyActiveobject = companyinfo.objects.filter(isactive=True).exclude(expirydate=None).order_by('id')
    activecompanySerializer = companyserializer(companyActiveobject,many=True)
    for i in activecompanySerializer.data:        
        i['created_at'] = i['created_at'].split('T')[0]
        exp_date = datetime.datetime.strptime(str(i['expirydate']), "%Y-%m-%d").date()
        if exp_date > current_date:
            activeCompanyList.append(i)
        else:
            inactiveCompanyList.append(i)
    return Response({
            "active": activeCompanyList,
            "inactive": inactiveCompanyList,
            "incomplete": incompleteSerializer.data,
            "response": {
                "n": 1,
                "msg": "Leads have been fetched successfully",
                "status": "success"
             }
            })

@api_view(['POST'])
def addcompanypayment(request):
    N = 60
    res = ''.join(secrets.choice(str('!@#$%^&*') + string.ascii_lowercase + string.digits )
              for i in range(N))
    data = {}
    data['companyId'] = request.POST.get('companyId')
    period = request.POST.get('planperiod')
    companyObject = companyinfo.objects.filter(id = data['companyId'],isactive=True).first()
    comapnyExpiryDate = companyObject.expirydate
    comExyear = str(comapnyExpiryDate).split("-")[0] 
    comExmonth = str(comapnyExpiryDate).split("-")[1] 
    comExdate = str(comapnyExpiryDate).split("-")[2] 
    current_date = date.today()
    cuyear = str(current_date).split("-")[0] 
    cumonth = str(current_date).split("-")[1] 
    cudate = str(current_date).split("-")[2] 
    d0 = date(int(comExyear), int(comExmonth), int(comExdate))
    d1 = date(int(cuyear), int(cumonth), int(cudate))
    delta = d1 - d0
    differenceDays = delta.days
    if differenceDays >= -15 :
        if period is not None and period != None:
            
            data['payment'] = request.POST.get('payment')
            data['planperiod'] = request.POST.get('planperiod')
            data['startdate'] = current_date
            if period == 'monthly':
                data['expirydate'] = current_date + timedelta(days=30)
            elif period == 'quaterly':
                data['expirydate'] = current_date + timedelta(days=90)
            elif period == 'haly yearly':
                data['expirydate'] = current_date + timedelta(days=180)
            else:
                data['expirydate'] = current_date + timedelta(days=365)
            
            companyObj = companyinfo.objects.filter(id = data['companyId']).first()
            if companyObj is not None:
                companyinfo.objects.filter(id=data['companyId']).update(
                period = request.POST.get('planperiod'),
                expirydate = data['expirydate']
                )
            companyApiObject = ApiKey.objects.filter(company_code = companyObj.companycode).update(
                isActive = False
            )
            ApiKey.objects.create(
                api_key = res,
                company_code = companyObj.companycode,
                expiry_date = data['expirydate']
            )
            serializer = CompanypaymentlogSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Payment added successfully",
                    "status": "success"
                }
                })
            else:
                return Response({
                    "data": serializer.errors,
                    "response": {
                        "n": 0,
                        "msg": "Error updating data",
                        "status": "Failed"
                    }
                })

    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "Plan yet not expired",
                "status": "Failed"
            }
        })

@api_view(['GET'])
def Companypaymentloglist(request):
    companyObj = companyinfo.objects.filter(isactive=True).exclude(expirydate=None).order_by('id')
    companySerializer = companyserializer(companyObj,many=True)
    def convertddmmyy(date_str):
        if date_str is not None and date_str !='':

            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%m-%Y")
            return formatted_date
        else:
            return ''

    companypaymentlogObj = companypaymentlog.objects.all().order_by('-id')
    companypaymentlogSer = CompanypaymentlogSerializer(companypaymentlogObj,many=True)
    for t in companypaymentlogSer.data:
        companynameobj =  companyinfo.objects.filter(id=t['companyId'],isactive=True).first()
        t['startdate'] = convertddmmyy(t['startdate'])
        t['expirydate'] = convertddmmyy(t['expirydate']) 
        if companynameobj is not None:
            t['compname'] = companynameobj.companyName


    return Response({
                "companylist": companySerializer.data,
                "companypaymentlist": companypaymentlogSer.data,
                "response": {
                    "n": 1,
                    "msg": "Payment added successfully",
                    "status": "success"
                }
                })

@api_view(['GET'])
def particualrcompanypaymentlog(request):
    if request.GET.get('companyId') is not None and request.GET.get('companyId') !="":
        companyId = request.GET.get('companyId')
    else:
        companyId = request.data.get('companyId')
    if companyId :
        companypaymentlogObj = companypaymentlog.objects.filter(companyId = companyId)
        companypaymentlogSer = CompanypaymentlogSerializer(companypaymentlogObj,many=True)
        return Response({"data": companypaymentlogSer.data,"response": {"n": 1,"msg": "Payment fetched successfully","status": "success"}})
    else:
        return Response({"data": [],"response": {"n": 0,"msg": "please provide company id","status": "fail"}})
    

    
@api_view(['GET'])
def remindercompanylist(request):
    reminderactiveList =[]
    reminderInactiveList = []
    current_date = date.today()
    nopaymentComobj = companyinfo.objects.filter(isactive=True,expirydate=None).order_by('id')
    nopaymentSer = companyserializer(nopaymentComobj,many=True)
    for t in nopaymentSer.data:
        t['created_at'] = t['created_at'].split('T')[0]    

    companyInActiveobject = companyinfo.objects.filter(isactive=True).exclude(expirydate=None).order_by('id')
    inactivecompanySerializer = companyserializer(companyInActiveobject,many=True)
    for c in inactivecompanySerializer.data:    
        c['created_at'] = c['created_at'].split('T')[0]    
        exp_date = datetime.datetime.strptime(str(c['expirydate']), "%Y-%m-%d").date()
        if exp_date < current_date:
            reminderInactiveList.append(c)

    companyObject = companyinfo.objects.filter(isactive=True).exclude(expirydate=None).order_by('id')
    if companyObject is not None:
        companySerializer = companyserializer(companyObject,many=True)
        for i in companySerializer.data:
            i['created_at'] = i['created_at'].split('T')[0]
            exp_date = datetime.datetime.strptime(str(i['expirydate']), "%Y-%m-%d").date()
            differenceindate = exp_date - current_date
            stripdiff = str(differenceindate).split(',')[0].split(' ')[0]
            if 0 <= int(stripdiff) < 15 :
                reminderactiveList.append(i)

        return Response({
                    "reminderactiveList": reminderactiveList,
                    "reminderincompleteList": nopaymentSer.data,
                    "reminderInactiveList":reminderInactiveList,
                    "response": {
                        "n": 1,
                        "msg": "List fetched  successfully",
                        "status": "success"
                    }
                    })
    else:
        return Response({
                    "data": "",
                    "response": {
                        "n": 0,
                        "msg": "List not fetched",
                        "status": "failed"
                    }
                    })

@api_view(['POST'])
def sendremindermail(request):
    companyId = request.POST.get('companyId')
    current_date = date.today()
    companyObject = companyinfo.objects.filter(isactive = True,id=companyId).first()    

    if companyObject is not None:
        userObject = Users.objects.filter(email = companyObject.memberadmin).first()
        if companyObject.expirydate is not None:
            exp_date = datetime.datetime.strptime(str(companyObject.expirydate), "%Y-%m-%d").date()
            differenceindate = exp_date - current_date
            stripdiff = str(differenceindate).split(',')[0].split(' ')[0]           
            if exp_date < current_date:
                TaskNotification.objects.create(
                    NotificationTitle = "Reminder",
                    NotificationMsg = "Your plan has expired on " + str(exp_date) + ". Please renew your pack.",
                    UserID_id = userObject.id,
                    NotificationTypeId_id = 1 ,
                    created_by = request.user.id,
                    company_code = request.user.company_code
                )
                inactive = companyserializer(companyObject)
                subject = "Reminder"
                data2 = {"subject": subject,"email":companyObject.memberadmin,'companyinfo':inactive.data,
                        "template": 'mails/inactivereminder.html'}
                message = render_to_string(
                    data2['template'], data2)
                send_mail(data2, message)

            elif 0 <= int(stripdiff) < 15 :
                notificatiionObject = TaskNotification.objects.filter(UserID=userObject.id,CreatedOn__icontains=current_date,NotificationTitle='Reminder').first()
                if notificatiionObject is None:
                    TaskNotification.objects.create(
                        NotificationTitle = "Reminder",
                        NotificationMsg = "Your plan will expire soon on " + str(exp_date) + ". Please renew your pack as soon as possible.",
                        UserID_id = userObject.id,
                        NotificationTypeId_id = 1 ,
                        created_by = request.user.id,
                        company_code = request.user.company_code
                    )
                    active = companyserializer(companyObject)
                    subject = "Reminder"
                    data2 = {"subject": subject,"email":companyObject.memberadmin,'companyinfo':active.data,
                            "template": 'mails/activereminder.html'}
                    message = render_to_string(
                        data2['template'], data2)
                    send_mail(data2, message)
                else:
                    return Response({
                    "data": "",
                    "response": {
                        "n": 0,
                        "msg": "Reminder has been already sent",
                        "status": "failed"
                    }
                    })

        else:
            incomplete = companyserializer(companyObject)
            subject = "Reminder"
            data2 = {"subject": subject,"email":companyObject.memberadmin,'companyinfo':incomplete.data,
                    "template": 'mails/incompletereminder.html'}
            message = render_to_string(
                data2['template'], data2)
            send_mail(data2, message)

        return Response({
                    "data": "",
                    "response": {
                        "n": 1,
                        "msg": "Reminder Mail sent successfully",
                        "status": "success"
                    }
                    })
    return Response({
                    "data": "",
                    "response": {
                        "n": 0,
                        "msg": "Comapany not found",
                        "status": "failed"
                    }
                    })

@api_view(['GET'])
def sendActiveReminder(request):
    activeList = []
    userList = []
    current_date = date.today()
    companyObject = companyinfo.objects.filter(isactive = True).exclude(expirydate=None)
    companySer = companyserializer(companyObject,many=True)
    for c in companySer.data:
        exp_date = datetime.datetime.strptime(str(c['expirydate']), "%Y-%m-%d").date()
        differenceindate = exp_date - current_date
        stripdiff = str(differenceindate).split(',')[0].split(' ')[0] 
        if 0 <= int(stripdiff) < 15 : 
            userObject = Users.objects.filter(email = c['memberadmin'])
            userSerializer = userUpdateSerializer(userObject,many=True)
            for u in userSerializer.data:
                notificatiionObject = TaskNotification.objects.filter(UserID=u['id'],CreatedOn__icontains=current_date,NotificationTitle='Reminder').first()
                if notificatiionObject is None:
                    userList.append(u['email'])
                    TaskNotification.objects.create(
                    NotificationTitle = "Reminder",
                    NotificationMsg = "Your plan will expire soon on " + str(exp_date) + ". Please renew your pack as soon as possible.",
                    UserID_id = u['id'],
                    NotificationTypeId_id = 1 ,
                    created_by = request.user.id,
                    company_code = request.user.company_code
                    )
                    subject = "Reminder"
                    data2 = {"subject": subject,"email":u['email'],'companyinfo':companySer.data,
                            "template": 'mails/activereminder.html'}
                    message = render_to_string(
                        data2['template'], data2)
                    send_mail(data2, message)
        
            

            # activeList.append(c)
    for s in userList:
        comobject = companyinfo.objects.filter(memberadmin=s)
        comSer = companyserializer(comobject,many=True)
        for r in comSer.data:
            TaskNotification.objects.create(
                        NotificationTitle = "Reminder",
                        NotificationMsg = str(r['companyName']) + " plan will expire soon on " + str(exp_date),
                        UserID_id = 1,
                        NotificationTypeId_id = 1 ,
                        created_by = request.user.id,
                        company_code = request.user.company_code
                        )


    return Response({
                    "data": activeList,
                    "response": {
                        "n": 1,
                        "msg": "Mail Sent successfully",
                        "status": "success"
                    }
                    })
            








@api_view(['POST'])
@permission_classes((AllowAny,))
def delete_company_type(request):
    data={}
    id = request.data.get('id')
    comdata = CompanyType.objects.filter(isActive=True,id=id).first()
    if comdata is not None:
        data['isActive'] = False
        serializer = CompanytypeSerializer(comdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "deleted successfully",
                "status": "success"
             }
            })
        else:
            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": "failure",
                    "status": "could nt delete"
                }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "failure",
                "status": "could nt delete"
            }
        })

@api_view(['GET'])
def companycountdashboard(request):
    activeCompanyList=[]
    inactiveCompanyList=[]
    current_date = date.today()

    companycount = companyinfo.objects.filter(isactive=True).count()
    incompletecount= companyinfo.objects.filter(isactive=True,startdate=None).count()
    companyActiveobject = companyinfo.objects.filter(isactive=True).exclude(expirydate=None).order_by('id')
    activecompanySerializer = companyserializer(companyActiveobject,many=True)
    for i in activecompanySerializer.data:        
        i['created_at'] = i['created_at'].split('T')[0]
        exp_date = datetime.datetime.strptime(str(i['expirydate']), "%Y-%m-%d").date()
        if exp_date > current_date:
            activeCompanyList.append(i)
        else:
            inactiveCompanyList.append(i)

    activecompanycount = len(activeCompanyList)
    inactivecompanycount = len(inactiveCompanyList)

    context={
        'totalcompanies':companycount,
        'activecompanies':activecompanycount,
        'inactivecompanies':inactivecompanycount,
        'incompletecompanies':incompletecount
    }
    return Response({
            "data": context,
            "response": {
                "n": 1,
                "msg": "success",
                "status": "success"
             }
            })

@api_view(['GET'])
def CompanyYearlyIncome(request):
    todays_date = date.today()
    currentyear = todays_date.year

    yearlist = []
    yearnamelist = []
    paymentlist = []

    year = datetime.datetime.today().year
    yearlist = [year - i for i in range(5)]
    for i in yearlist:
        payment = 0
        paymentobject = companypaymentlog.objects.filter(isActive=True,startdate__year = i)
        paymentser = CompanypaymentlogSerializer(paymentobject,many=True)
        for p in paymentser.data:
            if p['payment'] is not None and p['payment'] != "":
                payment += float(p['payment'])
       
        yearnamelist.append(str(i))
        paymentlist.append(payment)

    yearnamelist.reverse()
    paymentlist.reverse()

    context={
        'yearrlist':yearnamelist,
        'paymentlist':paymentlist,
    }

    return Response({
            "data": context,
            "response": {
                "n": 1,
                "msg": "success",
                "status": "success"
             }
            })

@api_view(['POST'])
def CompanyLeadsGraph(request):
    todays_date = date.today()
    currentyear = todays_date.year

    ajaxyear = request.POST.get("year")
    if ajaxyear is not None:
        ajaxyear = ajaxyear
    else:
        ajaxyear = currentyear

    leadscountlist = []
    monthlydata = []
    monthlabellist =[]

    monthlist = [{
        "month":"Jan","monthnumber":1},
        {"month":"Feb","monthnumber":2},
        {"month":"Mar","monthnumber":3},
        {"month":"Apr","monthnumber":4},
        {"month":"May","monthnumber":5},
        {"month":"Jun","monthnumber":6},
        {"month":"Jul","monthnumber":7},
        {"month":"Aug","monthnumber":8},
        {"month":"Sept","monthnumber":9},
        {"month":"Oct","monthnumber":10},
        {"month":"Nov","monthnumber":11},
        {"month":"Dec","monthnumber":12}]
    for i in monthlist:
        companyobject = companyinfo.objects.filter(isactive=True,startdate__year=ajaxyear,startdate__month = i['monthnumber']).exclude(expirydate=None)
        monthlabellist.append(i['month'])
        leadscountlist.append(companyobject.count())
    
    context = {
        'monthlabellist' : monthlabellist,
        'leadslist':leadscountlist
    }
    
    return Response({
            "data": context,
            "response": {
                "n": 1,
                "msg": "success",
                "status": "success"
             }
            })






@api_view(['POST'])
def companypackages(request):
    companyperiodfilter = request.POST.get("companyperiodfilter")
    if companyperiodfilter is None or companyperiodfilter == "":
        companyobject = companyinfo.objects.filter(isactive=True)
    else:
        companyobject = companyinfo.objects.filter(isactive=True,period = companyperiodfilter)
    if companyobject is not None:
        serializer = companyserializer(companyobject,many=True)
        for i in serializer.data:
            if i['companylogos'] is not None:
                i['companyphoto'] = imageUrl + str(i['companylogos'])
            else:
                i['companyphoto'] =  imageUrl + "/static/admin/dashboard/Media/TrackProRankingCard/profile_picture_1.png"

           

        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "success",
                "status": "success"
             }
            })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "failure",
                "status": "failure"
             }
            })





    
