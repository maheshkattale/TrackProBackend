from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from rest_framework.decorators import authentication_classes, permission_classes
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework import status



# Create your views here.


@api_view(['POST'])
def addclient(request):
    data={}
    clientname = request.POST.get("Client_Name")
    data['ClientName'] = clientname
    data['company_code']=request.user.company_code

    clientobj = Client.objects.filter(ClientName__in = [clientname.strip().capitalize(),clientname.strip(),clientname.title()],company_code = data['company_code'],is_active=True).first()
    if clientobj is not None:
        return Response({"data":'',"n":0,"Msg":"Client Already exist.","Status":"Failed"})
    else:
        serializer = Clientserializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Client added successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Client not added","Status":"Failed"})



@api_view(['GET'])
def clientlist(request):
    clientobjs = Client.objects.filter(is_active=True).order_by('-id')
    clienser = Clientserializer(clientobjs,many=True)
    return Response({"data":clienser.data,"n":1,"Msg":"List fetched successfully","Status":"Success"})


@api_view(['POST'])
def getclient(request):
    id = request.query_params.get('clientID', None)
    if id is not None:
        i = Client.objects.filter(id=id,company_code=request.user.company_code)
        if i is not None:
            serializer = Clientserializer(i, many=True)
            return Response({"data":serializer.data,"n":1,"Msg":"List fetched successfully","Status":"Success"})
        else:
            return Response({"data":'',"n":0,"Msg":"client not found","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"client ID not fetched","Status":"Failed"})


@api_view(['POST'])
def updateclient(request):
    data={}
    id = request.query_params.get('clientID', None)
    obj = Client.objects.filter(id=id,company_code=request.user.company_code).first()
    if obj is not None:
        clientname = request.POST.get("Client_Name")
        data['ClientName'] = request.POST.get("Client_Name")
        data['company_code']=request.user.company_code
        clientobj = Client.objects.filter(ClientName__in = [clientname.strip().capitalize(),clientname.strip(),clientname.title()],company_code = data['company_code'],is_active=True).exclude(id=id).first()
        if clientobj is not None:
            return Response({"data":'',"n":0,"Msg":"Client Already exist.","Status":"Failed"})
        else:
            serializer = Clientserializer(obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"n":1,"Msg":"Client added successfully","Status":"Success"})
            else:
                return Response({"data":serializer.errors,"n":0,"Msg":"Client not updated","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"client not found","Status":"Failed"})
    

@api_view(['POST'])
def deleteclient(request):
    data={}
    id = request.query_params.get('clientID', None)
    objdata=Client.objects.filter(id=id).first()
    if objdata is not None:
        data['is_active'] = False
        serializer = Clientserializer(objdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Client deleted successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Client not deleted","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"Client not found","Status":"Failed"})
    


#------------------------------------client side manager---------------------------------------------

@api_view(['POST'])
def addClientsideManager(request):
    data={}
    ManagerName = request.POST.get("Manager_Name")
    data['ManagerName'] = ManagerName
    data['company_code']=request.user.company_code

    managerobj = ClientsideManager.objects.filter(ManagerName__in = [ManagerName.strip().capitalize(),ManagerName.strip(),ManagerName.title()],company_code = data['company_code'],is_active=True).first()
    if managerobj is not None:
        return Response({"data":'',"n":0,"Msg":"Manager Already exist.","Status":"Failed"})
    else:
        serializer = ClientsideManagerserializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Manager added successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Manager not added","Status":"Failed"})
    


@api_view(['GET'])
def ClientsideManagerlist(request):
    managerobjs = ClientsideManager.objects.filter(is_active=True).order_by('-id')
    managerser = ClientsideManagerserializer(managerobjs,many=True)
    return Response({"data":managerser.data,"n":1,"Msg":"List fetched successfully","Status":"Success"})


@api_view(['GET'])
def getClientsideManager(request):
    id = request.query_params.get('ManagerID', None)
    if id is not None:
        i = ClientsideManager.objects.filter(id=id,company_code=request.user.company_code)
        if i is not None:
            serializer = ClientsideManagerserializer(i, many=True)
            return Response({"data":serializer.data,"n":1,"Msg":"List fetched successfully","Status":"Success"})
        else:
            return Response({"data":'',"n":0,"Msg":"Manager not found","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"Manager ID not fetched","Status":"Failed"})


@api_view(['POST'])
def updateClientsideManager(request):
    data={}
    id = request.query_params.get('ManagerID', None)
    obj = ClientsideManager.objects.filter(id=id,company_code=request.user.company_code).first()
    if obj is not None:
        ManagerName = request.POST.get("Manager_Name")
        data['ManagerName'] = request.POST.get("Manager_Name")
        data['company_code']=request.user.company_code

        managerobj = ClientsideManager.objects.filter(ManagerName__in = [ManagerName.strip().capitalize(),ManagerName.strip(),ManagerName.title()],company_code = data['company_code'],is_active=True).exclude(id=id).first()
        if managerobj is not None:
            return Response({"data":'',"n":0,"Msg":"Manager Already exist.","Status":"Failed"})
        else:
            serializer = ClientsideManagerserializer(obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"n":1,"Msg":"Manager updated successfully","Status":"Success"})
            else:
                return Response({"data":serializer.errors,"n":0,"Msg":"Manager not updated","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"Manager not found","Status":"Failed"})
    

@api_view(['POST'])
def deleteClientsideManager(request):
    data={}
    id = request.query_params.get('ManagerID', None)
    objdata=ClientsideManager.objects.filter(id=id).first()
    if objdata is not None:
        data['is_active'] = False
        serializer = ClientsideManagerserializer(objdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Manager deleted successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Manager not deleted","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"Manager not found","Status":"Failed"})
    
#----------------------------------------create client--------------------------------------------
@api_view(['POST'])
def createClient(request):

    data={}
    data['ClientId'] = request.POST.get("ClientId")
    data['Team']=request.POST.getlist("Team")
    data['Client_ManagerId']=request.POST.getlist("Client_ManagerId")
    data['SPOC_Person']=request.POST.get("SPOC_Person")
    data["company_code"]=request.user.company_code

    if data['ClientId'] is None or data['ClientId'] == "":
        data['ClientId'] = request.data.get("ClientId")

    if data['Team'] is None or data['Team'] == []:
        data['Team']=request.data.get("Team")

    if data['Client_ManagerId'] is None or data['Client_ManagerId'] ==[]:
        data['Client_ManagerId']=request.data.get("Client_ManagerId")

    if data['SPOC_Person'] is None or data['SPOC_Person'] =="":
        data['SPOC_Person']=request.data.get("SPOC_Person")







    obj = CreateClient.objects.filter(ClientId = data['ClientId'],company_code = data['company_code'],is_active=True).first()
    if obj is not None:
        return Response({"data":'',"n":0,"Msg":"Client already exist","Status":"failed"})
    else:
        serializer = createClientserializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Client Created successfully!","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Client  Creation unsuccessful!","Status":"Failed"})


@api_view(['GET'])
def createClientlist(request):
    allobjs = CreateClient.objects.filter(is_active=True).order_by('-id')
    serializer = getcreateClientserializer(allobjs,many=True)
    for i in serializer.data:
        clientid = i['ClientId']

        userobj = Client.objects.filter(id=clientid).first()
        if userobj is not None:
            i['ClientName'] = userobj.ClientName 

            spocid = i['SPOC_Person']
            userobjs = Users.objects.filter(id=spocid).first()
            if userobjs is not None:
                i['SPOC_PersonName'] = userobjs.Firstname + " " + userobjs.Lastname
            else:
                i['SPOC_PersonName'] = "---"
        else:
            i['ClientName'] = "---" 

            spocid = i['SPOC_Person']
            userobjs = Users.objects.filter(id=spocid).first()
            if userobjs is not None:
                i['SPOC_PersonName'] = userobjs.Firstname + " " + userobjs.Lastname
            else:
                i['SPOC_PersonName'] = "---"

    return Response({"data":serializer.data,"n":1,"Msg":"List fetched successfully","Status":"Success"})


@api_view(['POST'])
def getCreateClient(request):
    id = request.query_params.get('ID', None)
    if id is not None:
        i = CreateClient.objects.filter(ClientId=id,company_code=request.user.company_code,is_active=True)
        if i is not None:
            serializer = createClientserializer(i,many=True)
            for s in serializer.data:

                if s['Team'] is not None :
                    teamlist = []
                    for t in s['Team']:
                        teamdict={}
                        teamdict['id'] = t
                        empnameobj = Users.objects.filter(id=t).first()
                        teamdict['empname'] = empnameobj.Firstname + " " + empnameobj.Lastname
                        teamlist.append(teamdict)

                    s['teamlist'] = teamlist

                if s['Client_ManagerId'] is not None:
                    managerlist = []
                    for m in s['Client_ManagerId']:
                        managerdict={}
                        managerdict['id'] = m
                        mannameobj = ClientsideManager.objects.filter(id=m).first()
                        managerdict['managername'] = mannameobj.ManagerName
                        managerlist.append(managerdict)

                    s['managerlist'] = managerlist
                    
                if s['ClientId'] is not None:
                    projectobj=Client_Project.objects.filter(ClientId=s['ClientId'],is_active=True,company_code=request.user.company_code)
                    project_serializer=Client_Projectserializer(projectobj,many=True)
                    s['projectlist']=project_serializer.data

            return Response({"data":serializer.data,"n":1,"Msg":"Data fetched successfully","Status":"Success"})
        else:
            return Response({"data":'',"n":0,"Msg":"Data not found","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"ID not fetched","Status":"Failed"})
    


@api_view(['POST'])
def updateCreateClient(request):
    data={}
    id = request.query_params.get('ID', None)
    obj = CreateClient.objects.filter(id=id,company_code=request.user.company_code).first()
    if obj is not None:
        data['ClientId'] = request.POST.get("ClientId")
        data['Team']=request.POST.getlist("Team")
        data['Client_ManagerId']=request.POST.getlist("Client_ManagerId")
        data['SPOC_Person']=request.POST.get("SPOC_Person")
        data["company_code"]=request.user.company_code

        if data['ClientId'] is None or data['ClientId'] == "":
            data['ClientId'] = request.data.get("ClientId")

        if data['Team'] is None or data['Team'] == []:
            data['Team']=request.data.get("Team")

        if data['Client_ManagerId'] is None or data['Client_ManagerId'] ==[]:
            data['Client_ManagerId']=request.data.get("Client_ManagerId")

        if data['SPOC_Person'] is None or data['SPOC_Person'] =="":
            data['SPOC_Person']=request.data.get("SPOC_Person")



        updateobj = CreateClient.objects.filter(id = id,company_code = data['company_code'],is_active=True).exclude(id=obj.id).first()
        if updateobj is not None:
            return Response({"data":'',"n":0,"Msg":"Client already exist","Status":"failed"})
        else:

            serializer = createClientserializer(obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"n":1,"Msg":"Client updated successfully!","Status":"Success"})
            else:
                return Response({"data":serializer.errors,"n":0,"Msg":"Client not updated!","Status":"Failed"})
    else:
            return Response({"data":'',"n":0,"Msg":"Data not found","Status":"Failed"})
    

@api_view(['POST'])
def deleteCreateClient(request):
    data={}
    id = request.query_params.get('ID',None)
    objdata=CreateClient.objects.filter(id=id).first()
    if objdata is not None:
        data['is_active'] = False
        serializer = createClientserializer(objdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Client deleted successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Client not deleted","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"Client not found","Status":"Failed"})
    


@api_view(['POST'])
def AddEvent(request):
    data={}
    data['Project'] = request.POST.get("Project")
    data['ClientId'] = request.POST.get("ClientId")
    data['Assign_To']=request.POST.get("Assign_To")
    data['Assign_By']=request.POST.get("Assign_By")
    data['TaskDescription']=request.POST.get("TaskDescription")
    data['TaskValidation'] = request.POST.get("TaskValidation")
    data['Bonus']=request.POST.get("Bonus")
    data['AddNote']=request.POST.get("AddNote")
    data['FilledBy']=request.user.id
    data['updated_by']=request.user.id
    data["company_code"]=request.user.company_code

    serializer = Eventserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"n":1,"Msg":"Event Created successfully!","Status":"Success"})
    else:
        return Response({"data":serializer.errors,"n":0,"Msg":"Event  Creation unsuccessful!","Status":"Failed"})



@api_view(['GET'])
def Eventlist(request):
    Eventobj = Event.objects.filter(is_active=True).order_by('id')
    serializer = Eventserializer(Eventobj,many=True)
    for i in serializer.data:
        assigntoid = i['Assign_To']
        userobj = Users.objects.filter(id=assigntoid).first()
        if userobj is not None:
            i['Assign_Tostr'] = userobj.Firstname + " " +  userobj.Lastname
        else:
            i['Assign_Tostr'] =''

        assignbyid = i['Assign_By']
        abuserobj = ClientsideManager.objects.filter(id=assignbyid,is_active=True).first()
        if abuserobj is not None:
            i['Assign_Bystr'] = abuserobj.ManagerName
        else:
            i['Assign_Bystr'] =''

        ClientId = i['ClientId']
        clientobj = Client.objects.filter(id=ClientId,is_active=True).first()
        
        if clientobj is not None:
            i['clientstr'] = clientobj.ClientName
        else:
            i['clientstr'] =''
        projectid = i['Project']
        projectidobj = Client_Project.objects.filter(id=projectid,is_active=True).first()
        
        if projectidobj is not None:
            i['projectstr'] = projectidobj.ProjectName
        else:
            i['projectstr'] =''

        filledby = i['FilledBy']
        filledbyuserobj = Users.objects.filter(id=filledby).first()
        if filledbyuserobj is not None:
            i['FilledBystr'] = filledbyuserobj.Firstname + " " +  filledbyuserobj.Lastname
        else:
            i['FilledBystr'] = ''
            
        remarkzone = i['TaskValidation']
        if remarkzone == 1:
            i['remarkstr'] = "<img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='green'>"
        elif remarkzone == 2:
            i['remarkstr'] = "<img src='/static/Media/taskicons/activeyellowpoints.svg' class='activeicons' alt='yellow'>"
        elif remarkzone == 3:
            i['remarkstr'] = "<img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='red'>"
        elif remarkzone == 4:
            i['remarkstr'] = "<img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='notdone'>"

        bonusstr = i['Bonus']
        if bonusstr == True:
            i['bonusstr'] = "<img src='/static/Media/taskicons/activebonuspoints.svg' alt='bonus'>"
        else:
            i['bonusstr'] = ""


    return Response({"data":serializer.data,"n":1,"Msg":"Event Created successfully!","Status":"Success"})


@api_view(['GET'])
def getEvent(request):
    id = request.query_params.get('ID', None)
    if id is not None:
        Eventobj = Event.objects.filter(id=id,is_active=True).first()
        if Eventobj is not None:
            serializer = Eventserializer(Eventobj)

            newobj=serializer.data

            assigntoid = newobj['Assign_To']
            userobj = Users.objects.filter(id=assigntoid).first()
            newobj['Assign_Tostr'] = userobj.Firstname + " " +  userobj.Lastname

            assignbyid = newobj['Assign_By']
            abuserobj = ClientsideManager.objects.filter(id=assignbyid,is_active=True).first()
            newobj['Assign_Bystr'] = abuserobj.ManagerName

            projectid = newobj['Project']
            projectobj = Client.objects.filter(id=projectid,is_active=True).first()
            if projectobj is not None:
                
                newobj['projectstr'] = projectobj.ClientName
            else:
                newobj['projectstr'] = ''
                
            filledby = newobj['FilledBy']
            filledbyuserobj = Users.objects.filter(id=filledby).first()
            newobj['FilledBystr'] = filledbyuserobj.Firstname + " " +  filledbyuserobj.Lastname

              
            return Response({"data":newobj,"n":1,"Msg":"Event Created successfully!","Status":"Success"})
        else:
            return Response({"data":'',"n":0,"Msg":"Event not found!","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"ID not fetched","Status":"Failed"})
    

@api_view(['POST'])
def updateEvent(request):
    id = request.query_params.get('ID', None)
    obj = Event.objects.filter(id=id,is_active=True).first()
    if obj is not None:
        data={}
        data['ClientId'] = request.POST.get("ClientId")
        data['Project'] = request.POST.get("Project")
        data['Assign_To']=request.POST.get("Assign_To")
        data['Assign_By']=request.POST.get("Assign_By")
        data['TaskDescription']=request.POST.get("TaskDescription")
        data['TaskValidation'] = request.POST.get("TaskValidation")
        data['Bonus']=request.POST.get("Bonus")
        data['AddNote']=request.POST.get("AddNote")
        data['updated_by']=request.user.id
        data["company_code"]=request.user.company_code

        serializer = Eventserializer(obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Event Created successfully!","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Event  Creation unsuccessful!","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"ID not fetched","Status":"Failed"})
    

@api_view(['POST'])
def deleteEvent(request):
    data={}
    id = request.query_params.get('ID',None)
    objdata=Event.objects.filter(id=id).first()
    if objdata is not None:
        data['is_active'] = False
        data['updated_by']=request.user.id
        serializer = Eventserializer(objdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Event deleted successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Event not deleted","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"ID not fetched","Status":"Failed"})
    
@api_view(['POST'])
def AddClient_project(request):
    data={}
    data['ClientId'] = request.POST.get("Clientid")
    data['ProjectName'] = request.POST.get("Projectname")
    data["company_code"]=request.user.company_code
    serializer = Client_Projectserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"n":1,"Msg":"Project Added successfully.","Status":"Success"})
    else:
        return Response({"data":serializer.errors,"n":0,"Msg":"Project not added .","Status":"Failed"})


