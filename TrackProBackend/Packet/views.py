from rest_framework.decorators import authentication_classes, permission_classes
import json
from django.views.decorators.csrf import csrf_exempt
from Users.serializers import *
from CheckTrackPro.serializers import IntermediateGetTrackProResultSerializer
from CheckTrackPro.models import IntermediateTrackProResult
from Rules.models import Leaverule
from Rules.serializers import leaveruleserializer
from Users.serializers import RoleIdSerializer,UserSerializer, attendanceserializer, holidaysSerializer,UserSecondarySerializer,leaveserializer,leaveapprovalserializer,leaveMappingserializer,L1L2Serializer,UsersSerializeronlyid,UsersSerializeronlyattendance
from Users.serializers import MappingSerializer,EmployeeShiftDetailsSerializer,ShiftAllotmentSerializer,ShiftMasterSerializer,CompOffGrantedMasterSerializer
from .serializers import *
from Tasks.serializers import *
from Tasks.models import *
from .models import *
from TrackProBackend.settings import EMAIL_HOST_USER
from Users.models import Role, Users,UserToManager,UserSecondaryInfo,Leave,leaveApproval,leaveMapping,adminAttendanceRequest,EmployeeShiftDetails
from Users.views import create_google_maps_url,get_location_name
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework import status
from rest_framework.decorators import api_view
# from CompanyMaster.views import imageUrl
from django.template.loader import  get_template
from django.core.mail import EmailMessage
from datetime import date,datetime,timedelta,time
import datetime
import arrow
from django.db.models import Sum
from dateutil.relativedelta import *
import xlsxwriter
import calendar
import environ
env = environ.Env()
environ.Env.read_env()
from collections import defaultdict
from openpyxl import load_workbook
from Tasks.views import sendfirebasenotification,senddesktopnotf
from Users.sendmail import send_async_custom_template_email
from Users.static_info import adminemail,hremail,frontUrl,imageUrl
from rest_framework import pagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from Users.custom_functions import *
import os
from Leave.models import LeaveTypeMaster
class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'

    def get_paginated_response(self,data):
        response = Response({
            'n':1,
            'status':"success",
            'count':self.page.paginator.count,
            'next' : self.get_next_link(),
            'previous' : self.get_previous_link(),
            'data':data,
        })
        return response
    



