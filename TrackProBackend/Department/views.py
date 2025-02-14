from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .serializers import DepartmentSerializer, DepartmentUpdateSerializer
from Users.serializers import UserSerializer
from rest_framework.generics import ListAPIView
from Users.models import Designation, Role, Users, ErrorLog, UserToManager
from .models import Department
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.db.models import Q
from Users.serializers import UsersSerializer
# DISPLAY DEPARTMENT LIST-------------------------------------------------------------------------------------
# class departmentListAPI(ListAPIView):
#     serializer_class = DepartmentSerializer
#     queryset = Department.objects.all()
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     pagination_class = PageNumberPagination

@api_view(['GET'])
def departmentListAPI(request, format=None):
    """
    List all tasks, or create a new task.
    """
    if request.method == 'GET':
        teamlist=[]
        dept = Department.objects.filter(Active=True).exclude(Q(DepartmentName__isnull=True)|Q(DepartmentName='None')|Q(DepartmentName='')).order_by("-id")
        
        
        serializer = DepartmentSerializer(dept, many=True)
        for i in serializer.data:
            teamlist=[]
            userobject =Users.objects.filter(id=i['DepartmentHead'],is_active=True).first()
            if userobject is not None:
                i['departmentheadstr'] = userobject.Firstname + ' ' + userobject.Lastname

            teamobj = Users.objects.filter(DepartmentID=i['id']).exclude(DepartmentID=i['DepartmentHead'])
            teamobjser = UserSerializer(teamobj,many=True)
            for p in teamobjser.data:
                teamlist.append(p['Firstname']+" "+p['Lastname'])

            i['deptteamlist']=teamlist

        
            user_obj = Users.objects.filter(DepartmentID=i['id'],is_active=True).first()
            if user_obj is not None:
                i['Used']=True
            else:
                i['Used']=False
        return Response({'n':1,'Msg':'Department list fetched successfully','Status':'Success','data':serializer.data})

# ADD DEPARTMENT-------------------------------------------------------------------------------------
@api_view(['POST'])
def addDepartment(request):
    user = request.user
    if user.is_admin ==True:
        try:
            requestData = request.data.copy()
            DepartmentName = requestData['DepartmentName'].strip()
            requestData['DepartmentName'] = DepartmentName
            requestData['DepartmentHead'] = requestData['DepartmentHead']
            requestData['company_code'] = request.user.company_code
            requestData['Active'] = True
        except Exception as e:
            return Response({"n":0,"Msg":'serializer not accepting data',"Status":"Error"})
        else:
            deptObject = Department.objects.filter(DepartmentName__in=[DepartmentName.strip().capitalize(),DepartmentName.strip(),DepartmentName.title(),DepartmentName.lower()],company_code=request.user.company_code,Active=True).first()
            if deptObject is None:
                serializer =DepartmentUpdateSerializer(data=requestData, context={'request':request})
                if serializer.is_valid():
                    serializer.validated_data['CreatedBy'] = user
                    serializer.save()
                    return Response({"n":1,"Msg":"Department added successfully","Status":"success"})
                else:
                    return Response({"n":0,"Msg":serializer.errors,"Status":"Error"})
            return Response({"n":0,"Msg":"Department already exist","Status":"Error"})
            
    else:
        return Response({"n":0,"Msg":'User has no permission to create',"Status":"Error"})

# DELETE DEPARTMENT-------------------------------------------------------------------------------------
@api_view(['POST'])
def departmentDelete(request):
    data = {"n":0,"Msg":"","Status":""} 
    try:
        departmentID = request.data.get('departmentID')
        if departmentID is not None:
            department = Department.objects.filter(id = departmentID,Active=True).first()
            if department is None:
                data['n']=0
                data['Msg']= 'DEPARTMENT DOES NOT EXIST'
                data['Status']="warning"
            else:
                operation  = department.delete()
                if operation:
                    data['n']=1
                    data['Msg']= 'delete successfull'
                    data['Status']="Success"
                else:
                    data['n']=0
                    data['Msg']= 'delete failed'
                    data['Status']="warning"
        else:
            data['n']=0
            data['Msg']= ' is none'
            data['Status']="warning"         
    except Exception as e:
        data['n']=0
        data['Msg']= 'try method failed'
        data['Status']="warning"
    return Response(data =data)

# UPDATE DEPARTMENT-------------------------------------------------------------------------------------
@api_view(['POST'])
def departmentUpdate(request):
    data = {'n':'','Msg':'','Status':''}
    try:
        departmentID = request.query_params.get('departmentID')
        if departmentID is None:
            data['n']=0
            data['Msg']= 'department ID is none'
            data['Status']="Failed"
        else:
            try:
                department = Department.objects.filter(id = departmentID,Active = True,company_code = request.user.company_code).first()
            except Exception as e:
                data['n']=0
                data['Msg']= 'DEPARTMENT DOES NOT EXIST'
                data['Status']="Failed"
            else:
                requestData = request.data.copy()
                DepartmentName = requestData['DepartmentName'].strip()
                requestData['DepartmentName'] = DepartmentName
                requestData['company_code'] = request.user.company_code
                requestData['Active'] = True
                deptObject = Department.objects.filter(DepartmentName__in = [DepartmentName.strip().capitalize(),DepartmentName.strip(),DepartmentName.title(),DepartmentName.lower()],Active= True,company_code = requestData['company_code']).first()
                if department.DepartmentName != requestData['DepartmentName'] and deptObject is not None :
                    return Response({'n': 0, 'Msg': "Department already exists", 'Status': 'Failed'})
                serializer = DepartmentUpdateSerializer(department, data = requestData)
                if serializer.is_valid():
                    serializer.validated_data['UpdatedBy']  = request.user    
                    serializer.save()
                    return Response({"n":1,"Msg":"Department Updated successfully","Status":"success"})
                else:
                    return Response({"n":0,"Msg":serializer.errors,"Status":"Error"})
    except Exception as e:
        data['n']=0
        data['Msg']= 'try method failed'
        data['Status']="Failed"
        return Response(data = data)

#get object in designation---------------------------------------------------------------------------------------------
@api_view(['GET'])
def getDepartment(request):
    if request.method == 'GET':
        id = request.query_params.get('departmentID', None)
        if id is not None:
            i = Department.objects.filter(id = id,Active=True,company_code=request.user.company_code).first()
            if i is not None:
                serializer = DepartmentUpdateSerializer(i)
                return Response({'n': 1, 'Msg': 'Department fetched successfully', 'Status': 'success','data':serializer.data})
            return Response({'n': 0, 'Msg': 'Department not found', 'Status': 'failed','data':''})
        return Response({'n': 0, 'Msg': 'Please provide Id', 'Status': 'failed','data':''})