@api_view(['GET'])
def Client_Projectlist(request):
    projectobj = Client_Project.objects.filter(is_active=True).order_by('id')
    serializer = Client_Projectserializer(projectobj,many=True)

    return Response({"data":serializer.data,"n":1,"Msg":"Project List shown successfully!","Status":"Success"})


@api_view(['POST'])
def updateClient_project(request):
    data={}
    id = request.query_params.get('clientprojectID', None)
    obj = Client_Project.objects.filter(id=id,company_code=request.user.company_code,is_active=True).first()
    if obj is not None:
        ProjectName = request.POST.get("ProjectName")
        data['ProjectName'] = request.POST.get("ProjectName")
        data['ClientId'] = request.POST.get("ClientId")
        data['company_code']=request.user.company_code
        clientobj = Client_Project.objects.filter(ProjectName__in = [ProjectName.strip().capitalize(),ProjectName.strip(),ProjectName.title()],company_code = data['company_code'],is_active=True).exclude(id=id).first()
        if clientobj is not None:
            return Response({"data":'',"n":0,"Msg":"Client Project Already exist.","Status":"Failed"})
        else:
            serializer = Client_Projectserializer(obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"n":1,"Msg":"Client Project updated successfully","Status":"Success"})
            else:
                return Response({"data":serializer.errors,"n":0,"Msg":"Client Project not updated","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"client Project not found","Status":"Failed"})

# @api_view(['GET'])
# def GetClient_project(request):
#     id = request.query_params.get('ID', None)
#     if id is not None:
#         projectobj = Client_Project.objects.filter(id=id,is_active=True).first()
#         if projectobj is not None:
#             serializer = Eventserializer(projectobj)


@api_view(['POST'])
def deleteclientproject(request):
    data={}
    id = request.query_params.get('id', None)
    objdata=Client_Project.objects.filter(id=id).first()
    if objdata is not None:
        data['is_active'] = False
        serializer = Client_Projectserializer(objdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"n":1,"Msg":"Client project deleted successfully","Status":"Success"})
        else:
            return Response({"data":serializer.errors,"n":0,"Msg":"Client project not deleted","Status":"Failed"})
    else:
        return Response({"data":'',"n":0,"Msg":"Client project not found","Status":"Failed"})