# Create your views here.
@api_view(['POST'])
def add_packet(request):
    if request.method == 'POST':
        data=request.data.copy()
        data['PacketName']=data['PacketName'].lower()
        data['is_active']=True
        data['company_code']=request.user.company_code
        already_exist_obj=PacketMaster.objects.filter(PacketName=data['PacketName'],is_active=True,company_code=request.user.company_code).first()
        if already_exist_obj is not None:
            return Response ({"data":[], "response":{"n" : 0,"msg" : "Packet name already exists","status" : "error"}})
        else:
            serializer=PacketMasterSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response ({"data":[], "response":{"n" : 1,"msg" : "Packet added successfully","status" : "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response ({"data":[],"response":{"n" : 0,"msg" : first_key[0] +' '+ first_value[0],"status" : "error"}})

@api_view(['POST'])
def update_packet(request):
    if request.method == 'POST':
        data=request.data.copy()
        data['PacketName']=data['PacketName'].lower()
        if data['id'] is not None and data['id'] !='':
            update_packet_obj=PacketMaster.objects.filter(id=data['id'],is_active=True,company_code=request.user.company_code).first()
            if update_packet_obj is not None:
                already_exist_obj=PacketMaster.objects.filter(PacketName=data['PacketName'],is_active=True,company_code=request.user.company_code).exclude(id=data['id']).first()
                if already_exist_obj is not None:
                    return Response ({"data":[], "response":{"n" : 0,"msg" : "Packet name already exists","status" : "error"}})
                else:
                    serializer=PacketMasterSerializer(update_packet_obj,data=data,partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response ({"data":[], "response":{"n" : 1,"msg" : "Packet updated successfully","status" : "success"}})
                    else:
                        first_key, first_value = next(iter(serializer.errors.items()))
                        return Response ({"data":[],"response":{"n" : 0,"msg" : first_key[0] +' '+ first_value[0],"status" : "error"}})
            else:
                return Response ({"data":[], "response":{"n" : 0,"msg" : "leave typ not found ","status" : "error"}})
        else:
            return Response ({"data":[], "response":{"n" : 0,"msg" : "Please provide leave typ id ","status" : "error"}})

@api_view(['POST'])
def delete_packet(request):
    if request.method == 'POST':
        data=request.data.copy()
        if data['id'] is not None and data['id'] !='':
            delete_packet_obj=PacketMaster.objects.filter(id=data['id'],is_active=True,company_code=request.user.company_code).first()
            if delete_packet_obj is not None:
                data['is_active']=False
                serializer=PacketMasterSerializer(delete_packet_obj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response ({"data":[], "response":{"n" : 1,"msg" : "Packet deleted successfully","status" : "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response ({"data":[],"response":{"n" : 0,"msg" : first_key[0] +' '+ first_value[0],"status" : "error"}})
            else:
                return Response ({"data":[], "response":{"n" : 0,"msg" : "leave typ not found ","status" : "error"}})
        else:
            return Response ({"data":[], "response":{"n" : 0,"msg" : "Please provide leave typ id ","status" : "error"}})

@api_view(['POST'])
def get_packet_by_id(request):
    if request.method == 'POST':
        data=request.data.copy()
        if data['id'] is not None and data['id'] !='':
            packet_obj=PacketMaster.objects.filter(id=data['id'],is_active=True,company_code=request.user.company_code).first()
            if packet_obj is not None:
                serializer=PacketMasterSerializer(packet_obj)
                return Response ({"data":serializer.data, "response":{"n" : 1,"msg" : "Packet found successfully","status" : "success"}})
            else:
                return Response ({"data":[], "response":{"n" : 0,"msg" : "leave typ not found ","status" : "error"}})
        else:
            return Response ({"data":[], "response":{"n" : 0,"msg" : "Please provide leave typ id ","status" : "error"}})

@api_view(['GET'])
def get_packet_list(request):
    if request.method == 'GET':
        print("req",request.user.company_code)
        packet_obj=PacketMaster.objects.filter(is_active=True,company_code=request.user.company_code)
        if packet_obj is not None:
            serializer=PacketMasterSerializer(packet_obj,many=True)
            return Response ({"data":serializer.data, "response":{"n" : 1,"msg" : "Packets found successfully","status" : "success"}})
        else:
            return Response ({"data":[], "response":{"n" : 0,"msg" : "leave typ not found ","status" : "error"}})

@api_view(['POST'])
def get_packet_mapped_employees(request):
    if request.method == 'POST':
        PacketId=request.POST.get('PacketId')
        Location=request.POST.get('Location')
        if PacketId is not None and PacketId !='':
            packet_obj=PacketMaster.objects.filter(is_active=True,id=PacketId,company_code=request.user.company_code).first()
            if packet_obj is not None:
                userlist=[]
                employee_mapping_ids=list(PacketEmployeeMapping.objects.filter(is_active=True,PacketId=PacketId,company_code=request.user.company_code).values_list('EmployeeId', flat=True))
                mapped_user_obj=Users.objects.filter(id__in=employee_mapping_ids,is_active=True,company_code=request.user.company_code).exclude(Q(employeeId__isnull=True)|Q(employeeId='None')|Q(employeeId=''))
                mapped_user_serializer=UserSerializer(mapped_user_obj,many=True)
                for user in mapped_user_serializer.data:
                    userlist.append({'id':user['id'],'employeeId':user['employeeId'],'name':user['Firstname']+ ' ' +user['Lastname'],'selected':True})

                unmapped_user_obj=Users.objects.filter(is_active=True,company_code=request.user.company_code).exclude(Q(employeeId__isnull=True)|Q(employeeId='None')|Q(employeeId='')|Q(id__in=employee_mapping_ids,))
                if Location is not None and Location !='':
                    unmapped_user_obj=unmapped_user_obj.filter(locationId_id=Location)
                unmapped_user_serializer=UserSerializer(unmapped_user_obj,many=True)
                for user in unmapped_user_serializer.data:
                    userlist.append({'id':user['id'],'employeeId':user['employeeId'],'name':user['Firstname']+ ' ' +user['Lastname'],'selected':False})


                return Response ({"data":userlist, "response":{"n" : 1,"msg" : "Packets found successfully","status" : "success"}})
            else:
                return Response ({"data":[], "response":{"n" : 0,"msg" : "packet not found ","status" : "error"}})


@api_view(['POST'])
def apply_employees_packet_mapping(request):
    if request.method == 'POST':
        PacketId=request.POST.get('PacketId')
        selected_employee_ids=json.loads(request.POST.get('selected_employee_ids'))
        if PacketId is not None and PacketId !='':
            packet_obj=PacketMaster.objects.filter(is_active=True,id=PacketId,company_code=request.user.company_code).first()
            if packet_obj is not None:
                if selected_employee_ids !=[] and selected_employee_ids is not None:
                    delete_existing=PacketEmployeeMapping.objects.filter(PacketId=PacketId,company_code=request.user.company_code).delete()
                    for EmployeeId in selected_employee_ids:
                        create_obj=PacketEmployeeMapping.objects.create(PacketId=PacketId,EmployeeId=EmployeeId,company_code=request.user.company_code)

                        
                    return Response ({"data":{}, "response":{"n" : 1,"msg" : "Packets mapped to employees successfully","status" : "success"}})
                else:
                    return Response ({"data":{}, "response":{"n" : 0,"msg" : "please provide selected employee list","status" : "error"}})
            else:
                return Response ({"data":{}, "response":{"n" : 0,"msg" : "packet not found ","status" : "error"}})
        else:
            return Response ({"data":{}, "response":{"n" : 0,"msg" : "please provide packet id ","status" : "error"}})

@api_view(['POST'])
def apply_packet_rules(request):
    if request.method == 'POST':
        PacketId=request.POST.get('PacketId')
        LeaveTypeId=request.POST.get('LeaveTypeId')
        # print("req",request.data)

        company_code=request.user.company_code
        if PacketId is not None and PacketId !='':
            packet_obj=PacketMaster.objects.filter(is_active=True,id=PacketId,company_code=company_code).first()
            if packet_obj is not None:
                if LeaveTypeId is not None and LeaveTypeId !='':
                    leave_type_obj=LeaveTypeMaster.objects.filter(id=LeaveTypeId,is_active=True,company_code=company_code)
                    if leave_type_obj is not None:
                        data=request.data.copy()
                        data['PacketId']=PacketId
                        data['LeaveTypeId']=LeaveTypeId
                        data['company_code']=company_code
                        if data['Rule1'] == 'true':
                            data['Rule1']=True
                        else:
                            data['Rule1']=False

                        if data['Rule2'] == 'true':
                            data['Rule2']=True
                        else:
                            data['Rule2']=False

                        if data['Rule3'] == 'true':
                            data['Rule3']=True
                        else:
                            data['Rule3']=False

                        if data['PSHoliday'] == 'true':
                            data['PSHoliday']=True
                        else:
                            data['PSHoliday']=False

                        if data['PSWeeklyOff'] == 'true':
                            data['PSWeeklyOff']=True
                        else:
                            data['PSWeeklyOff']=False

                        if data['Rule4'] == 'true':
                            data['Rule4']=True
                        else:
                            data['Rule4']=False


                        if data['Rule5'] == 'true':
                            data['Rule5']=True
                        else:
                            data['Rule5']=False

                        if data['Rule6'] == 'true':
                            data['Rule6']=True
                        else:
                            data['Rule6']=False


                        if data['Rule7'] == 'true':
                            data['Rule7']=True
                        else:
                            data['Rule7']=False

                        if data['Rule8'] == 'true':
                            data['Rule8']=True
                        else:
                            data['Rule8']=False

                        if data['Rule9'] == 'true':
                            data['Rule9']=True
                        else:
                            data['Rule9']=False
                        
                        if data['Rule10'] == 'true':
                            data['Rule10']=True
                        else:
                            data['Rule10']=False
                        
                        if data['Rule11'] == 'true':
                            data['Rule11']=True
                        else:
                            data['Rule11']=False
                        
                        if data['Rule12'] == 'true':
                            data['Rule12']=True
                        else:
                            data['Rule12']=False


                        print("data",data)
                        check_already_exist=PacketLeaveRules.objects.filter(PacketId=PacketId,LeaveTypeId=LeaveTypeId,company_code=company_code).first()
                        if check_already_exist is not None:
                            action='updated'
                            serializer=PacketLeaveRulesSerializer(check_already_exist,data=data,partial=True)
                        else:
                            action='added'

                            serializer=PacketLeaveRulesSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()

                            return Response ({"data":{}, "response":{"n" : 1,"msg" : "Packets rules "+ action+" successfully","status" : "success"}})
                        else:
                            first_key, first_value = next(iter(serializer.errors.items()))
                            return Response ({"data":{},"response":{"n" : 0,"msg" : first_key[0] +' '+ first_value[0],"status" : "error"}})
                    else:
                        return Response ({"data":{}, "response":{"n" : 0,"msg" : "leave type not found ","status" : "error"}})

                else:
                    return Response ({"data":{}, "response":{"n" : 0,"msg" : "please provide leave type id","status" : "error"}})
            else:
                return Response ({"data":{}, "response":{"n" : 0,"msg" : "packet not found ","status" : "error"}})

        else:

            return Response ({"data":{}, "response":{"n" : 0,"msg" : "please provide packet id ","status" : "error"}})





@api_view(['POST'])
def get_packet_leave_rules(request):
    if request.method == 'POST':
        PacketId=request.POST.get('PacketId')
        LeaveTypeId=request.POST.get('LeaveTypeId')
        company_code=request.user.company_code
        if PacketId is not None and PacketId !='':
            packet_obj=PacketMaster.objects.filter(is_active=True,id=PacketId,company_code=company_code).first()
            if packet_obj is not None:
                if LeaveTypeId is not None and LeaveTypeId !='':
                    leave_type_obj=LeaveTypeMaster.objects.filter(id=LeaveTypeId,is_active=True,company_code=company_code)
                    if leave_type_obj is not None:
                        check_already_exist=PacketLeaveRules.objects.filter(PacketId=PacketId,LeaveTypeId=LeaveTypeId,company_code=company_code).first()
                        if check_already_exist is not None:
                            serializer=PacketLeaveRulesSerializer(check_already_exist)
                            return Response ({"data":serializer.data, "response":{"n" : 1,"msg" : "Packets rules found successfully","status" : "success"}})
                        else:
                            return Response ({"data":{},"response":{"n" : 0,"msg" :'Packets rules not found ',"status" : "error"}})
                    else:
                        return Response ({"data":{}, "response":{"n" : 0,"msg" : "leave type not found ","status" : "error"}})

                else:
                    return Response ({"data":{}, "response":{"n" : 0,"msg" : "please provide leave type id","status" : "error"}})
            else:
                return Response ({"data":{}, "response":{"n" : 0,"msg" : "packet not found ","status" : "error"}})
        else:
            return Response ({"data":{}, "response":{"n" : 0,"msg" : "please provide packet id ","status" : "error"}})
