
from rest_framework.decorators import authentication_classes, permission_classes
from drf_multiple_model.views import ObjectMultipleModelAPIView
import json
import pytz
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.dateparse import parse_datetime
from CheckTrackPro.serializers import IntermediateTrackProResult
from CheckTrackPro.serializers import IntermediateGetTrackProResultSerializer,IntermediatePostTrackProResultSerializer
from Users.serializers import UserSerializer,GetUserSerializer,MappingSerializer,leaveserializer
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from functools import partial
from django.utils import timezone
from rest_framework.views import set_rollback
from Project.serializers import ProjectSerializer, ProjectTasksUpdateSerializer
from Project.models import ProjectMaster
from django.shortcuts import redirect, render
from Users.models import Users,UserToManager,Holidays,Leave,leaveApproval
from Users.serializers import leaveserializer,leaveapprovalserializer
from CompanyMaster.models import companyinfo
from Rules.models import *
from Rules.serializers import *
# Create your views here.
from .models import ProjectTasks, Status, TaskMaster, Zone,NotificationTypeMaster,TaskNotification,TaskRemark
from .serializers import GetTaskMasterSerializer, PostTaskMasterSerializer, PostTaskMasterSerializerStatus, ZoneSerializer, SearchTaskMasterSerializer, GetTaskSerializer,NotificationTypeSerializer,TaskNotificationSerializer,GetTaskScoreSerializer,GetPendingTaskMasterSerializer
from .serializers import YearSerializer, WeekSerializer,ProjectTasksSerializer,TaskRemarkSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.http import JsonResponse
from datetime import date,timedelta
import datetime
from django.db.models import Avg
from operator import itemgetter
from CheckTrackPro.views import stock_maindictlist
import calendar
import numpy as np
from CompanyMaster.views import FCM_SERVER_KEY,Desktop_key
from Users.static_info import imageUrl,l1l2projectid
from CompanyMaster.common import createadminuser,paymentlog,givePermission,send_mail
from django.template.loader import get_template, render_to_string
import requests

from Department.models  import Department
from Department.serializers import DepartmentSerializer
from Users.sendmail import send_async_custom_template_email
import firebase_admin
from firebase_admin import credentials, messaging
from google.oauth2 import service_account
import google.auth.transport.requests
import json
import requests
import os
from TrackProBackend.settings import BASE_DIR

def convertdate2(input_date):
    try:
        # Parse the input date string into a datetime object
        date_obj = datetime.datetime.strptime(input_date, '%Y-%m-%d')

        # Format the date in the desired output format
        formatted_date = date_obj.strftime('%d %b %y')

        return formatted_date
    except ValueError:
        return "Invalid Date Format"

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True


def month_converter(month):
    month_num = month  # month_num = 4 will work too
    month_name = datetime.datetime(1, int(month_num), 1).strftime("%B")
    return month_name



@api_view(['GET'])
def taskList(request, format=None):
    if request.method == 'GET':
        task = TaskMaster.objects.filter(company_code = request.user.comapny_code).order_by('CreatedOn')
        serializer = GetTaskMasterSerializer(task, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def taskListApi(request, format=None):
    taskId=[]
    data={}
    companycode =  request.user.company_code 
    if request.method == 'GET':
        task = TaskMaster.objects.all().order_by('CreatedOn')
        serializer = GetTaskSerializer(task, many=True)
        for i in serializer.data:
            taskId.append(i['AssignTo'])
        userObject=Users.objects.filter(id__in=taskId,is_blocked=False,company_code=companycode).order_by('Firstname')
        userSer=GetUserSerializer(userObject,many=True)
        return Response(userSer.data)


@api_view(['POST'])
def addNewTask(request, format=None):
    if  request.method == 'POST':
        if request.data['Project'] != "":
            project = ProjectMaster.objects.get(id=request.data['Project'])
        currenttime =  timezone.localtime(timezone.now())
        companycode = request.user.company_code
        userid = request.user.id
        taskobject = TaskMaster.objects.filter(AssignTo=userid)
        taskser = GetTaskSerializer(taskobject,many=True)
        for i in taskser.data:
            if i['AssignBy'] == "" or i['AssignBy'] == None and i['Project'] == "" or i['Project'] == None:
                return Response({"n": 0, "Msg": "Manager and project has not been selected to some task please update that first.", "Status": "Failed",'data':{}})

            elif i['AssignBy'] == "" or i['AssignBy'] == None:
                return Response({"n": 0, "Msg": "Manager has not been assigned to some task please update that first.", "Status": "Failed",'data':{}})
            
            elif i['Project'] == "" or i['Project'] == None:
                return Response({"n": 0, "Msg": "Project has not been selected to some task please update that first.", "Status": "Failed",'data':{}})
            
        getactive = TaskMaster.objects.filter(AssignTo=request.user, Active=True, Status_id=1)

        if getactive is not None:
            taskserializer = GetTaskMasterSerializer(getactive, many=True)

            for t in taskserializer.data:
                TaskMaster.objects.filter(id=t['id'],
                AssignTo=request.user, Active=True, Status_id=1).update(Status=2,Active=False)
              
                taskid=t['id']
                enddatetime =  timezone.localtime(timezone.now())
                ProjectTasks.objects.filter(Task_id=taskid,EndDate__isnull=True).update(EndDate=enddatetime)
               
        if request.data['AssignBy'] == '' or request.data['AssignBy'] == None:
            requestData = request.data.copy()
            requestData['company_code'] = request.user.company_code
            if request.data['Project'] != "":
                requestData['ProjectName'] = project.ProjectName

            serializer = PostTaskMasterSerializer(data=requestData)
            if serializer.is_valid():
                serializer.validated_data['Active'] = True
                serializer.validated_data['AssignTo'] = request.user
                serializer.validated_data['CreatedBy'] = request.user
                serializer.save()

                taskid= serializer.data['id']
                ProjectTasks.objects.create(Task_id=taskid,StartDate=currenttime,company_code=companycode)

                return Response({"n": 1, "Msg": "Task added successfully", "Status": "Success",'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"n": 0, "Msg": "Error adding task", "Status": "Failed",'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            requestData = request.data.copy()
            requestData['company_code'] = request.user.company_code
            serializer = PostTaskMasterSerializer(data=requestData)
            if serializer.is_valid():
                serializer.validated_data['Active'] = True
                serializer.validated_data['AssignTo'] = request.user
                serializer.validated_data['CreatedBy'] = request.user
                serializer.validated_data['ProjectName'] = project.ProjectName
                s = serializer.validated_data['AssignBy']
                user = Users.objects.filter(id=s.id)
                for u in user:
                    serializer.validated_data['AssignByStr'] = u.Firstname + \
                        ' ' + u.Lastname
                serializer.save()

                taskid= serializer.data['id']
                ProjectTasks.objects.create(Task_id=taskid,StartDate=currenttime,company_code=companycode)

                return Response({"n": 1, "Msg": "Task added successfully", "Status": "Success",'data':serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"n": 0, "Msg": "Error adding task", "Status": "Failed",'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def addduplicatetask(request):
    data={}
    taskID = request.POST.get('taskID')
    currenttime =  timezone.localtime(timezone.now())
    companycode = request.user.company_code
    if taskID is not None:
        getactive = TaskMaster.objects.filter(AssignTo=request.user, Active=True, Status_id=1)
        if getactive is not None:
            taskserializer = GetTaskMasterSerializer(getactive, many=True)

            for t in taskserializer.data:
                TaskMaster.objects.filter(id=t['id'],
                AssignTo=request.user, Active=True, Status_id=1).update(Status=2,Active=False)
              
                taskid=t['id']

                enddatetime =  timezone.localtime(timezone.now())
                ProjectTasks.objects.filter(Task_id=taskid,EndDate__isnull=True).update(EndDate=enddatetime)
            

        taskobj = TaskMaster.objects.filter(id=taskID).first()
        if taskobj is not None:
            taskser = GetTaskSerializer(taskobj)
            data['AssignTo'] = taskser.data['AssignTo']
            data['Project'] = taskser.data['Project']
            data['ProjectName']= taskser.data['ProjectName']
            data['AssignBy'] = taskser.data['AssignBy']
            manager = Users.objects.filter(id=data['AssignBy'])
            for m in manager:
                assignbystr = m.Firstname +  ' ' + m.Lastname
            data['AssignByStr'] = assignbystr
            data['Status'] = 1
            data['company_code']=companycode
            data['TaskTitle'] = taskser.data['TaskTitle']

            todaysdate = date.today()
            data['AssignDate'] = todaysdate

            my_date = datetime.date.today()
            year, week_num, day_of_week = my_date.isocalendar()
            data['Week'] = int(week_num)
            data['Year'] = int(year)

            strday = datetime.datetime.today().strftime('%A')
            data['Day'] = strday

            if taskser.data['IsParent'] == True:
                return Response({"n": 0, "Msg": "Cant duplicate parent task", "Status": "Failed",'data':{}}, status=status.HTTP_201_CREATED)
            elif taskser.data['IsParent'] == False:
                if taskser.data['ParentTaskId'] is not None:
                    return Response({"n": 0, "Msg": "Cant duplicate child task", "Status": "Failed",'data':{}}, status=status.HTTP_201_CREATED)
                else:
                    serializer = PostTaskMasterSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()

                        taskid= serializer.data['id']
                        ProjectTasks.objects.create(Task_id=taskid,StartDate=currenttime,company_code=companycode)

                        return Response({"n": 1, "Msg": "Task Duplicated successfully", "Status": "Success",'data':serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"n": 0, "Msg": "Task not created", "Status": "Failed",'data':serializer.errors})

        else:
            return Response({"n": 0, "Msg": "task not found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"n": 0, "Msg": "taskid not found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST']) 
def AddContinuetask(request):
    data={}
    taskID = request.POST.get('taskID')
    currenttime =  timezone.localtime(timezone.now())
    companycode = request.user.company_code
    if taskID is not None:
        taskobj = TaskMaster.objects.filter(id=taskID).first()
        if taskobj is not None:
            getactive = TaskMaster.objects.filter(AssignTo=request.user, Active=True, Status_id=1)
            if getactive is not None:
                taskserializer = GetTaskMasterSerializer(getactive, many=True)

                for t in taskserializer.data:
                    TaskMaster.objects.filter(id=t['id'],
                    AssignTo=request.user, Active=True, Status_id=1).update(Status=2,Active=False)
                
                    taskid=t['id']

                    enddatetime =  timezone.localtime(timezone.now())
                    ProjectTasks.objects.filter(Task_id=taskid,EndDate__isnull=True).update(EndDate=enddatetime)


            taskobjplay = TaskMaster.objects.filter(id=taskID,Status__in=[1,2]).first()
            if taskobjplay is not None:
                return Response({"n": 0, "Msg": "Task is not closed", "Status": "Failed",'data':''})
            else:
                taskser = GetTaskSerializer(taskobj)
                data['AssignTo'] = taskser.data['AssignTo']
                data['Project'] = taskser.data['Project']
                data['ProjectName']= taskser.data['ProjectName']
                data['AssignBy'] = taskser.data['AssignBy']
                manager = Users.objects.filter(id=data['AssignBy'])
                for m in manager:
                    assignbystr = m.Firstname +  ' ' + m.Lastname
                data['AssignByStr'] = assignbystr
                data['Status'] = 1
                data['company_code']=companycode
                data['TaskTitle'] = taskser.data['TaskTitle']

                todaysdate = date.today()
                data['AssignDate'] = todaysdate

                my_date = datetime.date.today()
                year, week_num, day_of_week = my_date.isocalendar()
                data['Week'] = int(week_num)
                data['Year'] = int(year)
                
                pid = taskser.data['ParentTaskId']

                if pid == '' or pid is None:
                    data['ParentTaskId'] = int(taskID)
                else:
                    data['ParentTaskId'] = taskser.data['ParentTaskId']

                parentobj = TaskMaster.objects.filter(id= data['ParentTaskId']).update(IsParent=True)

                strday = datetime.datetime.today().strftime('%A')
                data['Day'] = strday

                
                startd = currenttime

                serializer = PostTaskMasterSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()

                    newtaskid= serializer.data['id']
                    
                    ProjectTasks.objects.create(Task_id=newtaskid,StartDate=startd,company_code=companycode)

                return Response({"n": 1, "Msg": "Task Continued successfully", "Status": "Success",'data':serializer.data})
        else:
            return Response({"n": 0, "Msg": "task not found", "Status": "Failed",'data':''})
    else:
        return Response({"n": 0, "Msg": "taskid not found", "Status": "Failed",'data':''})













@api_view(['POST'])
def deleteTask(request):
    data = {"n": 0, "Msg": "", "Status": ""}
    taskID = request.GET.get('taskID')
    if taskID is not None:
        task = TaskMaster.objects.filter(id=taskID)
        projecttask = ProjectTasks.objects.filter(id=taskID)
        if not task:
            return Response({"n": 0, "Msg": "TASK DOES NOT EXIST", "Status": "Failed"}, status=status.HTTP_201_CREATED)
        else:
            for t in task:
                if t.CheckedBy == None:
                    if t.IsParent == True :
                        return Response({"n": 0, "Msg": "Cant delete Continued Tasks", "Status": "Failure"})
                    elif t.ParentTaskId != "" and t.ParentTaskId is not None:
                        return Response({"n": 0, "Msg": "Cant delete Continued Tasks", "Status": "Failure"})
                    else:
                        t.delete()
                        projecttask.delete()
                        return Response({"n": 1, "Msg": "Task Deleted Successfully", "Status": "Success"})
                else:
                    return Response({"n": 0, "Msg": "This task has already been checked", "Status": "Failed"})
    else:
        return Response({"n": 0, "Msg": "TASK id not found", "Status": "Failed"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def gettaskdetail(request):
    currentzone = pytz.timezone("Asia/Kolkata") 
    currenttime = datetime.datetime.now(currentzone)
    newcurrenttime = currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    taskID = request.GET.get('taskID')
    taskdata = []
    if taskID is not None and taskID != "":
        taskobject = TaskMaster.objects.filter(id=taskID).first()
        if taskobject is not None:
            taskserializer = GetTaskSerializer(taskobject)
            for f in [taskserializer.data]:
                if f['Zone'] == 1:
                    greenstatusstr = "<img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    greenstatusstr = "<img src='/static/Media/taskicons/nongreen.svg' id='1' class='nonactive' alt='Paris'>"

                if f['Zone'] == 2:
                    yellowstatusstr = "<img src='/static/Media/taskicons/activeyellowpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    yellowstatusstr = "<img src='/static/Media/taskicons/yellow.svg' id='2' class='nonactive' alt='Paris'>"

                if f['Zone'] == 3:
                    redstatusstr = "<img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='Paris' >"
                else:
                    redstatusstr = "<img src='/static/Media/taskicons/red.svg' id='3' class='nonactive' alt='Paris'>"

                if f['Zone'] == 4:
                    notdonestr = "<img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='Paris'>"
                else:
                    notdonestr = "<img src='/static/Media/taskicons/notdone.svg' id='4' class='nonactive' alt='Paris' >"

                if f['Zone'] == 5:
                    cancelledstr = "<img src='/static/Media/taskicons/activecancelledpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    cancelledstr = "<img src='/static/Media/taskicons/cancelled.svg' id='5' class='nonactive' alt='Paris'>"

                if f['Zone'] == 6:
                    rejectedstr = "<img src='/static/Media/taskicons/activerejectpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    rejectedstr = "<img src='/static/Media/taskicons/rejected.svg' id='6' class='nonactive' alt='Paris'>"

                if f['Bonus'] == True:
                    bonusstr = "<img src='/static/Media/taskicons/activebonuspoints.svg' alt='Paris' >"
                    bonushiddenstr = "True"
                else:
                    bonusstr = "<img src='/static/Media/taskicons/bonus.svg' alt='Paris'>"
                    bonushiddenstr = "False"

                f['Bonus'] = bonusstr
                f['bonushiddenstr'] = bonushiddenstr
                f['greenstatusstr']=greenstatusstr
                f['yellowstatusstr']=yellowstatusstr
                f['redstatusstr']=redstatusstr
                f['notdonestr']=notdonestr
                f['cancelledstr']=cancelledstr
                f['rejectedstr']=rejectedstr

                projecttasks = ProjectTasks.objects.filter(Task = taskobject.id)
                projectser = ProjectTasksSerializer(projecttasks,many=True)
                totaltime=0
                for o in projectser.data:
                    startstring = o['StartDate']
                    starttime=startstring
                    t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                    endstring = o['EndDate']
                    if endstring is not None:
                        endtime = o['EndDate']
                    else:
                        endtime = str(newcurrenttime)
                    t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                    tdelta=t2-t1
                
                
                    if "day" in str(tdelta) or "days" in str(tdelta):
                        daystring = str(tdelta).split(",")[0]
                        noofdays = str(daystring).split(" ")[0]
                        daysmins = int(noofdays)*1440
                        thoursstr =  str(tdelta).split(",")[1]
                        thours = str(thoursstr).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(thoursstr).split(":")[1]
                        finalmins = int(hrs)+int(tmins)+int(daysmins)
                    else:
                        thours = str(tdelta).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(tdelta).split(":")[1]
                        finalmins = int(hrs)+int(tmins)
                    totaltime += finalmins
                

                totalhours =totaltime
                hour = int (totalhours) // 60
                if (len(str(hour)) < 2):
                    hours = "0"+str(hour)
                else:
                    hours = str(hour)
                
                mins = int (totalhours) % 60
                if (len(str(mins)) < 2):
                    minutes = "0"+str(mins)
                else:
                    minutes = str(mins)
                
                
                f['user_name'] = str(taskobject.AssignTo)
                f['task_time'] = str(hours) + ":" + str(minutes) + " hrs"
                taskdata.append(f)
            return Response({"n": 1,"data":taskdata[0], "Msg": "Task found Successfully", "Status": "Success"})
        return Response({"n": 0, "Msg": "Task not found", "Status": "Failed"})
    return Response({"n": 0, "Msg": "Task not found", "Status": "Failed"})
        
        


@api_view(['POST'])
def updateTask(request):
    data = {'n': '', 'Msg': '', 'Status': ''}
    try:
        taskID = request.query_params.get('taskID')

        if taskID is None:
            data['n'] = 0
            data['Msg'] = 'task ID is none'
            data['Status'] = "Failed"
        else:
            try:
                task = TaskMaster.objects.get(id=taskID)
            except Exception as e:
                data['n'] = 0
                data['Msg'] = 'TASK DOES NOT EXIST'
                data['Status'] = "Failed"
            else:
                if task.CheckedBy is None:
                    if request.data['AssignBy'] == '' or request.data['AssignBy'] == None:
                        requestData = request.data.copy()
                        requestData['company_code'] = request.user.company_code
                        serializer = PostTaskMasterSerializer(
                            task,data=requestData , partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            data['n'] = 1
                            data['Msg'] = 'update successfull'
                            data['Status'] = "Success"
                        else:
                            data = serializer.errors
                    else:
                        requestData = request.data.copy()
                        requestData['company_code'] = request.user.company_code
                        serializer = PostTaskMasterSerializer(
                            task, data=requestData,partial=True)
                        if serializer.is_valid():
                            s = serializer.validated_data['AssignBy']
                            user = Users.objects.filter(id=s.id)
                            for u in user:
                                serializer.validated_data['AssignByStr'] = u.Firstname + \
                                    ' ' + u.Lastname
                            serializer.save()
                            data['n'] = 1
                            data['Msg'] = 'update successfull'
                            data['Status'] = "Success"
                        else:
                            data = serializer.errors
                else:
                    data['n'] = 0
                    data['Msg'] = 'This task has already been checked'
                    data['Status'] = "Failed"

        return Response(data=data)

    except Exception as e:
        data['n'] = 0
        data['Msg'] = 'try method failed'
        data['Status'] = "Failed"
        return Response(data=data)


@api_view(['POST'])
def holdTaskStatus(request):
    data = {'n': '', 'Msg': '', 'Status': ''}
    try:
        id = request.query_params.get('id')
        userid = request.user.id
        taskobject = TaskMaster.objects.filter(AssignTo=userid)
        taskser = GetTaskSerializer(taskobject,many=True)
        for i in taskser.data:
            if i['AssignBy'] == "" or i['AssignBy'] == None and i['Project'] == "" or i['Project'] == None:
                data['n'] = 0
                data['Msg'] = 'Manager and project has not been selected to some task please update that first.'
                data['Status'] = "Failed"
                return Response(data=data)

            elif i['AssignBy'] == "" or i['AssignBy'] == None:
                data['n'] = 0
                data['Msg'] = 'Manager has not been assigned to some task please update that first.'
                data['Status'] = "Failed"
                return Response(data=data)
            elif i['Project'] == "" or i['Project'] == None:
                data['n'] = 0
                data['Msg'] = 'Project has not been selected to some task please update that first.'
                data['Status'] = "Failed"
                return Response(data=data)
        task = TaskMaster.objects.get(id=id)
        if id is None:
            data['n'] = 0
            data['Msg'] = 'task ID is none'
            data['Status'] = "Failed"
        else:
            task = TaskMaster.objects.filter(id=id).last()
            projecttask = ProjectTasks.objects.filter(Task_id=id).last()
            if projecttask is None:
                data['n'] = 0
                data['Msg'] = 'Task Does Not Found in project tasks'
                data['Status'] = "Failed"
            else:
                projectendtime = projecttask.EndDate
                if projectendtime is None :
                    requestData = request.data.copy()
                    requestData['company_code'] = request.user.company_code
                    serializer = PostTaskMasterSerializerStatus(task, data=requestData,partial=True)
                    projecttaskserializer = ProjectTasksUpdateSerializer(
                        projecttask, data=requestData,partial=True)
                    if serializer.is_valid() and projecttaskserializer.is_valid():
                        serializer.validated_data["Active"] = False
                        serializer.validated_data["Status_id"] = 2
                        serializer.save()
                        projecttaskserializer.validated_data['EndDate'] = timezone.now(
                        )
                        projecttaskserializer.save()

                        data['n'] = 1
                        data['Msg'] = 'task onhold'
                        data['Status'] = "Success"
                    else:
                        data = serializer.errors
                else:
                    data['n'] = 0
                    data['Msg'] = 'task is already on hold'
                    data['Status'] = "Failure"
        return Response(data=data)

    except Exception as e:
        data['n'] = 0
        data['Msg'] = 'try method failed'
        data['Status'] = "Failed"
        return Response(data=data)


@api_view(['POST'])
def resumeTaskStatus(request):
    COMPANYCODE = request.user.company_code
    data = {'n': '', 'Msg': '', 'Status': ''}
    userid = request.user.id
    taskobject = TaskMaster.objects.filter(AssignTo=userid)
    taskser = GetTaskSerializer(taskobject,many=True)
    for i in taskser.data:
        if i['AssignBy'] == "" or i['AssignBy'] == None and i['Project'] == "" or i['Project'] == None:
            data['n'] = 0
            data['Msg'] = 'Manager and project has not been selected to some task please update that first.'
            data['Status'] = "Failed"
            return Response(data=data)

        elif i['AssignBy'] == "" or i['AssignBy'] == None:
            data['n'] = 0
            data['Msg'] = 'Manager has not been assigned to some task please update that first.'
            data['Status'] = "Failed"
            return Response(data=data)
        elif i['Project'] == "" or i['Project'] == None:
            data['n'] = 0
            data['Msg'] = 'Project has not been selected to some task please update that first.'
            data['Status'] = "Failed"
            return Response(data=data)
    getactive = TaskMaster.objects.filter(AssignTo=request.user, Active=True, Status_id=1).first()
    if getactive:
        getactiveup = TaskMaster.objects.filter(
        AssignTo=request.user, Active=True, Status_id=1).update(Status=2,Active=False)

        taskid = getactive.id
        EndDatet = timezone.now()
        projecttask = ProjectTasks.objects.filter(Task_id=taskid).order_by('-id').first()
        if projecttask is not None:
            projecttask.EndDate=EndDatet
            projecttask.save()

    try:
        id = request.query_params.get('id')
        task = TaskMaster.objects.get(id=id)
        if id is None:
            data['n'] = 0
            data['Msg'] = 'task ID is none'
            data['Status'] = "Failed"
        else:
            try:
                task = TaskMaster.objects.filter(id=id).last()
            except Exception as e:
                data['n'] = 0
                data['Msg'] = 'TASK DOES NOT EXIST'
                data['Status'] = "Failed"
            else:
                requestData = request.data.copy()
                requestData['company_code'] = request.user.company_code
                serializer = PostTaskMasterSerializerStatus(
                    task, data=requestData ,partial=True)
                if serializer.is_valid():
                    serializer.validated_data["Active"] = True
                    serializer.validated_data["Status_id"] = 1
                    serializer.save()
                    data['n'] = 1
                    data['Msg'] = 'task resume '
                    data['Status'] = "Success"
                    try:
                        projectserializer = ProjectTasksUpdateSerializer(
                            data={'Active': True, 'StartDate': timezone.now(), 'ParentTask': id, 'Task': id,'company_code':COMPANYCODE})
                    except Exception as e:
                        return Response({'Error': 'serializer not accepting data'})
                    else:
                        if projectserializer.is_valid():

                            data = {}
                            projectserializer.save()
                            data['n'] = 1
                            data['Msg'] = 'task resume '
                            data['Status'] = 'task started successfully'
                        else:
                            data['n'] = 0
                            data['Msg'] = 'failed'
                            data['Status'] = "Failed"
                            data['Error'] = serializer.errors
                        return Response(data)

                else:
                    data['n'] = 0
                    data['Msg'] = 'failed'
                    data['Status'] = "Failed"
                    data['Error'] = serializer.errors
        return Response(data=data)

    except Exception as e:
        data['n'] = 0
        data['Msg'] = 'try method failed'
        data['Status'] = "Failed"
        return Response(data=data)


@api_view(['POST'])
def closeTaskStatus(request):
    data = {'n': '', 'Msg': '', 'Status': ''}
    requestdata={}
    projectdata={}
    userid = request.user.id
    taskobject = TaskMaster.objects.filter(AssignTo=userid)
    taskser = GetTaskSerializer(taskobject,many=True)
    for i in taskser.data:
        if i['AssignBy'] == "" or i['AssignBy'] == None and i['Project'] == "" or i['Project'] == None:
            data['n'] = 0
            data['Msg'] = 'Manager and project has not been selected to some task please update that first.'
            data['Status'] = "Failed"
            return Response(data=data)

        elif i['AssignBy'] == "" or i['AssignBy'] == None:
            data['n'] = 0
            data['Msg'] = 'Manager has not been assigned to some task please update that first.'
            data['Status'] = "Failed"
            return Response(data=data)
        elif i['Project'] == "" or i['Project'] == None:
            data['n'] = 0
            data['Msg'] = 'Project has not been selected to some task please update that first.'
            data['Status'] = "Failed"
            return Response(data=data)
    id = request.query_params.get('id')
    task = TaskMaster.objects.get(id=id)
    if id is None:
        data['n'] = 0
        data['Msg'] = 'task ID is none'
        data['Status'] = "Failed"
    else:
        task = TaskMaster.objects.filter(id=id).first()
        if task is not None:
            status = task.Status_id
            if status == 1:
                projecttask = ProjectTasks.objects.filter(Task_id=id).last()
                requestdata['Status'] = 3
                requestdata['Active'] = False

                projectdata['company_code'] = request.user.company_code
                projectdata['EndDate']=request.POST.get("EndDate")

                serializer = PostTaskMasterSerializerStatus(task,data=requestdata,partial=True)
                projecttaskserializer = ProjectTasksUpdateSerializer(
                    projecttask, data=projectdata,partial=True)
                
                if serializer.is_valid() and projecttaskserializer.is_valid():
                    serializer.validated_data["Active"] = False
                    serializer.validated_data["Status_id"] = 3
                    serializer.save()
                    

                    projecttaskserializer.validated_data['EndDate'] = timezone.now(
                    )
                    projecttaskserializer.save()

                    data['n'] = 1
                    data['Msg'] = 'task closed succesfully'
                    data['Status'] = "Success"

            else:
                requestdata['Status'] = 3
                requestdata['Active'] = False
                serializer = PostTaskMasterSerializerStatus(task,data=requestdata,partial=True)
                if serializer.is_valid() :
                    serializer.validated_data["Active"] = False
                    serializer.validated_data["Status_id"] = 3
                    serializer.save()

                  
                    data['n'] = 1
                    data['Msg'] = 'task closed succesfully'
                    data['Status'] = "Success"

        else:
            data = serializer.errors
    return Response(data=data)



@api_view(['POST'])
def updateTaskZone(request):
    data = {'n': '', 'Msg': '', 'Status': ''}
    try:
        taskID = request.query_params.get('taskID')
        task = TaskMaster.objects.get(id=taskID)
        if taskID is None:
            data['n'] = 0
            data['Msg'] = 'task ID is none'
            data['Status'] = "Failed"
        else:
            try:
                task = TaskMaster.objects.get(id=taskID)
            except Exception as e:
                data['n'] = 0
                data['Msg'] = 'TASK DOES NOT EXIST'
                data['Status'] = "Failed"
            else:
                requestData = request.data.copy()
                requestData['company_code'] = request.user.company_code
                serializer = PostTaskMasterSerializer(task,data=requestData,partial=True)
                if serializer.is_valid():
                    serializer.validated_data['CheckedBy'] = request.user
                    serializer.save()

                    data['n'] = 1
                    data['Msg'] = 'update successfull'
                    data['Status'] = "Success"
                else:
                    data = serializer.errors
        return Response(data=data)

    except Exception as e:
        data['n'] = 0
        data['Msg'] = 'try method failed'
        data['Status'] = "Failed"
        return Response(data=data)


@api_view(['POST'])  # data comes with taskid, zone, bonus
def updateTaskZoneMultiple(request):
    data = {'n': '', 'Msg': '', 'Status': ''}
    jsonStr = str(request.data)

    checkjon = is_json(str(jsonStr))
    
    if checkjon == False:
        jsondatadumps = json.dumps(request.data)
        aList = json.loads(jsondatadumps)
    else:
        aList = json.loads(jsonStr)

    for k in aList:
        TaskID = k['Taskid']
        TaskTitle = k['TaskTitle']
        Zone = k['Zone']
        Bonus = k['Bonus']
        data = {"TaskTitle": TaskTitle, "Zone": Zone,"Bonus": Bonus}
        try:
            task = TaskMaster.objects.get(id=TaskID)
        except Exception as e:
            data['n'] = 0
            data['Msg'] = 'TASK DOES NOT EXIST'
            data['Status'] = "Failed"
        else:
            serializer = PostTaskMasterSerializer(task, data=data)
            taskobject = TaskMaster.objects.filter(id=TaskID).first()
            if serializer.is_valid():
                if data['Zone'] is not None and taskobject.Zone_id != data['Zone']:
                    serializer.validated_data['CheckedBy'] = request.user
                serializer.save()
                data['n'] = 1
                data['Msg'] = 'update successfull'
                data['Status'] = "Success"
            else:
                data = serializer.errors
    return Response(data=data)


@api_view(['GET'])
def search(request):
    if request.method == 'GET':
        taskID = request.query_params.get('taskID', None)
        if taskID is not None:
            i = TaskMaster.objects.filter(id=taskID)
            serializer = SearchTaskMasterSerializer(i, many=True)
            return JsonResponse(serializer.data, safe=False)
        userID = request.query_params.get('userID', None)
        if userID is not None:
            u = TaskMaster.objects.filter(AssignTo=userID)
            serializer = GetTaskMasterSerializer(u, many=True)
            return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
def getTaskByDate(request):
    if request.method == 'POST':
        userid = int(request.data['AssignTo'])
        Year = request.data['Year']
        Week = request.POST.getlist('Week')

        if Week == []:
            Week = request.data.get('Week')
        else:
            Week = request.POST.getlist('Week')
        Status = request.POST.getlist('Status')
        if Status == []:
            Status = request.data.get('Status')
        else:
            Status = request.POST.getlist('Status')

        Zone = request.data.get('Zone')

        GreenZoneTask = 0
        YellowZoneTask = 0
        RedZoneTask = 0
        NotdoneZoneTask = 0
        bonus = 0
        cancelledZoneTask=0
        rejectedZoneTask=0
        finalcredit=0

        taskpointsper = 0
        greencountmultiple = 0
        yellowcountmultiple = 0
        redcountmultiple = 0
        notdonecountmultiple = 0
        rejectcountmultiple = 0
        bonuscountmultiple = 0

        trackprorules = rulestrackpro.objects.filter(is_active=True,company_code=request.user.company_code)
        if trackprorules is not None:
            trackproser = trackproruleserializer(trackprorules,many=True)
            for w in trackproser.data:
                if w['color'] == "green":
                    taskpointsper = int(w['points']) 
                if w['color'] == "green":
                    greencountmultiple = int(w['points'])
                if w['color'] == "yellow":
                    yellowcountmultiple = int(w['points'])
                if w['color'] == "red":
                    redcountmultiple = int(w['points'])
                if w['color'] == "notdone":
                    notdonecountmultiple = int(w['points'])
                if w['color'] == "reject":
                    rejectcountmultiple = int(w['points'])
                if w['color'] == "bonus":
                    bonuscountmultiple = int(w['points'])

        my_date = datetime.date.today()
        year, week_num, day_of_week = my_date.isocalendar()
        week = week_num
        crryear = year

        tasks = TaskMaster.objects.filter(
                AssignTo=userid, Year=crryear, Week=week).count()
        
        totaltask = TaskMaster.objects.filter(AssignTo=userid).count()

        trackpropercentavg = IntermediateTrackProResult.objects.filter(
                Employee=userid).aggregate(Avg('TrackProPercent'))

        for k in [trackpropercentavg]:
            if k['TrackProPercent__avg'] is not None:
                trackpropercnt = round(k['TrackProPercent__avg'],2)
            else:
                trackpropercnt=0
        if Week is None:
            Week=[]
        if len(Week) == 1:
            trackpropercentage = IntermediateTrackProResult.objects.filter(Employee=userid,Week__in = Week,Year=Year).first()
            if trackpropercentage is not None:
                weekpercentage = trackpropercentage.TrackProPercent
            else:
                weekpercentage = 0
        else:
            weekpercentage = 0
          
       

        if Zone == "Unchecked":
            i = TaskMaster.objects.filter(
                Year=Year, Week__in=Week,AssignTo=userid,Status__in=Status,Zone__isnull= True).order_by('Status','-AssignDate')
        elif Zone == "Checked":
            i = TaskMaster.objects.filter(
                Year=Year, Week__in=Week,AssignTo=userid,Status__in=Status,Zone__isnull= False).order_by('Status','-AssignDate')
        else:
            i = TaskMaster.objects.filter(
                Year=Year, Week__in=Week,AssignTo=userid,Status__in=Status).order_by('Status','-AssignDate')
        
        
        for w in Week:
            weekGreenZoneTask = 0
            weekYellowZoneTask = 0
            weekRedZoneTask = 0
            weekNotdoneZoneTask = 0
            weekbonus = 0
            weekcancelledZoneTask=0
            weekrejectedZoneTask=0
            creditamount=0

            weeknum = int(w)
            if Zone == "Unchecked":
                taskobjweek = TaskMaster.objects.filter(
                    Year=Year, Week=weeknum,AssignTo=userid,Status__in=Status,Zone__isnull= True).order_by('Status')
            elif Zone == "Checked":
                taskobjweek = TaskMaster.objects.filter(
                    Year=Year, Week=weeknum,AssignTo=userid,Status__in=Status,Zone__isnull= False).order_by('Status')
            else:
                taskobjweek = TaskMaster.objects.filter(
                    Year=Year, Week=weeknum,AssignTo=userid,Status__in=Status).order_by('Status')

            weekserializer = PostTaskMasterSerializer(taskobjweek, many=True)

            for r in weekserializer.data:
                if r['Zone'] == 1:
                    r['green'] = greencountmultiple
                    weekGreenZoneTask += r['green']
                elif r['Zone'] == 2:
                    r['yellow'] = yellowcountmultiple
                    weekYellowZoneTask += r['yellow']
                elif r['Zone'] == 3:
                    r['red'] = redcountmultiple
                    weekRedZoneTask += r['red']
                elif r['Zone'] == 4:
                    r['notdone'] = notdonecountmultiple
                    weekNotdoneZoneTask += r['notdone']
                elif r['Zone'] == 5:
                    r['cancelled'] = 1
                    weekcancelledZoneTask += r['cancelled']
                elif r['Zone'] == 6:
                    r['rejected'] = rejectcountmultiple
                    weekrejectedZoneTask += r['rejected']
                if r['Bonus'] == True:
                    r['isBonus'] = bonuscountmultiple
                    weekbonus += r['isBonus']

                greenzonecreditpoints = int(weekGreenZoneTask/greencountmultiple)
                ZoneNoneList = ""  
                if greenzonecreditpoints >= 10 and greenzonecreditpoints <= 14:
                    creditamount =  int(3*greencountmultiple)
                elif greenzonecreditpoints >= 15 and greenzonecreditpoints <= 19:
                    creditamount =  int(7*greencountmultiple)
                elif greenzonecreditpoints >= 20 and greenzonecreditpoints <= 24:
                    creditamount =  int(12*greencountmultiple)
                elif greenzonecreditpoints >= 25 and greenzonecreditpoints <= 29:
                    creditamount =  int(18*greencountmultiple)



            finalcredit += creditamount


        if i.exists():
            serializer = PostTaskMasterSerializer(i, many=True)
            for i in serializer.data:
                i['task_remark_count'] = TaskRemark.objects.filter(task_id=i['id']).count()
                if i['Zone'] == 1:
                    i['green'] = greencountmultiple
                    GreenZoneTask += i['green']
                elif i['Zone'] == 2:
                    i['yellow'] = yellowcountmultiple
                    YellowZoneTask += i['yellow']
                elif i['Zone'] == 3:
                    i['red'] = redcountmultiple
                    RedZoneTask += i['red']
                elif i['Zone'] == 4:
                    i['notdone'] = notdonecountmultiple
                    NotdoneZoneTask += i['notdone']
                elif i['Zone'] == 5:
                    i['cancelled'] = 1
                    cancelledZoneTask += i['cancelled']
                elif i['Zone'] == 6:
                    i['rejected'] = rejectcountmultiple
                    rejectedZoneTask += i['rejected']
                if i['Bonus'] == True:
                    i['isBonus'] = bonuscountmultiple
                    bonus += i['isBonus']

                # if GreenZoneTask >= 200 and GreenZoneTask <= 280:
                #     creditamount =  60
                # elif GreenZoneTask >= 300 and GreenZoneTask <= 380:
                #     creditamount =  140
                # elif GreenZoneTask >= 400 and GreenZoneTask <= 480:
                #     creditamount =  240
                # elif GreenZoneTask >= 500 and GreenZoneTask <= 580:
                #     creditamount =  360

                greenzonecreditpoints = int(GreenZoneTask/greencountmultiple)
                ZoneNoneList = ""  
                if greenzonecreditpoints >= 10 and greenzonecreditpoints <= 14:
                    creditamount =  int(3*greencountmultiple)
                elif greenzonecreditpoints >= 15 and greenzonecreditpoints <= 19:
                    creditamount =  int(7*greencountmultiple)
                elif greenzonecreditpoints >= 20 and greenzonecreditpoints <= 24:
                    creditamount =  int(12*greencountmultiple)
                elif greenzonecreditpoints >= 25 and greenzonecreditpoints <= 29:
                    creditamount =  int(18*greencountmultiple)

                currentzone = pytz.timezone("Asia/Kolkata") 
                currenttime = datetime.datetime.now(currentzone)
                newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                taskobj = TaskMaster.objects.filter(id=i['id']).first()
                taskidlist = []
                if taskobj.ParentTaskId is not None:
                    parenttaskid  = taskobj.ParentTaskId
                    taskidlist.append(parenttaskid)
                    taskobject = TaskMaster.objects.filter(ParentTaskId=parenttaskid)
                    taskser = PostTaskMasterSerializer(taskobject,many=True)
                    for t in taskser.data:
                        taskidlist.append(t['id'])
                else:
                    taskidlist.append(i['id'])
                    taskobject = TaskMaster.objects.filter(ParentTaskId=i['id'])
                    taskser = PostTaskMasterSerializer(taskobject,many=True)
                    for t in taskser.data:
                        taskidlist.append(t['id'])

                projecttask = ProjectTasks.objects.filter(Task_id__in=taskidlist)
                if projecttask:
                    projectser = ProjectTasksSerializer(projecttask,many=True)
                    FMT = '%H:%M:%S.%f'
                    totaltime=0
                
                    for p in projectser.data:
                        startstring = p['StartDate']
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = p['EndDate']
                        if endstring :
                            endtime = p['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        tdelta=t2-t1
                    
                    
                        if "day" in str(tdelta) or "days" in str(tdelta):
                            daystring = str(tdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(tdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            finalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            thours = str(tdelta).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(tdelta).split(":")[1]
                            finalmins = int(hrs)+int(tmins)
                        totaltime += finalmins

                    totalhours =totaltime
                    hour = int (totalhours) // 60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalhours) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                    i['taskhours'] = hourstring

                if i['Zone'] == 1:
                    greenstatusstr = "<img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    greenstatusstr = "<img src='/static/Media/taskicons/nongreen.svg' id='1' class='nonactive' alt='Paris'>"

                if i['Zone'] == 2:
                    yellowstatusstr = "<img src='/static/Media/taskicons/activeyellowpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    yellowstatusstr = "<img src='/static/Media/taskicons/yellow.svg' id='2' class='nonactive' alt='Paris'>"

                if i['Zone'] == 3:
                    redstatusstr = "<img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='Paris' >"
                else:
                    redstatusstr = "<img src='/static/Media/taskicons/red.svg' id='3' class='nonactive' alt='Paris'>"

                if i['Zone'] == 4:
                    notdonestr = "<img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='Paris'>"
                else:
                    notdonestr = "<img src='/static/Media/taskicons/notdone.svg' id='4' class='nonactive' alt='Paris' >"

                if i['Zone'] == 5:
                    cancelledstr = "<img src='/static/Media/taskicons/activecancelledpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    cancelledstr = "<img src='/static/Media/taskicons/cancelled.svg' id='5' class='nonactive' alt='Paris'>"

                if i['Zone'] == 6:
                    rejectedstr = "<img src='/static/Media/taskicons/activerejectpoints.svg' class='activeicons' alt='Paris'>"
                else:
                    rejectedstr = "<img src='/static/Media/taskicons/rejected.svg' id='6' class='nonactive' alt='Paris'>"

                i['greenstatusstr']=greenstatusstr
                i['yellowstatusstr']=yellowstatusstr
                i['redstatusstr']=redstatusstr
                i['notdonestr']=notdonestr
                i['cancelledstr']=cancelledstr
                i['rejectedstr']=rejectedstr

                datestr = i['AssignDate']
                newdate = datetime.datetime.strptime(datestr,"%Y-%m-%d")
                newmonthdate = newdate.strftime("%d-%B-%Y")
                i['AssignDate']=newmonthdate

                empuser = Users.objects.filter(id=i['AssignTo']).first()
                if empuser:
                    i['empstr'] = empuser.Firstname +" "+empuser.Lastname

                if i['Bonus'] == True:
                    bonusstr = "<img src='/static/Media/taskicons/activebonuspoints.svg' alt='Paris' id='bonustask"+str(i['id'])+"'>"
                    bonushiddenstr = "True"
                    mbonus = True

                else:
                    bonusstr = "<img src='/static/Media/taskicons/bonus.svg' alt='Paris'  id ='bonustask"+str(i['id'])+"'>"
                    bonushiddenstr = "False"
                    mbonus = False

                i['Bonus'] = bonusstr
                i['m_bonus'] = mbonus
            context={
                'serdata':serializer.data,
                'weeektaskcount':tasks,
                'totaltaskscount':totaltask,
                'trackpropercentavg':trackpropercnt,
                'GreenZoneTask':GreenZoneTask,
                'YellowZoneTask':YellowZoneTask,
                'RedZoneTask':RedZoneTask,
                'NotdoneZoneTask':NotdoneZoneTask,
                'cancelledZoneTask':cancelledZoneTask,
                'rejectedZoneTask':rejectedZoneTask,
                'bonus':bonus,
                'extracredits':finalcredit,
                'Weeklyperc':weekpercentage,
            }
        else:
            context={
                'serdata':[],
                'weeektaskcount':tasks,
                'totaltaskscount':totaltask,
                'trackpropercentavg':trackpropercnt,
                'GreenZoneTask':GreenZoneTask,
                'YellowZoneTask':YellowZoneTask,
                'RedZoneTask':RedZoneTask,
                'NotdoneZoneTask':NotdoneZoneTask,
                'cancelledZoneTask':cancelledZoneTask,
                'rejectedZoneTask':rejectedZoneTask,
                'bonus':bonus,
                'extracredits':finalcredit,
                'Weeklyperc':weekpercentage
            }
           
        
        return JsonResponse(context, safe=False)
    


@api_view(['POST'])
def getTaskBymanagerDate(request):
    if request.method == 'POST':
        userid = request.POST.getlist('AssignTo')
        if userid == []:
            userid = request.data.get('AssignTo')
        else:
            userid =  request.POST.getlist('AssignTo')

        Year = request.data['Year']

        Week = request.POST.getlist('Week')
        if Week == []:
            Week = request.data.get('Week')
        else:
            Week =  request.POST.getlist('Week')

        managerid = request.data['Assigby'] 

        Status = request.POST.getlist('Status')
        if Status == []:
            Status = request.data.get('Status')
        else:
            Status =  request.POST.getlist('Status')

        Zone = request.data['Zone']
        GreenZoneTask = 0
        YellowZoneTask = 0
        RedZoneTask = 0
        NotdoneZoneTask = 0
        bonus = 0
        cancelledZoneTask=0
        rejectedZoneTask=0
        finalcredit=0

        taskpointsper = 0
        greencountmultiple = 0
        yellowcountmultiple = 0
        redcountmultiple = 0
        notdonecountmultiple = 0
        rejectcountmultiple = 0
        bonuscountmultiple = 0

        trackprorules = rulestrackpro.objects.filter(is_active=True,company_code=request.user.company_code)
        if trackprorules is not None:
            trackproser = trackproruleserializer(trackprorules,many=True)
            for w in trackproser.data:
                if w['color'] == "green":
                    taskpointsper = int(w['points']) 
                if w['color'] == "green":
                    greencountmultiple = int(w['points'])
                if w['color'] == "yellow":
                    yellowcountmultiple = int(w['points'])
                if w['color'] == "red":
                    redcountmultiple = int(w['points'])
                if w['color'] == "notdone":
                    notdonecountmultiple = int(w['points'])
                if w['color'] == "reject":
                    rejectcountmultiple = int(w['points'])
                if w['color'] == "bonus":
                    bonuscountmultiple = int(w['points'])

        my_date = datetime.date.today()
        year, week_num, day_of_week = my_date.isocalendar()
        week = week_num
        crryear = year

        tasks = TaskMaster.objects.filter(
                AssignTo__in=userid, Year=crryear, Week=week).count()
        
        totaltask = TaskMaster.objects.filter(AssignTo__in=userid).count()

        trackpropercentavg = IntermediateTrackProResult.objects.filter(
                Employee__in=userid).aggregate(Avg('TrackProPercent'))
        
        for k in [trackpropercentavg]:
            if k['TrackProPercent__avg'] is not None:
                trackpropercnt = round(k['TrackProPercent__avg'],2)
            else:
                trackpropercnt=0
        
        if Zone == "Unchecked":
            taskobj = TaskMaster.objects.filter(
                Year=Year, Week__in=Week,AssignTo__in=userid,AssignBy=managerid,Status__in=Status,Zone__isnull= True).order_by('-id')
            
        elif Zone == "Checked":
            taskobj = TaskMaster.objects.filter(
                Year=Year, Week__in=Week,AssignTo__in=userid,AssignBy=managerid,Status__in=Status,Zone__isnull= False).order_by('-id')
        else:
            taskobj = TaskMaster.objects.filter(
                Year=Year, Week__in=Week,AssignTo__in=userid,AssignBy=managerid,Status__in=Status).order_by('-id')


        for w in Week:
            weekGreenZoneTask = 0
            weekYellowZoneTask = 0
            weekRedZoneTask = 0
            weekNotdoneZoneTask = 0
            weekbonus = 0
            weekcancelledZoneTask=0
            weekrejectedZoneTask=0
            creditamount=0

            weeknum = int(w)
            if Zone == "Unchecked":
                taskobjweek = TaskMaster.objects.filter(
                Year=Year, Week = weeknum,AssignTo__in=userid,AssignBy=managerid,Status__in=Status,Zone__isnull= True).order_by('-id')
            
            elif Zone == "Checked":
                taskobjweek = TaskMaster.objects.filter(
                Year=Year, Week = weeknum,AssignTo__in=userid,AssignBy=managerid,Status__in=Status,Zone__isnull= False).order_by('-id')
            else:
                taskobjweek = TaskMaster.objects.filter(
                Year=Year, Week = weeknum,AssignTo__in=userid,AssignBy=managerid,Status__in=Status).order_by('-id')

            weekserializer = PostTaskMasterSerializer(taskobjweek, many=True)

            for r in weekserializer.data:
                if r['Zone'] == 1:
                    r['green'] = greencountmultiple
                    weekGreenZoneTask += r['green']
                elif r['Zone'] == 2:
                    r['yellow'] = yellowcountmultiple
                    weekYellowZoneTask += r['yellow']
                elif r['Zone'] == 3:
                        r['red'] = redcountmultiple
                        weekRedZoneTask += r['red']
                elif r['Zone'] == 4:
                    r['notdone'] = notdonecountmultiple
                    weekNotdoneZoneTask += r['notdone']
                elif r['Zone'] == 5:
                    r['cancelled'] = 1
                    weekcancelledZoneTask += r['cancelled']
                elif r['Zone'] == 6:
                    r['rejected'] = rejectcountmultiple
                    weekrejectedZoneTask += r['rejected']
                if r['Bonus'] == True:
                    r['isBonus'] = bonuscountmultiple
                    weekbonus += r['isBonus']

                greenzonecreditpoints = int(weekGreenZoneTask/greencountmultiple)
                ZoneNoneList = ""  
                if greenzonecreditpoints >= 10 and greenzonecreditpoints <= 14:
                    creditamount =  int(3*greencountmultiple)
                elif greenzonecreditpoints >= 15 and greenzonecreditpoints <= 19:
                    creditamount =  int(7*greencountmultiple)
                elif greenzonecreditpoints >= 20 and greenzonecreditpoints <= 24:
                    creditamount =  int(12*greencountmultiple)
                elif greenzonecreditpoints >= 25 and greenzonecreditpoints <= 29:
                    creditamount =  int(18*greencountmultiple)


                # if weekGreenZoneTask >= 200 and weekGreenZoneTask <= 280:
                #     creditamount =  60
                # elif weekGreenZoneTask >= 300 and weekGreenZoneTask <= 380:
                #     creditamount =  140
                # elif weekGreenZoneTask >= 400 and weekGreenZoneTask <= 480:
                #     creditamount =  240
                # elif weekGreenZoneTask >= 500 and weekGreenZoneTask <= 580:
                #     creditamount =  360
            finalcredit += creditamount


        serializer = PostTaskMasterSerializer(taskobj, many=True)

        
        for i in serializer.data:

            if i['Zone'] == 1:
                i['green'] = greencountmultiple
                GreenZoneTask += i['green']
            elif i['Zone'] == 2:
                i['yellow'] = yellowcountmultiple
                YellowZoneTask += i['yellow']
            elif i['Zone'] == 3:
                i['red'] = redcountmultiple
                RedZoneTask += i['red']
            elif i['Zone'] == 4:
                i['notdone'] = notdonecountmultiple
                NotdoneZoneTask += i['notdone']
            elif i['Zone'] == 5:
                 i['cancelled'] = 1
                 cancelledZoneTask += i['cancelled']
            elif i['Zone'] == 6:
                i['rejected'] = rejectcountmultiple
                rejectedZoneTask += i['rejected']
            if i['Bonus'] == True:
                i['isBonus'] = bonuscountmultiple
                bonus += i['isBonus']

            datestr = i['AssignDate']
            newdate = datetime.datetime.strptime(datestr,"%Y-%m-%d")
            newmonthdate = newdate.strftime("%d-%B-%Y")
            i['AssignDate']=newmonthdate

            empuser = Users.objects.filter(id=i['AssignTo']).first()
            if empuser:
                i['empstr'] = empuser.Firstname +" "+empuser.Lastname

            currentzone = pytz.timezone("Asia/Kolkata") 
            currenttime = datetime.datetime.now(currentzone)
            newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        
            projecttask = ProjectTasks.objects.filter(Task_id=i['id'])
            if projecttask:
                projectser = ProjectTasksSerializer(projecttask,many=True)
                FMT = '%H:%M:%S.%f'
                totaltime=0
               
                for p in projectser.data:
                    startstring = p['StartDate']
                    starttime=startstring
                    t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                    endstring = p['EndDate']
                    if endstring :
                        endtime = p['EndDate']
                    else:
                        endtime = str(newcurrenttime)
                    t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                    tdelta=t2-t1
                  
                   
                    if "day" in str(tdelta) or "days" in str(tdelta):
                        daystring = str(tdelta).split(",")[0]
                        noofdays = str(daystring).split(" ")[0]
                        daysmins = int(noofdays)*1440

                        thoursstr =  str(tdelta).split(",")[1]
                        thours = str(thoursstr).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(thoursstr).split(":")[1]
                        finalmins = int(hrs)+int(tmins)+int(daysmins)
                    else:
                        thours = str(tdelta).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(tdelta).split(":")[1]
                        finalmins = int(hrs)+int(tmins)
                    totaltime += finalmins

                totalhours =totaltime
                hour = int (totalhours) // 60
                if (len(str(hour)) < 2):
                    hours = "0"+str(hour)
                else:
                    hours = str(hour)

                mins = int (totalhours) % 60
                if (len(str(mins)) < 2):
                    minutes = "0"+str(mins)
                else:
                    minutes = str(mins)

                hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"
               
                i['taskhours'] = hourstring

            if i['Zone'] == 1:
                zonestr =  "<span class='status-btn greenstatus-btn'>Green</span>"
            elif i['Zone'] == 2:
                zonestr ="<span class='status-btn yellowstatus-btn'>Yellow</span>"
            elif i['Zone'] == 3:
                zonestr = "<span class='status-btn redstatus-btn'>Red</span>"    
            elif i['Zone'] == 4:
                zonestr = "<span class='status-btn notdonestatus-btn'>Not Done</span>"    
            elif i['Zone'] == 5:
                zonestr = "<span class='status-btn cancelledstatus-btn'>Cancelled</span>"    
            elif i['Zone'] == 6:
                zonestr = "<span class='status-btn rejectedstatus-btn'>Rejected</span>"    
            else:
                zonestr = ""             
            
            i['zonestr'] = zonestr

            if i['Zone'] == 1:
                greenstatusstr = "<img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='Paris'>"
            else:
                greenstatusstr = "<img src='/static/Media/taskicons/nongreen.svg' id='1' class='nonactive' alt='Paris' onclick='Zonemarks(this.id,"+str(i['id'])+")'>"

            if i['Zone'] == 2:
                yellowstatusstr = "<img src='/static/Media/taskicons/activeyellowpoints.svg' class='activeicons' alt='Paris'>"
            else:
                yellowstatusstr = "<img src='/static/Media/taskicons/yellow.svg' id='2' class='nonactive' alt='Paris' onclick='Zonemarks(this.id,"+str(i['id'])+")'>"

            if i['Zone'] == 3:
                redstatusstr = "<img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='Paris' >"
            else:
                redstatusstr = "<img src='/static/Media/taskicons/red.svg' id='3' class='nonactive' alt='Paris' onclick='Zonemarks(this.id,"+str(i['id'])+")'>"

            if i['Zone'] == 4:
                notdonestr = "<img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='Paris'>"
            else:
                notdonestr = "<img src='/static/Media/taskicons/notdone.svg' id='4' class='nonactive' alt='Paris' onclick='Zonemarks(this.id,"+str(i['id'])+")'>"

            if i['Zone'] == 5:
                cancelledstr = "<img src='/static/Media/taskicons/activecancelledpoints.svg' class='activeicons' alt='Paris'>"
            else:
                cancelledstr = "<img src='/static/Media/taskicons/cancelled.svg' id='5' class='nonactive' alt='Paris' onclick='Zonemarks(this.id,"+str(i['id'])+")'>"

            if i['Zone'] == 6:
                rejectedstr = "<img src='/static/Media/taskicons/activerejectpoints.svg' class='activeicons' alt='Paris'>"
            else:
                rejectedstr = "<img src='/static/Media/taskicons/rejected.svg' id='6' class='nonactive' alt='Paris' onclick='Zonemarks(this.id,"+str(i['id'])+")'>"

            i['greenstatusstr']=greenstatusstr
            i['yellowstatusstr']=yellowstatusstr
            i['redstatusstr']=redstatusstr
            i['notdonestr']=notdonestr
            i['cancelledstr']=cancelledstr
            i['rejectedstr']=rejectedstr

            if i['Bonus'] == True:
                bonusstr = "<img src='/static/Media/taskicons/activebonuspoints.svg' alt='Paris' id='bonustask"+str(i['id'])+"'  onclick='taskbonus("+str(i['id'])+")'>"
                bonushiddenstr = "True"
            else:
                bonusstr = "<img src='/static/Media/taskicons/bonus.svg' alt='Paris'  id ='bonustask"+str(i['id'])+"'  onclick='taskbonus("+str(i['id'])+")'>"
                bonushiddenstr = "False"

            i['Bonus'] = bonusstr
            i['bonushiddenstr'] = bonushiddenstr

        context={
            'serdata':serializer.data,
            'weeektaskcount':tasks,
            'totaltaskscount':totaltask,
            'trackpropercentavg':trackpropercnt,
            'GreenZoneTask':GreenZoneTask,
            'YellowZoneTask':YellowZoneTask,
            'RedZoneTask':RedZoneTask,
            'NotdoneZoneTask':NotdoneZoneTask,
            'cancelledZoneTask':cancelledZoneTask,
            'rejectedZoneTask':rejectedZoneTask,
            'bonus':bonus,
            'extracredits':finalcredit,
        }
    return JsonResponse(context, safe=False)


@api_view(['GET'])
def getDate(request):
    data = {"n": 0, "Msg": "", "Status": ""}
    date = request.query_params.get('AssignDate', None)
    try:
        if date is not None:
            i = TaskMaster.objects.filter(AssignDate=date)
            serializer = GetTaskMasterSerializer(i, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse({"n": 0, "Msg": "Failed", "Status": "Date is None"})

    except Exception as e:
        print(e)


@api_view(['GET'])
def yearList(request, format=None):
    if request.method == 'GET':
        year = TaskMaster.objects.order_by('Year').distinct('Year').reverse()
        serializer = YearSerializer(year, many=True)
        return Response(serializer.data)

# later on combine weekList and userWeekList into one


@api_view(['GET'])
def weekList(request, format=None):
    year = request.query_params.get('year', None)
    if year is not None:
        week = TaskMaster.objects.filter(Year=year).order_by(
            'Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)
        return Response(serializer.data)
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})


@api_view(['POST'])
def userWeekList(request, format=None):
    assignTo = request.data.get('userID', None)
    year = request.data.get('Year', None)
    if year is not None:
        week = TaskMaster.objects.filter(Year=year, AssignTo=assignTo).order_by(
            'Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)
        return Response({"data":serializer.data})
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})
    


@api_view(['POST'])
def managertaskWeekList(request, format=None):
    assignTo = request.data.get('userID', None)
    year = request.data.get('Year', None)
    if year is not None:
        week = TaskMaster.objects.filter(Year=year, AssignBy=assignTo).order_by(
            'Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)
        return Response({"data":serializer.data})
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})
    

@api_view(['POST'])
def managerWeekList(request, format=None):
    assignby = request.data.get('userID', None)
    year = request.data.get('Year', None)
    if year is not None:
        week = TaskMaster.objects.filter(Year=year, AssignBy=assignby).order_by(
            'Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)
        return Response(serializer.data)
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})


@api_view(['GET'])
def zoneList(request, format=None):
    if request.method == 'GET':
        zone = Zone.objects.all().order_by('id').reverse()
        serializer = ZoneSerializer(zone, many=True)
        return Response(serializer.data)


class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 1000


class GetAllTaskData(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination
    querylist = [
        {'queryset': Users.objects.order_by(
            'Firstname'), 'serializer_class': UserSerializer},
        {'queryset': TaskMaster.objects.all().order_by(
            'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
        {'queryset': Zone.objects.all().order_by('id').reverse(),
         'serializer_class': ZoneSerializer},
        {'queryset': IntermediateTrackProResult.objects.all(
        ), 'serializer_class': IntermediateGetTrackProResultSerializer},
        {'queryset': TaskMaster.objects.values('Year').distinct().order_by(
            'Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
        {'queryset': IntermediateTrackProResult.objects.values('Year').distinct().order_by(
            'Year').reverse(), 'serializer_class': YearSerializer, 'label': 'trackproyear'}
    ]
 # get combined data for a single user


class GetUserTaskData(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination

    def get_querylist(self):
        userID = self.request.query_params['userID']
        company_code = self.request.user.company_code
        querylist = (
            {'queryset': Users.objects.filter(id=userID).order_by(
                'Firstname'), 'serializer_class': UserSerializer},
            {'queryset': TaskMaster.objects.filter(AssignTo=userID).order_by(
                'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
            {'queryset': IntermediateTrackProResult.objects.filter(
                Employee=userID), 'serializer_class': IntermediateGetTrackProResultSerializer},
            {'queryset': TaskMaster.objects.filter(AssignTo=userID).values('Year').distinct(
            ).order_by('Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
            {'queryset': ProjectMaster.objects.filter(Active=True,company_code=company_code).order_by(
                'ProjectName').reverse(), 'serializer_class': ProjectSerializer},
        )
        return querylist
    

class GetmanagerTaskData(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination

    def get_querylist(self):
        managerid = self.request.query_params['managerid']
        company_code = self.request.user.company_code
        querylist = (
            {'queryset': Users.objects.filter(id=managerid).order_by(
                'Firstname'), 'serializer_class': UserSerializer},
            {'queryset': TaskMaster.objects.filter(AssignBy=managerid).order_by(
                'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
            {'queryset': TaskMaster.objects.filter(AssignBy=managerid).values('Year').distinct(
            ).order_by('Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
            {'queryset': ProjectMaster.objects.filter(Active=True,company_code=company_code).order_by(
                'ProjectName').reverse(), 'serializer_class': ProjectSerializer},
        )
        return querylist

 


class Mytrackproscoredata(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination

    def get_querylist(self):
        userID = self.request.query_params['userID']
        querylist = (
            {'queryset': Users.objects.filter(id=userID).order_by(
                'Firstname'), 'serializer_class': UserSerializer},
            {'queryset': TaskMaster.objects.filter(AssignTo=userID).order_by(
                'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
            {'queryset': IntermediateTrackProResult.objects.filter(Employee=userID).order_by(
                'Year').order_by('Week'), 'serializer_class': IntermediateGetTrackProResultSerializer},
            {'queryset': IntermediateTrackProResult.objects.filter(Employee=userID).values('Year').distinct(
            ).order_by('Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
        )
        return querylist

# three parameter task data
# call on ajax


@api_view(['POST'])
def ThreeParamTaskData(request, format=None):
    assignTo = request.data.get('userID', None)
    year = request.data.get('Year', None)
    week = request.data.get('Week', None)
    if assignTo is None or year is None or week is None:
        return Response({"n": 0, "Msg": "Missing Parameter", "Status": "Failed"})
    Task = TaskMaster.objects.filter(
        Year=year, AssignTo=assignTo, Week=week).order_by('-AssignDate')
    serializer = PostTaskMasterSerializer(Task, many=True)
    return Response(serializer.data)
    # else:
    #     return Response({"n":0,"Msg":"Failed","Status":"Year value is None"})


@api_view(['GET'])
def assignUserTask(request, format=None):
    userID = request.query_params.get('userID', None)
    if userID is not None:
        userID = Users.objects.exclude(id=userID).order_by('Firstname')
        serializer = UserSerializer(userID, many=True)
        return Response(serializer.data)
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def cronejob(request):
    # officetime = parse_datetime("2012-02-21 20:30:00")
    dt=timezone.now()
    officetime=dt.replace(hour=21, minute=00,second=00)
    off=str(officetime).split('.')[0]
    endtime = pytz.timezone("Asia/Kolkata").localize(parse_datetime(off), is_dst=None)

    # currentzone = pytz.timezone("Asia/Kolkata") 
    currenttime = timezone.localtime(timezone.now())

    if request.method == 'POST':
        Task = TaskMaster.objects.filter(Active=True, Status=1)
        for status in Task:
            serializer = PostTaskMasterSerializer(
                status, data={"Active": False, "Status": 2}, partial=True)
            if serializer.is_valid():
                serializer.save()
                taskid = serializer.data['id']
                projecttask = ProjectTasks.objects.filter(
                    Task_id=taskid).last()
                projecttaskserializer = ProjectTasksUpdateSerializer(
                    projecttask, data={"Active": False, "EndDate": currenttime}, partial=True)
                if projecttaskserializer.is_valid():
                    projecttaskserializer.save()
        return Response({"n": 1, "Msg": "All Tasks on Hold", "Status": "Success"})
    return Response({"n": 0, "Msg": "No Active Tasks", "Status": "Failed"})

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def weeklycronejob(request):
    if request.method == 'POST':
        my_date = datetime.date.today()
        year, week_num, day_of_week = my_date.isocalendar()
        currweek = week_num
        Task = TaskMaster.objects.filter(Week=currweek,Status=2)
        for status in Task:
            serializer = PostTaskMasterSerializer(
                status, data={"Status": 3}, partial=True)
            if serializer.is_valid():
                serializer.save()
        return Response({"n": 1, "Msg": "All Tasks are completed", "Status": "Success"})
    return Response({"n": 0, "Msg": "Active Tasks present", "Status": "Failed"})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def completeweeklycronejob(request):
    if request.method == 'POST':
        my_date = datetime.date.today()
        year, week_num, day_of_week = my_date.isocalendar()
        currweek = week_num
        prevweek = int(currweek)-1
        Task = TaskMaster.objects.filter(Week=prevweek,Status__in=[2,1])
        for status in Task:
            serializer = PostTaskMasterSerializer(
                status, data={"Status": 3}, partial=True)
            if serializer.is_valid():
                serializer.save()
        return Response({"n": 1, "Msg": "All Tasks are completed", "Status": "Success"})
    return Response({"n": 0, "Msg": "Active Tasks present", "Status": "Failed"})



@api_view(['GET'])
def get_task_coordiantor(request):
    taskObject = TaskMaster.objects.all()
    coordinatorList = []
    usertomanagerList = []
    usertomanagerobject = UserToManager.objects.filter(Active=True)
    usertomanagerserializer = MappingSerializer(usertomanagerobject,many=True)
    for k in usertomanagerserializer.data:
        usertomanagerList.append(k['ManagerID'])

    userObject = Users.objects.filter(is_active=True,id__in=usertomanagerList)
    
    if userObject is not None:
        userSer = UserSerializer(userObject,many=True)
        for i in userSer.data:            
            coordinatorList.append(i['id'])
            
        # setCoordinator = coordinatorList
        cordList = []
        for s in coordinatorList:
            employeeList = []
            employeeObject = TaskMaster.objects.filter(AssignBy = s)
            employeeTaskSer = GetTaskSerializer(employeeObject,many=True)            
            for e in employeeTaskSer.data:
                employeeList.append(e['AssignTo'])
            employeeListSet = len(set(employeeList))
            cordDict = {
                'coordiantor':s,
                'employeeCount':employeeListSet
            }
            cordList.append(cordDict)
        
        
        return Response({
            "Coordinator":cordList,
            "response": {
                "n": 1,
                "Msg": "Fetched successfully",
                "Status": "Success"
            }
        }, status=200)
    return Response({
            "data": {},
            "response": {
                "n": 0,
                "Msg": "no data found",
                "Status": "Failed"
            }
        }, status=200)

@api_view(['GET'])
def get_employeetask(request):
    assignId = request.GET.get('assignId')
    coordinatorList = []
    taskObject = TaskMaster.objects.filter(AssignBy = assignId)
    taskSerializer = GetTaskSerializer(taskObject,many=True)
    for i in taskSerializer.data:
        activeUserList = Users.objects.filter(is_active=True,id=i['AssignTo']).first()
        if activeUserList is not None:
            coordinatorList.append(i['AssignTo'])
    setCoordinator = set(coordinatorList) 
    cordList = []
    for s in setCoordinator:
        employeeObject = TaskMaster.objects.filter(AssignTo = s,AssignBy = assignId).count()
        cordDict = {
            'employee':s,
            'employeeCount':employeeObject
        }
        cordList.append(cordDict)   
    return Response({
            "employeeTask":cordList,
            "response": {
                "n": 1,
                "Msg": "Fetched successfully",
                "Status": "Success"
            }
        }, status=200)

@api_view(['GET'])
def get_employeemanager(request):
    employeeId = request.GET.get('employeeId')
    managerList = []
    taskObject = TaskMaster.objects.filter(AssignTo = employeeId)
    taskSerializer = GetTaskSerializer(taskObject,many=True)
    for ts in taskSerializer.data:
        managerList.append(ts['AssignBy'])
    empmanagerList = list(set(managerList))
    # for i in empmanagerList:
    userObject = Users.objects.filter(is_active=True,id__in=empmanagerList)
    userSer = UserSerializer(userObject,many=True)
    return Response({
            "data":userSer.data,
            "response": {
                "n": 1,
                "Msg": "Fetched successfully",
                "Status": "Success"
            }
        }, status=200)

@api_view(['POST'])
def add_notification_type(request):
    requestData ={}
    requestData['Type'] = request.POST.get('Type')
    requestData['company_code'] = request.user.company_code
    serializer = NotificationTypeSerializer(data=requestData)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Notification Type added successfully",
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

@api_view(['POST'])
def add_notification(request):
    requestData = request.POST.copy()
    requestData['company_code'] = request.user.company_code
    requestData['created_by'] = request.user.id
    serializer = TaskNotificationSerializer(data=requestData)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Notification added successfully",
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

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

from itertools import chain
from operator import attrgetter

@api_view(['GET'])
def notificationlist(request):
    
    # notlist = []
    # my_date = datetime.date.today()
    # currentdatestr = str(my_date)
    
    userId = request.user.id
    # userprofileimage = request.user.Photo
    # companycode = request.user.company_code
    # notficationobject = TaskNotification.objects.filter(UserID = userId,CreatedOn__gte=datetime.datetime.now()-timedelta(days=7)).exclude(action_Taken = False,To_manager=True,NotificationTypeId=3).order_by('-id')
    # secondnotficationobject = TaskNotification.objects.filter(UserID = userId,action_Taken = False,To_manager=True,NotificationTypeId=3).order_by('-id')
    # result_list = sorted(
    # chain(notficationobject, secondnotficationobject),
    # key=attrgetter('id'),
    # reverse=True,
    # )
    notficationobjectCount = TaskNotification.objects.filter(UserID = userId ,ReadMsg=False).count()
    # if result_list is not None:
    #     notificationser = TaskNotificationSerializer(result_list,many=True)
    #     for i in notificationser.data:
    #         notfdatetime = i['CreatedOn']
    #         notffdatetime = str(notfdatetime)
    #         notfdate = notffdatetime.split("T")[0]
    #         notftime = notffdatetime.split("T")[1]
    #         notffinaltime = notftime.split(".")[0]

    #         nndatestr = str(notfdate)
    #         nmonth_name = calendar.month_abbr[int(nndatestr.split('-')[1])]    
    #         ndatestr = nndatestr.split('-')[2]+" "+nmonth_name+" "+nndatestr.split('-')[0]
    #         i['notfctndate'] = ndatestr

    #         n_str = str(notffinaltime)
    #         n_obj = datetime.datetime.strptime( n_str, '%H:%M:%S')
            
    #         #Time format representation
    #         n_am_pm = n_obj.strftime('%I:%M:%S %p')
    #         i['notfctntime'] = n_am_pm

    #         if currentdatestr == nndatestr:
    #             mn_am_pm = n_obj.strftime('%I:%M:%S %p')
    #             i['mobilenotftime'] = str(mn_am_pm)
    #         else:
    #             nmonth_name = calendar.month_abbr[int(nndatestr.split('-')[1])]    
    #             ndatestr = nndatestr.split('-')[2]+" "+nmonth_name
    #             i['mobilenotftime'] = ndatestr


    #         if i['NotificationTypeId'] == 3 :
    #             leaveobject = Leave.objects.filter(id=i['leaveID'],Active=True).first()
    #             if leaveobject is not None:
    #                 leaveapplyser = leaveserializer(leaveobject)
    #                 leaveapprovalobject = leaveApproval.objects.filter(leave_id=i['leaveID'],managerId = str(userId) ).first()
    #                 if leaveapprovalobject:
    #                     i['leaveapprovalid'] = leaveapprovalobject.id

    #                 appdatetime = leaveapplyser.data['created_at']
    #                 strdatetime = str(appdatetime)
    #                 appdate = strdatetime.split("T")[0]
    #                 apptime = strdatetime.split("T")[1]
    #                 appfinaltime = apptime.split(".")[0]

    #                 appdatestr = str(appdate)
    #                 startmonth_name = calendar.month_abbr[int(appdatestr.split('-')[1])]    
    #                 startdatestr = appdatestr.split('-')[2]+" "+startmonth_name+" "+appdatestr.split('-')[0]
    #                 i['applieddate'] = startdatestr
                    

    #                 t_str = str(appfinaltime)
    #                 t_obj = datetime.datetime.strptime( t_str, '%H:%M:%S')
    #                 #Time format representation
    #                 t_am_pm = t_obj.strftime('%I:%M:%S %p')
    #                 i['appliedtime'] = t_am_pm


    #                 if currentdatestr == appdatestr:
    #                     mmn_am_pm = t_obj.strftime('%I:%M:%S %p')
    #                     i['mobilenotftime'] = str(mmn_am_pm)
    #                 else:
    #                     startmonth_name = calendar.month_abbr[int(appdatestr.split('-')[1])]    
    #                     startdatestr = appdatestr.split('-')[2]+" "+startmonth_name
    #                     i['mobilenotftime'] = startdatestr

    #                 leaveser = leaveserializer(leaveobject)
    #                 for o in [leaveser.data]:
    #                     startd = str(o['start_date'])
    #                     startdateday = startd.split("-")[2]
    #                     startdateyear = startd.split("-")[0]
    #                     startdatemonth = month_converter(int(startd.split("-")[1]))
    #                     newstart_date = str(startdateday) +" "+ startdatemonth +" "+str(startdateyear)

    #                     endd = str(o['end_date'])
    #                     enddateday = endd.split("-")[2]
    #                     enddateyear = endd.split("-")[0]
    #                     enddatemonth = month_converter(int(endd.split("-")[1]))
    #                     newend_date = str(enddateday) +" "+ enddatemonth +" "+str(enddateyear)

    #                 i['leavemanager'] = leaveser.data
    #                 i['newleavestartdate'] = newstart_date
    #                 i['newleaveenddate'] = newend_date
    #                 i['leave_employee'] = ""
                
    #         simplifynotmsg = strip_tags(i['NotificationMsg'])
                
    #         i['simplifynotmsg'] = simplifynotmsg
       
    trackprocheckobj = TaskMaster.objects.filter(Zone__isnull=True,AssignBy=userId).count()
    
    leaveactioncount = 0
    pendingleaveobj = leaveApproval.objects.filter(managerId=userId,approvedBy=False,rejectedBy=False)
    if pendingleaveobj is not None:
        leaveser = leaveapprovalserializer(pendingleaveobj,many=True)
        for s in leaveser.data:
            leaveobj = Leave.objects.filter(id=int(s['leave_id']),Active=True,leave_status="Pending").first()
            if leaveobj is not None:
                leaveactioncount += 1


    return Response({
        "notificationCount" :notficationobjectCount,
        "pendingleaveobj":leaveactioncount,
        "trackprocheckcount":trackprocheckobj,
        "response": {
            "n": 1,
            "msg": "Notification fetched successfully",
            "status": "success"
            }
        })
    # else:
    #     return Response({
    #         "data": "",
    #         "response": {
    #             "n": 0,
    #             "msg": "Error fetching data",
    #             "status": "Failed"
    #         }
    #     })




@api_view(['GET'])
def leavenotificationlist(request):
    userId = request.user.id
    my_date = datetime.date.today()
    currentdatestr = str(my_date)
    notficationobject = TaskNotification.objects.filter(UserID = userId,action_Taken = False,To_manager=True,NotificationTypeId=3).order_by('-id')
    if notficationobject is not None:
        notificationser = TaskNotificationSerializer(notficationobject,many=True)
        for i in notificationser.data:
            notfdatetime = i['CreatedOn']
            notffdatetime = str(notfdatetime)
            notfdate = notffdatetime.split("T")[0]
            notftime = notffdatetime.split("T")[1]
            notffinaltime = notftime.split(".")[0]

            nndatestr = str(notfdate)
            nmonth_name = calendar.month_abbr[int(nndatestr.split('-')[1])]    
            ndatestr = nndatestr.split('-')[2]+" "+nmonth_name+" "+nndatestr.split('-')[0]
            i['notfctndate'] = ndatestr

            n_str = str(notffinaltime)
            n_obj = datetime.datetime.strptime( n_str, '%H:%M:%S')
            
            #Time format representation
            n_am_pm = n_obj.strftime('%I:%M:%S %p')
            i['notfctntime'] = n_am_pm

            if currentdatestr == nndatestr:
                mn_am_pm = n_obj.strftime('%I:%M:%S %p')
                i['mobilenotftime'] = str(mn_am_pm)
            else:
                nmonth_name = calendar.month_abbr[int(nndatestr.split('-')[1])]    
                ndatestr = nndatestr.split('-')[2]+" "+nmonth_name
                i['mobilenotftime'] = ndatestr


            if i['NotificationTypeId'] == 3 :
                leaveobject = Leave.objects.filter(id=i['leaveID'],Active=True).first()
                if leaveobject is not None:
                    leaveapplyser = leaveserializer(leaveobject)
                    leaveapprovalobject = leaveApproval.objects.filter(leave_id=i['leaveID'],managerId = str(userId) ).first()
                    if leaveapprovalobject:
                        i['leaveapprovalid'] = leaveapprovalobject.id

                    appdatetime = leaveapplyser.data['created_at']
                    strdatetime = str(appdatetime)
                    appdate = strdatetime.split("T")[0]
                    apptime = strdatetime.split("T")[1]
                    appfinaltime = apptime.split(".")[0]

                    appdatestr = str(appdate)
                    startmonth_name = calendar.month_abbr[int(appdatestr.split('-')[1])]    
                    startdatestr = appdatestr.split('-')[2]+" "+startmonth_name+" "+appdatestr.split('-')[0]
                    i['applieddate'] = startdatestr
                    

                    t_str = str(appfinaltime)
                    t_obj = datetime.datetime.strptime( t_str, '%H:%M:%S')
                    #Time format representation
                    t_am_pm = t_obj.strftime('%I:%M:%S %p')
                    i['appliedtime'] = t_am_pm


                    if currentdatestr == appdatestr:
                        mmn_am_pm = t_obj.strftime('%I:%M:%S %p')
                        i['mobilenotftime'] = str(mmn_am_pm)
                    else:
                        startmonth_name = calendar.month_abbr[int(appdatestr.split('-')[1])]    
                        startdatestr = appdatestr.split('-')[2]+" "+startmonth_name
                        i['mobilenotftime'] = startdatestr

                    leaveser = leaveserializer(leaveobject)
                    for o in [leaveser.data]:
                        startd = str(o['start_date'])
                        startdateday = startd.split("-")[2]
                        startdateyear = startd.split("-")[0]
                        startdatemonth = month_converter(int(startd.split("-")[1]))
                        newstart_date = str(startdateday) +" "+ startdatemonth +" "+str(startdateyear)

                        endd = str(o['end_date'])
                        enddateday = endd.split("-")[2]
                        enddateyear = endd.split("-")[0]
                        enddatemonth = month_converter(int(endd.split("-")[1]))
                        newend_date = str(enddateday) +" "+ enddatemonth +" "+str(enddateyear)

                    i['leavemanager'] = leaveser.data
                    i['newleavestartdate'] = newstart_date
                    i['newleaveenddate'] = newend_date
                    i['leave_employee'] = ""
                
            simplifynotmsg = strip_tags(i['NotificationMsg'])
                
            i['simplifynotmsg'] = simplifynotmsg
        return Response({
            "data": notificationser.data,
            "response": {
                "n": 1,
                "msg": "Notification have been read by user",
                "status": "Success"
            }
        })

    else:
        return Response({
            "data": "",
            "response": {
                "n": 0,
                "msg": "Error fetching data",
                "status": "Failed"
            }
        })
def is_within_15_minutes(timestamp_str):
    # Convert the timestamp string to a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)

    # Get the current time
    current_time = datetime.datetime.now(timezone.utc)

    # Calculate the difference between the two timestamps
    time_difference = current_time - timestamp

    # Check if the difference is within 15 minutes
    return abs(time_difference) <= timedelta(minutes=15)



@api_view(['GET'])
def readnotifications(request):
    userId = request.user.id
    notficationobject = TaskNotification.objects.filter(UserID = userId,ReadMsg=False)
    if notficationobject is not None:
        serializer = TaskNotificationSerializer(notficationobject,many=True)
        for s in serializer.data:
            TaskNotification.objects.filter(UserID = userId,ReadMsg=False).update(
                                ReadMsg = True
            )
        
    my_date = datetime.date.today()
    currentdatestr = str(my_date)
    
    userId = request.user.id
    notficationobject = TaskNotification.objects.filter(UserID = userId,CreatedOn__gte=datetime.datetime.now()-timedelta(days=7)).exclude(action_Taken = False,To_manager=True,NotificationTypeId=3).order_by('-id')
    secondnotficationobject = TaskNotification.objects.filter(UserID = userId,action_Taken = False,To_manager=True,NotificationTypeId=3).order_by('-id')
    result_list = sorted(
    chain(notficationobject, secondnotficationobject),
    key=attrgetter('id'),
    reverse=True,
    )
    
    if result_list is not None:
        notificationser = TaskNotificationSerializer(result_list,many=True)
        for i in notificationser.data:
            notfdatetime = i['CreatedOn']
            notffdatetime = str(notfdatetime)
            notfdate = notffdatetime.split("T")[0]
            notftime = notffdatetime.split("T")[1]
            notffinaltime = notftime.split(".")[0]

            nndatestr = str(notfdate)
            nmonth_name = calendar.month_abbr[int(nndatestr.split('-')[1])]    
            ndatestr = nndatestr.split('-')[2]+" "+nmonth_name+" "+nndatestr.split('-')[0]
            i['notfctndate'] = ndatestr

            n_str = str(notffinaltime)
            n_obj = datetime.datetime.strptime( n_str, '%H:%M:%S')
            #Time format representation
            n_am_pm = n_obj.strftime('%I:%M:%S %p')
            i['notfctntime'] = n_am_pm

            if currentdatestr == nndatestr:
                mn_am_pm = n_obj.strftime('%I:%M:%S %p')
                i['mobilenotftime'] = str(mn_am_pm)
            else:
                nmonth_name = calendar.month_abbr[int(nndatestr.split('-')[1])]    
                ndatestr = nndatestr.split('-')[2]+" "+nmonth_name
                i['mobilenotftime'] = ndatestr

            if i['NotificationTypeId'] == 7 :
                result = is_within_15_minutes(i['CreatedOn'])
                if result:
                    print(f"{i['CreatedOn']} is within 15 minutes from the current time.")
                else:
                    i['action_Taken']=True
                    print(f"{i['CreatedOn']} is NOT within 15 minutes from the current time.")

                                
                
                
            if i['NotificationTypeId'] == 3 :
                leaveobject = Leave.objects.filter(id=i['leaveID'],Active=True).first()
                if leaveobject is not None:
                    leaveapplyser = leaveserializer(leaveobject)
                    leaveapprovalobject = leaveApproval.objects.filter(leave_id=i['leaveID'],managerId = str(userId) ).first()
                    if leaveapprovalobject:
                        i['leaveapprovalid'] = leaveapprovalobject.id
                    else:
                        i['leaveapprovalid'] = ''
                        
                    appdatetime = leaveapplyser.data['created_at']
                    strdatetime = str(appdatetime)
                    appdate = strdatetime.split("T")[0]
                    apptime = strdatetime.split("T")[1]
                    appfinaltime = apptime.split(".")[0]

                    appdatestr = str(appdate)
                    startmonth_name = calendar.month_abbr[int(appdatestr.split('-')[1])]    
                    startdatestr = appdatestr.split('-')[2]+" "+startmonth_name+" "+appdatestr.split('-')[0]
                    i['applieddate'] = startdatestr
                    

                    t_str = str(appfinaltime)
                    t_obj = datetime.datetime.strptime( t_str, '%H:%M:%S')
                    #Time format representation
                    t_am_pm = t_obj.strftime('%I:%M:%S %p')
                    i['appliedtime'] = t_am_pm


                    if currentdatestr == appdatestr:
                        mmn_am_pm = t_obj.strftime('%I:%M:%S %p')
                        i['mobilenotftime'] = str(mmn_am_pm)
                    else:
                        startmonth_name = calendar.month_abbr[int(appdatestr.split('-')[1])]    
                        startdatestr = appdatestr.split('-')[2]+" "+startmonth_name
                        i['mobilenotftime'] = startdatestr

                    leaveser = leaveserializer(leaveobject)
                    for o in [leaveser.data]:
                        startd = str(o['start_date'])
                        startdateday = startd.split("-")[2]
                        startdateyear = startd.split("-")[0]
                        startdatemonth = month_converter(int(startd.split("-")[1]))
                        newstart_date = str(startdateday) +" "+ startdatemonth +" "+str(startdateyear)

                        endd = str(o['end_date'])
                        enddateday = endd.split("-")[2]
                        enddateyear = endd.split("-")[0]
                        enddatemonth = month_converter(int(endd.split("-")[1]))
                        newend_date = str(enddateday) +" "+ enddatemonth +" "+str(enddateyear)

                    i['leavemanager'] = leaveser.data
                    i['newleavestartdate'] = newstart_date
                    i['newleaveenddate'] = newend_date
                    i['leave_employee'] = ""
                
            simplifynotmsg = strip_tags(i['NotificationMsg'])
                
            i['simplifynotmsg'] = simplifynotmsg
        return Response({
            "data": notificationser.data,
            "response": {
                "n": 1,
                "msg": "Notification have been read by user",
                "status": "Success"
            }
        })

    else:
        return Response({
            "data": "",
            "response": {
                "n": 0,
                "msg": "Error fetching data",
                "status": "Failed"
            }
        })



@api_view(['GET'])
def gettaskbyid(request,id):
    task = TaskMaster.objects.filter(id=id).first()
    if not task:
        return Response({
            "data": "",
            "response": {
                "n": 0,
                "msg": "Task Not Found",
                "status": "Failed"
            }
        })
    else:
        serializer = GetTaskSerializer(task)
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Task Information Found Successfully",
                "status": "Success"
            }
        })

@api_view(['GET'])
def checktaskbymanager(request):
        idd = request.GET.get('ID')
        empid =  int(idd)

        taskplay = TaskMaster.objects.filter(AssignTo=empid,Status=1,Active=True).first()
        if taskplay is not None:
            taskser = GetTaskSerializer(taskplay)
            return Response({
            "data": taskser.data,
            "response": {
                "n": 1,
                "status": "Failure"
              }
            })
        else:
            return Response({
            "data": "",
            "response": {
                "n": 0,
                "status": "Sucsess"
              }
            })
            

            
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']  # Example scope

check_path = os.path.join(BASE_DIR, "trackpro-ort-firebase-adminsdk-h3bqu-34f03d56eb.json")

json_path = check_path
cred = credentials.Certificate(json_path)

default_app = firebase_admin.initialize_app(cred, {
    'projectId': 'trackpro-ort'
})
        
def fb_get_access_token():
  """
  Retrieve a valid access token that can be used to authorize requests
  :return: Access token.
  """
  credentials = service_account.Credentials.from_service_account_file(
    json_path, scopes=SCOPES)
  request = google.auth.transport.requests.Request()
  credentials.refresh(request)
  return credentials.token

def sendfirebasenotification(fcmtoken,firebasemsg,notftype,fcmleaveid,fcmtomanager):
    result =[]
    headers = {
        'Authorization': 'Bearer ' + fb_get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }


    data = {

        "message":{
            "token":fcmtoken,
            "notification":{
                "body":firebasemsg,
                "title":'trackpro'
            },
        
        "data": {
            'notftype':notftype,
            'LeaveId':fcmleaveid,
            'ToManager':fcmtomanager
        }
    }
        
        
        
        
    
    }

   



    response = requests.post("https://fcm.googleapis.com/v1/projects/trackpro-ort/messages:send",headers = headers, data=json.dumps(data))
    if response.status_code == 200:
        result.append(response.json())
        result.append(response.status_code)
        print(result)
        return result
    return []

def senddesktopnotf(desktoptoken,firebasemsg): 
    result =[]
    

    
    if desktoptoken is not None and desktoptoken !='' and desktoptoken != 'None':
        
        headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'key=' + Desktop_key
                    }

        body = {
                'notification': {
            
                            'title': 'trackpro',

                            'body':  firebasemsg,

                        
                        },

                'to':desktoptoken,

                'priority': 'high',

                }

    

        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
        result.append(response.json())
        result.append(response.status_code)
    else:
        result.append('desktop token not found')
        result.append(201)
        
    return result

def send_desktop_notfication_to_all(desktoptokens,firebasemsg): 
    result =[]
    

    
    if desktoptokens is not None and desktoptokens !=[] :
        
        headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'key=' + Desktop_key
                    }

        body = {
                'notification': {
            
                            'title': 'trackpro',

                            'body':  firebasemsg,

                        
                        },

                'registration_ids':desktoptokens,

                'priority': 'high',

                }

    

        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
        result.append(response.json())
        result.append(response.status_code)
    else:
        result.append('desktop token not found')
        result.append(201)
        
    
    
    return result

@api_view(['POST'])
def addNewTaskbyManager(request, format=None):
    if  request.method == 'POST':
        requestData = request.data.copy()
        AssignBymanager = int(requestData['AssignBy'])
        requestData['CreatedBy'] = AssignBymanager
        currenttime =  timezone.localtime(timezone.now())
        companycode = request.user.company_code
        project = ProjectMaster.objects.get(id=request.data['Project'])
        requestData = request.data.copy()
        requestData['company_code'] = request.user.company_code
        serializer = PostTaskMasterSerializer(data=requestData)
        if serializer.is_valid():
            serializer.validated_data['Active'] = False
            serializer.validated_data['ProjectName'] = project.ProjectName
            s = serializer.validated_data['AssignBy']
            serializer.validated_data['Status_id'] = 2
            serializer.validated_data['AddedByManager'] = True
            user = Users.objects.filter(id=s.id)
            for u in user:
                serializer.validated_data['AssignByStr'] = u.Firstname + \
                    ' ' + u.Lastname
            serializer.save()

            useremp = Users.objects.filter(id=requestData['AssignTo']).first()
            useremail = useremp.email
            username = useremp.Firstname + " " + useremp.Lastname

            usermanager = Users.objects.filter(id=int(AssignBymanager)).first()
            managername = usermanager.Firstname + " " + usermanager.Lastname


            taskid= serializer.data['id']
            ProjectTasks.objects.create(Task_id=taskid,StartDate=currenttime,EndDate=currenttime,company_code=companycode)
            TaskNotification.objects.create(
                NotificationTitle = "Task Assignment",
                NotificationMsg = "New Task is Assigned by " + "<span class='taskmanagername'>"+str(managername) +"</span>",
                UserID_id = requestData['AssignTo'],
                NotificationTypeId_id = 1 ,
                leaveID = 0,
                created_by = request.user.id,
                company_code = request.user.company_code,
            )

            firebasemsg =  "New Task is Assigned by " + str(managername)
            fcmtoken = useremp.FirebaseID
            notftype = "Task"
            fcmleaveid = 0
            fcmtomanager = False
            
            desktoptoken = useremp.desktopToken 
            # desktopnotf = senddesktopnotf(desktoptoken,firebasemsg)
            
            if fcmtoken is not None and fcmtoken != "":
                firebasenotification = ""
                # firebasenotification = sendfirebasenotification(fcmtoken,firebasemsg,notftype,fcmleaveid,fcmtomanager)
            else:
                firebasenotification = ""
            
            
            subject = "Reminder"
            data2 = {"subject": subject,
                     "email":useremail,
                     'Message':str(managername),
                     'projectdetails':project.ProjectName,
                     'Taskdetails':requestData['TaskTitle'],
                     'empname':username,
                    "template": 'mails/Taskassignmentmail.html'}
            message = render_to_string(
                data2['template'], data2)
            send_mail(data2, message)

            return Response({"n": 1, "Msg": "Task Assigned Successfully", "Status": "Success",'data':serializer.data,'firebase':firebasenotification}, status=status.HTTP_201_CREATED)
        return Response({"n": 0, "Msg": "Error adding task", "Status": "Failed",'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Zonestatusbymanagerapi(request):
    data={}
    newdata={}
    data['Zone'] = request.data.get('Zonestatus', None)
    zone=int(data['Zone'])
    data['id'] = request.data.get('taskid', None)
    data['CheckedBy'] = request.user.id

    if zone == 1:
        zonestr = "Green Zone Assigned Successfully."
    elif zone == 2:
        zonestr = "Yellow Zone Assigned Successfully."
    elif zone == 3:
        zonestr = "Red Zone Assigned Successfully."
    elif zone == 4:
        zonestr = "Not Done Zone Assigned Successfully."
    elif zone == 5:
        zonestr = "Task Cancelled Successfully."
    elif zone == 6:
        zonestr = "Task Rejected Successfully."

    taskexist = TaskMaster.objects.filter(id=data['id']).first()
    if taskexist:
        if zone == 3 or zone == 4 or zone == 5 or zone == 6:
            newdata['Bonus']=False
            newdata['Zone']=zone
            newdata['CheckedBy'] = request.user.id

            taskser = GetTaskSerializer(taskexist,data=newdata,partial=True)
            if taskser.is_valid():
                taskser.save()
                return Response({"n": 1, "Msg": zonestr , "Status": "Success",'data':taskser.data}, status=status.HTTP_201_CREATED)
        else:
            taskser = GetTaskSerializer(taskexist,data=data,partial=True)
            if taskser.is_valid():
                taskser.save()
                return Response({"n": 1, "Msg": zonestr, "Status": "Success",'data':taskser.data}, status=status.HTTP_201_CREATED)
                
    else:
        return Response({"n": 0, "Msg": "Task Not Found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def taskbonusbymanagerapi(request):
    data={}
    newdata={}
    data['Bonus'] = request.data.get('Bonus', None)
    bonus = data['Bonus'] 
    id = request.data.get('taskid', None)

    taskexist = TaskMaster.objects.filter(id=id).first()
    if taskexist:
        greenyellowzone = TaskMaster.objects.filter(id=id,Zone__in=[1,2]).first()
        nozone =  TaskMaster.objects.filter(id=id,Zone__isnull= True).first()
        if greenyellowzone is not None:
            taskser = GetTaskSerializer(taskexist,data=data,partial=True)
            if taskser.is_valid():
                taskser.save()
                return Response({"n": 1, "Msg": "Bonus added successfully", "Status": "Success",'data':taskser.data}, status=status.HTTP_201_CREATED)
        elif nozone is not None:
            newdata['Zone']=1
            newdata['Bonus']=bonus
            taskser = GetTaskSerializer(taskexist,data=newdata,partial=True)
            if taskser.is_valid():
                taskser.save()
                return Response({"n": 1, "Msg": "Bonus added successfully", "Status": "Success",'data':taskser.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"n": 0, "Msg": "Task needs to be in green or yellow zone", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"n": 0, "Msg": "Task Not Found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def employeetaskinfo(request):
    employeeid = request.POST.get("employeeid")
    managerid = request.POST.get("managerid")

    if employeeid is not None:
        if managerid is not None and managerid != "" and managerid != "All":
            taskobj = TaskMaster.objects.filter(AssignTo=employeeid,AssignBy=managerid,Zone__isnull=True).order_by('id').first()
        else:
            taskobj = TaskMaster.objects.filter(AssignTo=employeeid,Zone__isnull=True).order_by('id').first()

        if taskobj is not None:
            week = taskobj.Week
            year = taskobj.Year
            context={
                'week':week,
                'year':year,
            }
            return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success",'data':context}, status=status.HTTP_201_CREATED)
        else:
            my_date = datetime.date.today()
            year, week_num, day_of_week = my_date.isocalendar()
            currweek = week_num
            curryear  = year
            context={
                'week':currweek,
                'year':curryear,
            }
            return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success",'data':context}, status=status.HTTP_201_CREATED)
    else:
        return Response({"n": 0, "Msg": "employeeid not found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Managertaskinfomapi(request):
    managerid = request.POST.get("managerid")
    if managerid is not None:
        if managerid is not None and managerid != "" and managerid != "all":
            taskobj = TaskMaster.objects.filter(AssignBy=managerid,Zone__isnull=True).order_by('id').first()
            if taskobj is not None:
                week = taskobj.Week
                year = taskobj.Year
                context={
                    'week':week,
                    'year':year,
                }
                return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success",'data':context}, status=status.HTTP_201_CREATED)
            else:
                my_date = datetime.date.today()
                year, week_num, day_of_week = my_date.isocalendar()
                currweek = week_num
                curryear  = year
                context={
                    'week':currweek,
                    'year':curryear,
                }
                return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success",'data':context}, status=status.HTTP_201_CREATED)
        else:
            taskobj = TaskMaster.objects.filter(Zone__isnull=True).order_by('id').first()
            if taskobj is not None:
                week = taskobj.Week
                year = taskobj.Year
                context={
                    'week':week,
                    'year':year,
                }
                return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success",'data':context}, status=status.HTTP_201_CREATED)
            else:
                my_date = datetime.date.today()
                year, week_num, day_of_week = my_date.isocalendar()
                currweek = week_num
                curryear  = year
                context={
                    'week':currweek,
                    'year':curryear,
                }
                return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success",'data':context}, status=status.HTTP_201_CREATED)

    else:
        return Response({"n": 0, "Msg": "employeeid not found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Allemp_finalsubmit(request):
    users = request.user.id
    company_code =  request.user.company_code
    manid = request.POST.get("Managerid")
    if manid != "all":
        managerid = int(request.POST.get("Managerid") )
    else:
        managerid = request.POST.get("Managerid")
    year = int( request.POST.get("Year"))
    week = int( request.POST.get("Week"))

    taskpointsper = 0
    greencountmultiple = 0
    yellowcountmultiple = 0
    redcountmultiple = 0
    notdonecountmultiple = 0
    rejectcountmultiple = 0
    bonuscountmultiple = 0

    trackprorules = rulestrackpro.objects.filter(is_active=True,company_code=request.user.company_code)
    if trackprorules is not None:
        trackproser = trackproruleserializer(trackprorules,many=True)
        for w in trackproser.data:
            if w['color'] == "green":
                taskpointsper = int(w['points']) 
            if w['color'] == "green":
                greencountmultiple = int(w['points'])
            if w['color'] == "yellow":
                yellowcountmultiple = int(w['points'])
            if w['color'] == "red":
                redcountmultiple = int(w['points'])
            if w['color'] == "notdone":
                notdonecountmultiple = int(w['points'])
            if w['color'] == "reject":
                rejectcountmultiple = int(w['points'])
            if w['color'] == "bonus":
                bonuscountmultiple = int(w['points'])
    
    if manid != "all":
        emptask = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week).distinct('AssignTo_id')
        if emptask.exists():
            taskser = GetTaskSerializer(emptask,many=True)
            for p in taskser.data:
                GreenZoneTask = 0
                YellowZoneTask = 0
                RedZoneTask = 0
                NotdoneZoneTask = 0
                bonus = 0
                cancelledZoneTask=0
                rejectedZoneTask=0
                extracredits=0
            
                empexist = IntermediateTrackProResult.objects.filter(Employee=p['AssignTo'],Year=year,Week=week).first()
                if empexist is None:
                    alltaskobjs = TaskMaster.objects.filter(AssignTo_id=p['AssignTo'],Year=year,Week=week).count()

                    checkedobjs  = TaskMaster.objects.filter(AssignTo_id=p['AssignTo'],Year=year,Week=week,Zone__isnull = False).count()

                    if alltaskobjs == checkedobjs:
                        scoreObject=TaskMaster.objects.filter(Week=week,Year=year,AssignTo=p['AssignTo'])
                        if scoreObject is not None:
                            Ser = GetTaskScoreSerializer(scoreObject,many=True)
                            for i in Ser.data:
                                if i['Zone'] == 1:
                                    i['green'] = greencountmultiple
                                    GreenZoneTask += i['green']
                                elif i['Zone'] == 2:
                                    i['yellow'] = yellowcountmultiple
                                    YellowZoneTask += i['yellow']
                                elif i['Zone'] == 3:
                                    i['red'] = redcountmultiple
                                    RedZoneTask += i['red']
                                elif i['Zone'] == 4:
                                    i['notdone'] = notdonecountmultiple
                                    NotdoneZoneTask += i['notdone']
                                elif i['Zone'] == 5:
                                    i['cancelled'] = 1
                                    cancelledZoneTask += i['cancelled']
                                elif i['Zone'] == 6:
                                    i['rejected'] = rejectcountmultiple
                                    rejectedZoneTask += i['rejected']
                                if i['Bonus'] == True:
                                    i['isBonus'] = bonuscountmultiple
                                    bonus += i['isBonus']
                          
                            greenzonecreditpoints = int(GreenZoneTask/greencountmultiple)
                            ZoneNoneList = ""  
                            if greenzonecreditpoints >= 10 and greenzonecreditpoints <= 14:
                                extracredits =  int(3*greencountmultiple)
                            elif greenzonecreditpoints >= 15 and greenzonecreditpoints <= 19:
                                extracredits =  int(7*greencountmultiple)
                            elif greenzonecreditpoints >= 20 and greenzonecreditpoints <= 24:
                                extracredits =  int(12*greencountmultiple)
                            elif greenzonecreditpoints >= 25 and greenzonecreditpoints <= 29:
                                extracredits =  int(18*greencountmultiple)

                            totalTrackProScore = (GreenZoneTask + YellowZoneTask + RedZoneTask  + bonus+ extracredits) - (NotdoneZoneTask + rejectedZoneTask)
                            totalScore = (alltaskobjs-cancelledZoneTask) * greencountmultiple 
                            trackpropercentcal = (100 * (((GreenZoneTask + YellowZoneTask + RedZoneTask + bonus + extracredits) - (NotdoneZoneTask + rejectedZoneTask)) / totalScore))
                            trackpropercent = round(trackpropercentcal, 2)

                            Green = GreenZoneTask
                            Yellow = YellowZoneTask
                            Red= RedZoneTask
                            NotDone = NotdoneZoneTask
                            Cancelled = cancelledZoneTask
                            Rejected = rejectedZoneTask
                            Bonus = bonus
                            extra_credit=extracredits
                            TotalScore = totalScore
                            TrackProScore = totalTrackProScore
                            TrackProPercent = trackpropercent
                            TotalTask = alltaskobjs
                            CreatedBy = users

                            IntermediateTrackProResult.objects.create(Employee_id=p['AssignTo'],Year=year,Week=week,EmpID_id=p['AssignTo'],Green = Green, Yellow = Yellow,Red= Red,NotDone = NotDone,company_code=company_code,
                            Cancelled = Cancelled,Rejected = Rejected,Bonus = Bonus, extra_credit= extra_credit,TotalScore=TotalScore,TrackProScore=TrackProScore,TrackProPercent=TrackProPercent,TotalTask=TotalTask,CreatedBy_id=CreatedBy)


            return Response({"n": 1, "Msg": "final submit successful", "Status": "Success",'data':''}, status=status.HTTP_201_CREATED)
        else:
            return Response({"n": 0, "Msg": "Task not found", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"n": 0, "Msg": "Please select manager !", "Status": "Failed",'data':''}, status=status.HTTP_400_BAD_REQUEST)














@api_view(['POST'])
def employeereviewinfo(request):
    manid = request.POST.get("Managerid")
    if manid != "all":
        managerid = int(request.POST.get("Managerid") )
    else:
        managerid = request.POST.get("Managerid")

  
    year = int( request.POST.get("Year"))
    week = int( request.POST.get("Week"))
    my_date = datetime.date.today()
    curryear, week_num, day_of_week = my_date.isocalendar()
    currweek = week_num

    if managerid == "all":
        emptask = TaskMaster.objects.filter(Year=year,Week=week).distinct('AssignTo_id')
        Totalemployee = TaskMaster.objects.filter(Year=year,Week=week).distinct('AssignTo_id').count()
        uncheckedTaskcount = TaskMaster.objects.filter(Year=year,Week=week,Zone__isnull=True).count()
    else:    
        emptask = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week).distinct('AssignTo_id')
        Totalemployee = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week).distinct('AssignTo_id').count()
        uncheckedTaskcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone__isnull=True).count()

    if emptask.exists():
        empcounter=0
        finalsubmitcheck = GetTaskSerializer(emptask,many=True)
        for p in finalsubmitcheck.data:
            empexist = IntermediateTrackProResult.objects.filter(Employee=p['AssignTo'],Year=year,Week=week).first()
            if empexist is not None:
                empcounter += 0
            else:
                empcounter += 1
        
        emptaskser = GetTaskSerializer(emptask,many=True)
        for i in emptaskser.data:
            userobj = Users.objects.filter(id=i['AssignTo']).first()
            i['UserID']=userobj.id
            i['UserIDStr'] = userobj.Firstname + " " +  userobj.Lastname

            if managerid != "all":
                i['uncheckedcount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],AssignBy_id=managerid,Year=year,Week=week,Zone__isnull = True).count()
                i['checkedcount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],AssignBy_id=managerid,Year=year,Week=week,Zone__isnull = False).count()
                i['totalmanagercount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],AssignBy_id=managerid,Year=year,Week=week).count()
            else:
                i['uncheckedcount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],Year=year,Week=week,Zone__isnull = True).count()
                i['checkedcount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],Year=year,Week=week,Zone__isnull = False).count()
                i['totalmanagercount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],Year=year,Week=week).count()
            i['totaltaskcount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],Year=year,Week=week).count()
          
            i['totalCheckedcount'] = TaskMaster.objects.filter(AssignTo_id=i['UserID'],Year=year,Week=week,Zone__isnull = False).count()

            checkfinalsubmit = IntermediateTrackProResult.objects.filter(EmpID_id=i['UserID'],Year=year,Week=week).first()
            if checkfinalsubmit is not None:
                i['fsubstr'] = "<button type='button' class='submittedbtn'>Submitted</button>"
               

            else:
                i['fsubstr'] = "<button type='button' onclick='finalsaveTrackProScore("+str(i['UserID'])+")'  id='#finalsubmitbtn"+str(i['UserID'])+"' class='finalsbmtbtn'>Final Submit</button>"
                
            if int(i['uncheckedcount']) > 0:
                i['sortordersubmit'] = 1
            elif i['totalCheckedcount'] == i['totaltaskcount'] and checkfinalsubmit is None:
                i['sortordersubmit'] = 2
            elif checkfinalsubmit is None and int(i['uncheckedcount']) == 0:
                i['sortordersubmit'] = 3
            
            else:
                i['sortordersubmit'] = 4

        
         

            
        countslist=[]
        if managerid != "all":
            Totalcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week).count()
            
            Checkedcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone__isnull = False).count()
            
            if Totalcount > 0:
                perc = round((Checkedcount/Totalcount)*100)
                percentage = perc
            else:
                percentage = 0
            
            Greencount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone_id=1).count()
            yellowcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone_id=2).count()
            redcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone_id=3).count()
            notdonecount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone_id=4).count()
            cancelcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone_id=5).count()
            rejectcount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone_id=6).count()
            bonuscount = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Bonus=True).count()
        else:
            Totalcount = TaskMaster.objects.filter(Year=year,Week=week).count()
            
            Checkedcount = TaskMaster.objects.filter(Year=year,Week=week,Zone__isnull = False).count()
            
            if Totalcount > 0:
                perc = round((Checkedcount/Totalcount)*100)
                percentage = perc
            else:
                percentage = 0
            
            Greencount = TaskMaster.objects.filter(Year=year,Week=week,Zone_id=1).count()
            yellowcount = TaskMaster.objects.filter(Year=year,Week=week,Zone_id=2).count()
            redcount = TaskMaster.objects.filter(Year=year,Week=week,Zone_id=3).count()
            notdonecount = TaskMaster.objects.filter(Year=year,Week=week,Zone_id=4).count()
            cancelcount = TaskMaster.objects.filter(Year=year,Week=week,Zone_id=5).count()
            rejectcount = TaskMaster.objects.filter(Year=year,Week=week,Zone_id=6).count()
            bonuscount = TaskMaster.objects.filter(Year=year,Week=week,Bonus=True).count()

            
        countslist.append(Greencount)
        countslist.append(yellowcount)
        countslist.append(redcount)
        countslist.append(notdonecount)
        countslist.append(cancelcount)
        countslist.append(rejectcount)
      

        sortlist = emptaskser.data
        newlist = sorted(sortlist, key=itemgetter('sortordersubmit')) 

        my_date = datetime.date.today()
        curryear, week_num, day_of_week = my_date.isocalendar()
        currentweek = week_num
        currentyear = curryear


        context={
            'serdata':newlist,
            'Countslist':countslist,
            'totaltaskcount':Totalcount,
            'totalchecked':Checkedcount,
            'totalperc':percentage,
            'currweek':currweek,
            'bonuscount':bonuscount,
            'empcounter':empcounter,
            'finalsubmit':empcounter,
            'Totaluncheckedtask':uncheckedTaskcount,
            'Currentweek':currentweek,
            'Currentyear':currentyear,
            'TotalEmployees':Totalemployee,
        }
            
        return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success","data":context}, status=status.HTTP_201_CREATED)
    else:
        my_date = datetime.date.today()
        curryear, week_num, day_of_week = my_date.isocalendar()
        currentweek = week_num
        currentyear = curryear

        context={
            'Currentweek':currentweek,
            'Currentyear':currentyear,
        }

        return Response({"n": 0, "Msg": "Tasks not found ", "Status": "failure",'data':context}, status=status.HTTP_201_CREATED)
    





















@api_view(['POST'])
def employeetasklistreviewinfo(request):
    manid = request.POST.get("Managerid")
    if manid != "all":
        managerid = int(request.POST.get("Managerid") )
    else:
        managerid = request.POST.get("Managerid")

  
    year = int( request.POST.get("Year"))
    week = int( request.POST.get("Week"))
    my_date = datetime.date.today()
    curryear, week_num, day_of_week = my_date.isocalendar()
    currweek = week_num

    if managerid == "all":
        emptask = TaskMaster.objects.filter(Year=year,Week=week,Zone__isnull=True).distinct('AssignTo_id')
    else:    
        emptask = TaskMaster.objects.filter(AssignBy_id=managerid,Year=year,Week=week,Zone__isnull=True)
       

    if emptask.exists():

        emptaskser = GetTaskSerializer(emptask,many=True)
        for i in emptaskser.data:
            userobj = Users.objects.filter(id=i['AssignTo']).first()
            i['UserID']=userobj.id
            i['UserIDStr'] = userobj.Firstname + " " +  userobj.Lastname

            if i['Status'] == 3:
                i['task_status'] = "<img data-bs-toggle='tooltip' data-bs-placement='bottom' title='Completed' src='/static/Media/taskicons/checktrackprocompleted.svg' class='task_status_icon' alt='notdone'>"
            else:
                i['task_status'] = "<img data-bs-toggle='tooltip' data-bs-placement='bottom' title='Inprocess' src='/static/Media/taskicons/checktrackprorunning.svg' class='task_status_icon' alt='notdone'>"
            
            taskremark = TaskRemark.objects.filter(task_id = i['id'], IsRead = False).first()
            if taskremark is not None:
                i['taskremark'] = False
            else:
                i['taskremark'] = True
                
            strdate = str(i['AssignDate'])
            startmonth_name = calendar.month_abbr[int(strdate.split('-')[1])]  
            newdate = strdate.split('-')[2] +" "+startmonth_name +" "+strdate.split('-')[0]
            i['AssignDate']=newdate

            currentzone = pytz.timezone("Asia/Kolkata") 
            currenttime = datetime.datetime.now(currentzone) 
           
            newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

            taskobj = TaskMaster.objects.filter(id=i['id']).first()
            taskidlist = []
            if taskobj.ParentTaskId is not None:
                parenttaskid  = taskobj.ParentTaskId
                taskidlist.append(parenttaskid)

                taskobject = TaskMaster.objects.filter(ParentTaskId=parenttaskid)
                taskser = PostTaskMasterSerializer(taskobject,many=True)
                for t in taskser.data:
                    taskidlist.append(t['id'])
            else:
                taskidlist.append(i['id'])
                taskobject = TaskMaster.objects.filter(ParentTaskId=i['id'])
                taskser = PostTaskMasterSerializer(taskobject,many=True)
                for t in taskser.data:
                    taskidlist.append(t['id'])

            
            projecttasktime = ProjectTasks.objects.filter(Task__in=taskidlist).order_by("id")
            if projecttasktime :
                projectser = ProjectTasksSerializer(projecttasktime,many=True)
                FMT = '%H:%M:%S.%f'
                totaltime=0
                for o in projectser.data:
                    startstring = o['StartDate']
                    starttime=startstring
                    t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                    endstring = o['EndDate']
                    if endstring is not None:
                        endtime = o['EndDate']
                    else:
                        endtime = str(newcurrenttime)
                    t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                    tdelta=t2-t1
                  
                   
                    if "day" in str(tdelta) or "days" in str(tdelta):
                        daystring = str(tdelta).split(",")[0]
                        noofdays = str(daystring).split(" ")[0]
                        daysmins = int(noofdays)*1440

                        thoursstr =  str(tdelta).split(",")[1]
                        thours = str(thoursstr).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(thoursstr).split(":")[1]
                        finalmins = int(hrs)+int(tmins)+int(daysmins)
                    else:
                        thours = str(tdelta).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(tdelta).split(":")[1]
                        finalmins = int(hrs)+int(tmins)
                    totaltime += finalmins

                totalhours =totaltime
                hour = int (totalhours) // 60
                if (len(str(hour)) < 2):
                    hours = "0"+str(hour)
                else:
                    hours = str(hour)

                mins = int (totalhours) % 60
                if (len(str(mins)) < 2):
                    minutes = "0"+str(mins)
                else:
                    minutes = str(mins)

                hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                i['taskhours'] = hourstring

                #  calculate day wise time strings

                protimelist = []
                seconddaylist = []
                finallist=[]
            
                for s in projectser.data:

                    FMT = '%H:%M:%S.%f'
                   
                    startstring = s['StartDate']
                    enddatestr = s['EndDate']

                    a = startstring.split('T')[0]
                    revdate = a.split('-')[2]+"-"+ a.split('-')[1]+"-"+ a.split('-')[0]
                    startdatestring = revdate

                    if enddatestr is not None:
                        b = enddatestr.split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate
                    else:
                        b = str(newcurrenttime).split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate

                    # if task played and closed on same date
                    if startdatestring == enddatestring:

                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")
                     

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        dtdelta=t2-t1
                    
                    
                        if "day" in str(dtdelta) or "days" in str(dtdelta):
                            daystring = str(dtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(dtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            dfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(dtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(dtdelta).split(":")[1]
                            dfinalmins = int(dhrs)+int(dtmins)

                        timeport ={
                            "date":startdatestring,
                            "time":dfinalmins
                        }
                        protimelist.append(timeport)
                    #if task played and closed on different dates
                    else:
                        
                        # for startdate till 12 o'clock calculation
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        startdateendtime = str(a)+"T"+"23:59:00.00000+05:30"
                        strtdatetym = str(startdateendtime)
                        t2=datetime.datetime.strptime(strtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")
                        sdtdelta=t2-t1
                    
                    
                        if "day" in str(sdtdelta) or "days" in str(sdtdelta):
                            daystring = str(sdtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(sdtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            frstdayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(sdtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(sdtdelta).split(":")[1]
                            frstdayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":startdatestring,
                            "time":frstdayfinalmins
                        }
                        seconddaylist.append(secondtimeport)
                    #calculation of second day

                        seconddaystrt = str(b)+"T"+"00:00:00.00000+05:30"
                        seconddaystrtdatetym = str(seconddaystrt)
                        t11=datetime.datetime.strptime(seconddaystrtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)

                        seconddayenddt = endtime
                        t12 = datetime.datetime.strptime(seconddayenddt, "%Y-%m-%dT%H:%M:%S.%f%z")

                        seconddaytdelta=t12-t11

                        if "day" in str(seconddaytdelta) or "days" in str(seconddaytdelta):
                            daystring = str(seconddaytdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(seconddaytdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            secondayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(seconddaytdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(seconddaytdelta).split(":")[1]
                            secondayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":enddatestring,
                            "time":secondayfinalmins
                        }
                        seconddaylist.append(secondtimeport)

                    
                    finallist = protimelist+seconddaylist


                # finaldatetimelist= reduce(lambda d1,d2: {k: d1.get(k,0)+d2.get(k,0)for k in set(d1)|set(d2)}, timelist)
            
                maindata = []
                for p in finallist:
                
                    v=stock_maindictlist("date", p['date'],"time",p['time'], maindata)
                    if v == {}:
                        timecalc={
                            "date":p['date'],
                            "time":p['time'],
                        }
                        maindata.append(timecalc)
                
                for m in maindata:
                    totalhours = m['time']
                    hour = int (totalhours % 1440) // 60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalhours % 1440) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+" Hrs "+str(minutes)+" mins"

                    m['time'] = hourstring

                i['daywisetime']=maindata
            else:
                timelist=[]
                timedict={
                            "date":"--",
                            "time":"--"
                        }
                timelist.append(timedict)
                i['taskhours'] = "--------"
                i['daywisetime'] = timelist

        sortlist = emptaskser.data
        newlist = sorted(sortlist, key=itemgetter('UserID')) 
      
        my_date = datetime.date.today()
        curryear, week_num, day_of_week = my_date.isocalendar()
        currentweek = week_num
        currentyear = curryear


        context={
            'serdata':newlist,
            'currweek':currweek,
            'Currentyear':currentyear,
        }
            
        return Response({"n": 1, "Msg": "Tasks found successfully", "Status": "Success","data":context}, status=status.HTTP_201_CREATED)
    else:
        my_date = datetime.date.today()
        curryear, week_num, day_of_week = my_date.isocalendar()
        currentweek = week_num
        currentyear = curryear

        context={
            'Currentweek':currentweek,
            'Currentyear':currentyear,
        }

        return Response({"n": 0, "Msg": "Tasks not found ", "Status": "failure",'data':context}, status=status.HTTP_201_CREATED)
    






def get_week_of_month(year, month, day): 
    x = np.array(calendar.monthcalendar(year, month)) 
    week_of_month = np.where(x==day)[0][0] + 1 
    return(week_of_month)




@api_view(['POST'])
def weeklydataapi(request):
    userid = request.data['ajaxEmployee']
    Year = request.data['ajaxyear']
    Week = request.POST.getlist('ajaxweek')
    weeklydatalist = []
    piechartid = 0
    if userid is not None and userid != "" and userid != "All" :
        for w in Week:
            piechartid += 1
            weeklydatadict = {}
            year = int(Year)
            week = int(w)
            date_string = f'{year}-W{week}-1'
            month = datetime.datetime.strptime(date_string, "%Y-W%W-%w").month

            firstdateobj = TaskMaster.objects.filter(Year=Year,Week=w,AssignTo=userid).first()
            if firstdateobj is not None: 


                empname = Users.objects.filter(id=userid).first()
                empstrname = empname.Firstname +" "+ empname.Lastname
                employeeId = empname.uid
                if str(empname.Photo) is not None and str(empname.Photo) != "":
                    empimage = imageUrl +"/media/" + str(empname.Photo)
                else:
                    empimage = imageUrl + "/static/assets/images/profile.png"

                firstdate = str(firstdateobj.AssignDate)
                firstday = firstdate.split("-")[2]
                day = int(firstday)
                
                weeknumber = get_week_of_month(year,month,day)

                holidaysearch = Holidays.objects.filter(HolidayYear=year,HolidayMonth=month,                      Holidayweek_of_month=weeknumber,Active=True).count()

                if weeknumber % 2 == 0:
                    totalhours = 45
                    TotalWorkinghours = totalhours - (holidaysearch*9)
                else:
                    totalhours = 54
                    TotalWorkinghours = totalhours - (holidaysearch*9)



                weeklytime=0
                weekdictlist=[]
                searchobj = TaskMaster.objects.filter(Year=Year,Week=w,AssignTo=userid).order_by("id")
                searchobjser = GetTaskMasterSerializer(searchobj,many=True)
                for i in  searchobjser.data:
                    currentzone = pytz.timezone("Asia/Kolkata") 
                    currenttime = datetime.datetime.now(currentzone)
                    newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                    projecttasktime = ProjectTasks.objects.filter(Task=i['id']).order_by("id")
                    if projecttasktime is not None:
                        projectser = ProjectTasksSerializer(projecttasktime,many=True)
                        totaltime=0
                        for o in projectser.data:
                            startstring = o['StartDate']
                            starttime=startstring
                            t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                            endstring = o['EndDate']
                            if endstring is not None:
                                endtime = o['EndDate']
                            else:
                                endtime = str(newcurrenttime)
                            t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                            tdelta=t2-t1
                        
                        
                            if "day" in str(tdelta) or "days" in str(tdelta):
                                daystring = str(tdelta).split(",")[0]
                                noofdays = str(daystring).split(" ")[0]
                                daysmins = int(noofdays)*1440

                                thoursstr =  str(tdelta).split(",")[1]
                                thours = str(thoursstr).split(":")[0]
                                hrs = int(thours)*60
                                tmins = str(thoursstr).split(":")[1]
                                finalmins = int(hrs)+int(tmins)+int(daysmins)
                            else:
                                thours = str(tdelta).split(":")[0]
                                hrs = int(thours)*60
                                tmins = str(tdelta).split(":")[1]
                                finalmins = int(hrs)+int(tmins)
                            totaltime += finalmins
                        weeklytime += totaltime

                        totalhours =totaltime
                        hour = int (totalhours) // 60
                        if (len(str(hour)) < 2):
                            hours = "0"+str(hour)
                        else:
                            hours = str(hour)

                        mins = int (totalhours) % 60
                        if (len(str(mins)) < 2):
                            minutes = "0"+str(mins)
                        else:
                            minutes = str(mins)

                        hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                        i['taskhours'] = hourstring

                weektotalminutes = weeklytime

                #################### worked hrs and min and str ##########################################

                workedhours = round(int(weektotalminutes)/60,2) 

                workedddhours = weektotalminutes//60
                workedmins =  weektotalminutes%60
                workedstr = str(workedddhours)+" Hrs "+str(workedmins)+" Mins"

                workedpercentage = round ((weektotalminutes/(TotalWorkinghours*60))*100,2)

                #################### nonworked hrs and min and str ##########################################

                totalhourstr = str(TotalWorkinghours) +" Hrs"

                #################### nonworked hrs and min and str ##########################################

                remtime = float(TotalWorkinghours) - float(workedhours)

                if remtime < 0 :
                    remainingtime = 0
                else:
                    remainingtime = remtime

                remminutes = float(TotalWorkinghours*60) - float(weektotalminutes)
                min = remminutes  % 60 
                hrs = (remminutes - min) / 60 
                nonworkedhours = abs(remminutes//60)
                nonworkedmins =  abs(remminutes%60)
                nonworkedstr = str(int(nonworkedhours))+" Hrs "+str(int(nonworkedmins))+" Mins"

                if remminutes > 0 :
                    diffstring = "<span class='redmarks'><i class='fa fa-arrow-down'></i>" +nonworkedstr+"</span>" 
                else:
                    diffstring = "<span class='greenmarks'><i class='fa fa-arrow-up'></i>" +nonworkedstr+"</span>"

                rempercentage2 = round ((remminutes/(TotalWorkinghours*60))*100,2)
                if rempercentage2 < 0 :
                    rempercentage = 0
                else:
                    rempercentage = rempercentage2

              
                ############################----dict---#####################################################                

                weektimedict={
                    "title":"Worked Hours",
                    "tooltipvalue": workedpercentage,
                    "value": workedhours,
                    "hourstr":workedstr,
                    "sliceradius":100
                }
                weekdictlist.append(weektimedict)

                weektimedict2 = {
                    "title":"NonWorked Hours",
                    "tooltipvalue": rempercentage,
                    "value": remainingtime,
                    "hourstr":nonworkedstr,
                    "sliceradius":90
                }
                weekdictlist.append(weektimedict2)

                weeklydatadict['piechartid'] = piechartid
                weeklydatadict['userid'] = userid
                weeklydatadict['Empname'] = empstrname
                weeklydatadict['Piechartdata'] = weekdictlist
                weeklydatadict['EmployeeId'] = employeeId
                weeklydatadict['week'] = w
                weeklydatadict['year'] = Year
                weeklydatadict['Totalweekhours'] = totalhourstr
                weeklydatadict['TotalWorkedHours'] = workedstr
                weeklydatadict['remhours'] = nonworkedstr
                weeklydatadict['Userimage'] = empimage 
                weeklydatadict['Diffstring'] = diffstring

            if len(weeklydatadict) != 0 or weeklydatadict != {}:
                weeklydatalist.append(weeklydatadict)   

           
        finalweeklydatalist = list(filter(None, weeklydatalist))
        return Response({"n": 1, "Msg": "Data found successfully", "Status": "Success","data":finalweeklydatalist}, status=status.HTTP_201_CREATED)   
    else:
        userid = Users.objects.filter(is_active=True)
        userser = UserSerializer(userid,many=True)
        for e in userser.data:
            piechartid += 1
            weeklydatadict = {}
            year = int(Year)
            week = int(Week[0])
            date_string = f'{year}-W{week}-1'
            month = datetime.datetime.strptime(date_string, "%Y-W%W-%w").month

            firstdateobj = TaskMaster.objects.filter(Year=Year,Week=week,AssignTo=e['id']).first()

            if firstdateobj is not None: 
                empname = Users.objects.filter(id=e['id']).first()
                empstrname = empname.Firstname +" "+ empname.Lastname
                employeeId = empname.uid

                if str(empname.Photo) is not None and str(empname.Photo) != "":
                    empimage = imageUrl +"/media/" + str(empname.Photo)
                else:
                    empimage = imageUrl + "/static/assets/images/profile.png"
                


                firstdate = str(firstdateobj.AssignDate)
                firstday = firstdate.split("-")[2]
                day = int(firstday)
                
                weeknumber = get_week_of_month(year,month,day)

                holidaysearch = Holidays.objects.filter(HolidayYear=year,HolidayMonth=month,                      Holidayweek_of_month=weeknumber,Active=True).count()

                if weeknumber % 2 == 0:
                    totalhours = 45
                    TotalWorkinghours = totalhours - (holidaysearch*9)
                else:
                    totalhours = 54
                    TotalWorkinghours = totalhours - (holidaysearch*9)



                weeklytime=0
                weekdictlist=[]
                searchobj = TaskMaster.objects.filter(Year=Year,Week=week,AssignTo=e['id']).order_by("id")
                searchobjser = GetTaskMasterSerializer(searchobj,many=True)
                for i in  searchobjser.data:
                    currentzone = pytz.timezone("Asia/Kolkata") 
                    currenttime = datetime.datetime.now(currentzone)
                    newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                    projecttasktime = ProjectTasks.objects.filter(Task=i['id']).order_by("id")
                    if projecttasktime is not None:
                        projectser = ProjectTasksSerializer(projecttasktime,many=True)
                        totaltime=0
                        for o in projectser.data:
                            startstring = o['StartDate']
                            starttime=startstring
                            t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                            endstring = o['EndDate']
                            if endstring is not None:
                                endtime = o['EndDate']
                            else:
                                endtime = str(newcurrenttime)
                            t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                            tdelta=t2-t1
                        
                        
                            if "day" in str(tdelta) or "days" in str(tdelta):
                                daystring = str(tdelta).split(",")[0]
                                noofdays = str(daystring).split(" ")[0]
                                daysmins = int(noofdays)*1440

                                thoursstr =  str(tdelta).split(",")[1]
                                thours = str(thoursstr).split(":")[0]
                                hrs = int(thours)*60
                                tmins = str(thoursstr).split(":")[1]
                                finalmins = int(hrs)+int(tmins)+int(daysmins)
                            else:
                                thours = str(tdelta).split(":")[0]
                                hrs = int(thours)*60
                                tmins = str(tdelta).split(":")[1]
                                finalmins = int(hrs)+int(tmins)
                            totaltime += finalmins
                        weeklytime += totaltime

                        totalhours =totaltime
                        hour = int (totalhours) // 60
                        if (len(str(hour)) < 2):
                            hours = "0"+str(hour)
                        else:
                            hours = str(hour)

                        mins = int (totalhours) % 60
                        if (len(str(mins)) < 2):
                            minutes = "0"+str(mins)
                        else:
                            minutes = str(mins)

                        hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                        i['taskhours'] = hourstring

                weektotalminutes = weeklytime

                #################### worked hrs and min and str ##########################################

                workedhours = round(int(weektotalminutes)/60,2) 

                workedddhours = weektotalminutes//60
                workedmins =  weektotalminutes%60
                workedstr = str(workedddhours)+" Hrs "+str(workedmins)+" Mins"

                workedpercentage = round ((weektotalminutes/(TotalWorkinghours*60))*100,2)

                #################### nonworked hrs and min and str ##########################################

                totalhourstr = str(TotalWorkinghours) +" Hrs"

                #################### nonworked hrs and min and str ##########################################

                remtime = float(TotalWorkinghours) - float(workedhours)

                if remtime < 0 :
                    remainingtime = 0
                else:
                    remainingtime = remtime

                remminutes = float(TotalWorkinghours*60) - float(weektotalminutes)
                nonworkedhours = abs(remminutes//60)
                nonworkedmins =  abs(remminutes%60)
                nonworkedstr = str(int(nonworkedhours))+" Hrs "+str(int(nonworkedmins))+" Mins"

                if remminutes > 0 :
                    diffstring = "<span class='redmarks'><i class='fa fa-arrow-down'></i>" +nonworkedstr+"</span>" 
                else:
                    diffstring = "<span class='greenmarks'><i class='fa fa-arrow-up'></i>" +nonworkedstr+"</span>"

                rempercentage2 = round ((remminutes/(TotalWorkinghours*60))*100,2)

                if rempercentage2 < 0 :
                    rempercentage = 0
                else:
                    rempercentage = rempercentage2
              
                ############################----dict---#####################################################                

                weektimedict={
                    "title":"Worked Hours",
                    "tooltipvalue": workedpercentage,
                    "value": workedhours,
                    "hourstr":workedstr,
                    "sliceradius":100
                }
                weekdictlist.append(weektimedict)

                weektimedict2 = {
                    "title":"NonWorked Hours",
                    "tooltipvalue": rempercentage,
                    "value": remainingtime,
                    "hourstr":nonworkedstr,
                    "sliceradius":90
                }
                weekdictlist.append(weektimedict2)

                weeklydatadict['piechartid'] = piechartid
                weeklydatadict['userid'] = e['id']
                weeklydatadict['Empname'] = empstrname
                weeklydatadict['Piechartdata'] = weekdictlist
                weeklydatadict['EmployeeId'] = employeeId
                weeklydatadict['week'] = week
                weeklydatadict['year'] = Year
                weeklydatadict['Totalweekhours'] = totalhourstr
                weeklydatadict['TotalWorkedHours'] = workedstr
                weeklydatadict['remhours'] = nonworkedstr
                weeklydatadict['Userimage'] = empimage 
                weeklydatadict['Diffstring'] = diffstring

            if len(weeklydatadict) != 0:
                weeklydatalist.append(weeklydatadict)   

           
        finalweeklydatalist = list(filter(None, weeklydatalist))


        return Response({"n": 1, "Msg": "Data found successfully", "Status": "Success","data":finalweeklydatalist}, status=status.HTTP_201_CREATED)        
          


@api_view(['POST'])       
def userweekmodaldata(request):
    userid = request.data['ajaxEmployee']
    Year = request.data['ajaxyear']
    Week = request.data['ajaxweek']

    searchobj = TaskMaster.objects.filter(Year=Year,Week=Week,AssignTo=userid).order_by("id")
    
    if searchobj is not None :
        projectobj = TaskMaster.objects.filter(Year=Year,Week=Week,AssignTo=userid).distinct("Project")

        searchobjser = GetTaskMasterSerializer(projectobj,many=True)
        for h in searchobjser.data:
            projectid = h['Project']
            taskobj =  TaskMaster.objects.filter(Project=projectid,Year=Year,AssignTo=userid,Week=Week).order_by("AssignDate")
            taskser = GetTaskMasterSerializer(taskobj,many=True)
            projecthours=0
            for i in taskser.data:
               
                projectendtasktime = ProjectTasks.objects.filter(Task=i['id']).order_by("-id").first()
                
                if projectendtasktime is not None:
                    endtaskstring=projectendtasktime.EndDate
                    if endtaskstring :
                        endtasktimestring = str(endtaskstring)
                        etime = endtasktimestring.split(' ')[0]
                        userendtaskdate = etime.split('-')[2] +"-"+etime.split('-')[1] +"-"+etime.split('-')[0]
                        i['endtaskdate']=userendtaskdate


                
                strdate = str(i['AssignDate'])
                startmonth_name = calendar.month_abbr[int(strdate.split('-')[1])] 
                newdate = strdate.split('-')[2] +" "+startmonth_name+" "+strdate.split('-')[0]
                i['AssignDate']=newdate

                userObject=Users.objects.filter(id=i['AssignTo']).first()
                i['CreatedBy']=userObject.Firstname+" "+userObject.Lastname
              
                

                currentzone = pytz.timezone("Asia/Kolkata") 
                currenttime = datetime.datetime.now(currentzone)
                newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                projecttasktime = ProjectTasks.objects.filter(Task=i['id']).order_by("id")
                if projecttasktime is not None:
                    projectser = ProjectTasksSerializer(projecttasktime,many=True)
                    totaltime=0
                    for o in projectser.data:
                        startstring = o['StartDate']
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = o['EndDate']
                        if endstring is not None:
                            endtime = o['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        tdelta=t2-t1
                    
                    
                        if "day" in str(tdelta) or "days" in str(tdelta):
                            daystring = str(tdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(tdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            finalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            thours = str(tdelta).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(tdelta).split(":")[1]
                            finalmins = int(hrs)+int(tmins)
                        totaltime += finalmins
                    projecthours += totaltime

                    totalhours =totaltime
                    hour = int (totalhours) // 60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalhours) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                    i['taskhours'] = hourstring

                #  calculate day wise time strings

                protimelist = []
                seconddaylist = []
                finallist=[]
            
                for s in projectser.data:
                    startstring = s['StartDate']
                    enddatestr = s['EndDate']

                    a = startstring.split('T')[0]
                    revdate = a.split('-')[2]+"-"+ a.split('-')[1]+"-"+ a.split('-')[0]
                    startdatestring = revdate

                    if enddatestr is not None:
                        b = enddatestr.split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate
                    else:
                        b = str(newcurrenttime).split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate

                    # if task played and closed on same date

                    if startdatestring == enddatestring:

                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        dtdelta=t2-t1
                    
                    
                        if "day" in str(dtdelta) or "days" in str(dtdelta):
                            daystring = str(dtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(dtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            dfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(dtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(dtdelta).split(":")[1]
                            dfinalmins = int(dhrs)+int(dtmins)

                        timeport ={
                            "date":startdatestring,
                            "time":dfinalmins
                        }
                        protimelist.append(timeport)

                    #if task played and closed on different dates
                    else:
                        
                        # for startdate till 12 o'clock calculation
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        startdateendtime = str(a)+"T"+"23:59:00.00000+05:30"
                        strtdatetym = str(startdateendtime)
                        t2=datetime.datetime.strptime(strtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")
                        sdtdelta=t2-t1
                    
                    
                        if "day" in str(sdtdelta) or "days" in str(sdtdelta):
                            daystring = str(sdtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(sdtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            frstdayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(sdtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(sdtdelta).split(":")[1]
                            frstdayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":startdatestring,
                            "time":frstdayfinalmins
                        }
                        seconddaylist.append(secondtimeport)

                    #calculation of second day

                        seconddaystrt = str(b)+"T"+"00:00:00.00000+05:30"
                        seconddaystrtdatetym = str(seconddaystrt)
                        t11=datetime.datetime.strptime(seconddaystrtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)

                        seconddayenddt = endtime
                        t12 = datetime.datetime.strptime(seconddayenddt, "%Y-%m-%dT%H:%M:%S.%f%z")

                        seconddaytdelta=t12-t11

                        if "day" in str(seconddaytdelta) or "days" in str(seconddaytdelta):
                            daystring = str(seconddaytdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(seconddaytdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            secondayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(seconddaytdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(seconddaytdelta).split(":")[1]
                            secondayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":enddatestring,
                            "time":secondayfinalmins
                        }
                        seconddaylist.append(secondtimeport)

                    
                    finallist = protimelist+seconddaylist


            
                maindata = []
                for p in finallist:
                
                    v=stock_maindictlist("date", p['date'],"time",p['time'], maindata)
                    if v == {}:
                        timecalc={
                            "date":p['date'],
                            "time":p['time'],
                        }
                        maindata.append(timecalc)
                
                for m in maindata:
                    totalminutes = m['time']
                    hour = int (totalminutes)//60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalminutes) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+" Hrs "+str(minutes)+" mins"

                    m['time'] = hourstring

                i['daywisetime']=maindata

            ########################################### project info ########################3333
            h['userprojecttaskdata'] = taskser.data

            projecttotalminutes =projecthours
            phour = int (projecttotalminutes) // 60
            if (len(str(phour)) < 2):
                phours = "0"+str(phour)
            else:
                phours = str(phour)

            pmins = int (projecttotalminutes) % 60
            if (len(str(pmins)) < 2):
                pminutes = "0"+str(pmins)
            else:
                pminutes = str(pmins)

            h['projecthourstring'] = str(phours)+":"+str(pminutes)+" "+"Hrs"
            h['grade']=''
            if h['Zone'] == 1:
                h['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Green'><img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='Paris'></span>"

            if h['Zone'] == 2:
                h['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Yellow'><img src='/static/Media/taskicons/activeyellowpoints.svg' class='activeicons' alt='Paris'></span>"

            if h['Zone'] == 3:
                h['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Red'><img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='Paris' ></span>"

            if h['Zone'] == 4:
                h['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Not Done'><img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='Paris'></span>"

            if h['Zone'] == 5:
                h['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Cancelled'><img src='/static/Media/taskicons/activecancelledpoints.svg' class='activeicons' alt='Paris'></span>"

            if h['Zone'] == 6:
                h['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Rejected'><img src='/static/Media/taskicons/activerejectpoints.svg' class='activeicons' alt='Paris'></span>"

            if h['Zone'] == "" or h['Zone'] is None:
                h['grade'] = "--"


        return Response({"n": 1, "Msg": "Data found successfully", "Status": "Success","data":searchobjser.data}, status=status.HTTP_201_CREATED)        
    else:
        return Response({"n": 0, "Msg": "Data not found", "Status": "Success","data":""}, status=status.HTTP_201_CREATED)        


            
@api_view(['POST'])
def tasktime(request, format=None):   
    Taskid = request.data['Taskid']
    currentzone = pytz.timezone("Asia/Kolkata") 
    currenttime = datetime.datetime.now(currentzone)
    newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    

    taskobj = TaskMaster.objects.filter(id=Taskid).first()
    taskidlist = []
    if taskobj.ParentTaskId is not None:
        parenttaskid  = taskobj.ParentTaskId
        taskidlist.append(parenttaskid)

        taskobject = TaskMaster.objects.filter(ParentTaskId=parenttaskid)
        taskser = PostTaskMasterSerializer(taskobject,many=True)
        for t in taskser.data:
            taskidlist.append(t['id'])
    else:
        taskidlist.append(Taskid)
    if taskobj is not None:
        projecttasktime = ProjectTasks.objects.filter(Task__in=taskidlist).order_by("id")
        if projecttasktime is not None:
            projectser = ProjectTasksSerializer(projecttasktime,many=True)
            totaltime=0
            for o in projectser.data:
                
                startstring = o['StartDate']
                starttime=startstring
                t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                endstring = o['EndDate']
                if endstring is not None:
                    endtime = o['EndDate']
                else:
                    endtime = str(newcurrenttime)
            
                t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                tdelta=t2-t1
            
            
                if "day" in str(tdelta) or "days" in str(tdelta):
                    daystring = str(tdelta).split(",")[0]
                    noofdays = str(daystring).split(" ")[0]
                    daysmins = int(noofdays)*1440

                    thoursstr =  str(tdelta).split(",")[1]
                    thours = str(thoursstr).split(":")[0]
                    hrs = int(thours)*60
                    tmins = str(thoursstr).split(":")[1]
                    finalmins = int(hrs)+int(tmins)+int(daysmins)
                else:
                    thours = str(tdelta).split(":")[0]
                    hrs = int(thours)*60
                    tmins = str(tdelta).split(":")[1]
                    finalmins = int(hrs)+int(tmins)
                totaltime += finalmins

            totalhours =totaltime
            hour = int (totalhours) // 60
            if (len(str(hour)) < 2):
                hours = "0"+str(hour)
            else:
                hours = str(hour)

            mins = int (totalhours) % 60
            if (len(str(mins)) < 2):
                minutes = "0"+str(mins)
            else:
                minutes = str(mins)

            hourstring = str(hours)+":"+str(minutes)
            return Response({"n": 1, "Msg": "Data found successfully", "Status": "Success","data":hourstring}, status=status.HTTP_201_CREATED)        

        else:
            hourstring = str(00)+":"+str(00)
            return Response({"n": 0, "Msg": "Data not found in task time", "Status": "failure","data":hourstring}, status=status.HTTP_201_CREATED)        
    else:
        return Response({"n": 0, "Msg": "Task not found", "Status": "Success","data":''}, status=status.HTTP_201_CREATED)     
       

def getDateRangeFromWeek(p_year,p_week):
    firstdayofweek = datetime.datetime.strptime(f'{p_year}-W{int(p_week )}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + datetime.timedelta(days=6.9)
    return firstdayofweek, lastdayofweek


@api_view(['POST'])
def weekdatesapi(request, format=None):   
    Weekid = request.POST.get('week')
    year = request.POST.get('year')

    firstdate, lastdate =  getDateRangeFromWeek(year,Weekid)
    stdate = str(firstdate)
    startmonth_name = calendar.month_abbr[int(stdate.split('-')[1])]    
    startdatestr = stdate.split('-')[2]+" "+startmonth_name+" "+stdate.split('-')[0]
    
    endate = str(lastdate)
    endmonth_name = calendar.month_abbr[int(endate.split('-')[1])]  
    enddatestr = endate.split('-')[2]+" "+endmonth_name+" "+endate.split('-')[0]

    context={
        'startdate':startdatestr,
        'enddate':enddatestr
    }
    return Response({"n": 1, "Msg": "Data found successfully", "Status": "Success","data":context}, status=status.HTTP_201_CREATED)        


@api_view(['POST'])
def m_weeklyperc(request,format=None):
    userid = request.user.id
    perlist=[]
    labellist = []
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    currentweek = week_num
    week=currentweek

    for x in range(5):
        week = week - 1
        userobj = IntermediateTrackProResult.objects.filter(EmpID=userid,Year=year,Week=week).first()
        
        if userobj is not None:
            perlist.append(userobj.TrackProPercent)
            labellist.append("Week" + str(userobj.Week))
        else:
            perlist.append(0)
            labellist.append("Week" + str(week))

    perlist.reverse()
    labellist.reverse()
    
    context={
            'percentlist' : perlist,
            'labellist' : labellist
        }
    return Response({'data':context,"n":1,"Msg":"List fetched successfully","Status":"Success"})




# @api_view(['POST'])
# def m_userrankdata(request,format=None):
#     userid = request.user.id
#     my_date = datetime.date.today()
#     year, week_num, day_of_week = my_date.isocalendar()
#     curryear  = year
    
#     weeklist=[]
#     weekobjs =  TaskMaster.objects.filter(AssignTo=userid,Year=curryear).distinct("Week").order_by('id')
#     weekser = PostTaskMasterSerializer(weekobjs,many=True)
#     for t in weekser.data:
#         weeklist.append(t['Week'])

#     Weeklyinfolist = []
#     for w in weeklist :
#         weekdict = {}
#         weekdict['year'] = curryear
#         weekdict['week'] = w
#         Taskcount = TaskMaster.objects.filter(AssignTo=userid,Year=curryear,Week=w).count()
#         weekdict['Taskcount'] = Taskcount

#         intermediateobj = IntermediateTrackProResult.objects.filter(Employee=userid,Week=w,Year=y).first()
#         if intermediateobj is not None:
#             weekdict['Totalmarks'] = intermediateobj.TotalScore
#             weekdict['trackproscore'] = intermediateobj.TrackProScore
#             weekdict['percentage'] = intermediateobj.TrackProPercent

#             Projectlist = []
#             projectobj = TaskMaster.objects.filter(Year=curryear,Week=w,AssignTo=userid).distinct("Project")
#             searchobjser = GetTaskMasterSerializer(projectobj,many=True)
#             for h in searchobjser.data:
#                 projectdict = {}
#                 projectid = h['Project']
#                 projectobj = ProjectMaster.objects.filter(id=projectid).first()
#                 projectdict['projectname'] = projectobj.ProjectName

#                 taskprojectobj = TaskMaster.objects.filter(Year=curryear,Week=w,AssignTo=userid,Project=projectid).order_by('id')
#                 taskprojectser = GetTaskMasterSerializer(taskprojectobj,many=True)

#                 totalprojectcount = 0
#                 GreenZoneTask = 0
#                 YellowZoneTask = 0
#                 RedZoneTask = 0
#                 NotdoneZoneTask = 0
#                 bonus = 0
#                 cancelledZoneTask=0
#                 rejectedZoneTask=0
#                 creditamount=0

#                 for i in taskprojectser.data:
#                     if i['Zone'] == 1:
#                         i['green'] = 20
#                         GreenZoneTask += i['green']
#                     elif i['Zone'] == 2:
#                         i['yellow'] = 10
#                         YellowZoneTask += i['yellow']
#                     elif i['Zone'] == 3:
#                         i['red'] = 5
#                         RedZoneTask += i['red']
#                     elif i['Zone'] == 4:
#                         i['notdone'] = 20
#                         NotdoneZoneTask += i['notdone']
#                     elif i['Zone'] == 5:
#                         i['cancelled'] = 1
#                         cancelledZoneTask += i['cancelled']
#                     elif i['Zone'] == 6:
#                         i['rejected'] = 5
#                         rejectedZoneTask += i['rejected']
#                     if i['Bonus'] == True:
#                         i['isBonus'] = 20
#                         bonus += i['isBonus']

#                 totalTrackProScore = (GreenZoneTask + YellowZoneTask + RedZoneTask  + bonus) - (NotdoneZoneTask + rejectedZoneTask)



@api_view(['POST'])
def Empweeklytrackpro(request,format=None):
    userid = request.POST.get("empid")
    year = request.POST.get("year")


    weeklist=[]
    weekobjs = TaskMaster.objects.filter(AssignTo=userid,Year=year).distinct("Week")
    weekser = PostTaskMasterSerializer(weekobjs,many=True)
    for t in weekser.data:
        weeklist.append(t['Week'])

    weekdata=[]
    for w in weeklist:
        p={}
        p['strweek'] = "Week"+" "+str(w)
        trackproobj = IntermediateTrackProResult.objects.filter(Year=year,Week=w,Employee=userid).first()
        if trackproobj is not None:
            p['percent'] = str(trackproobj.TrackProPercent) +" "+"%"
            p['trackproscore'] = trackproobj.TrackProScore
            p['Totalscore'] = trackproobj.TotalScore
            if trackproobj.Rank is None:
                p['Rank'] = "-"
            else:
                p['Rank'] = trackproobj.Rank
        else:
            p['percent'] = "-"
            p['trackproscore'] = "-"
            p['Totalscore'] = "-"
            p['Rank'] = "-"
        
        p['greencount'] = TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Zone=1).count()

        p['yellowcount'] = TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Zone=2).count()
        
        p['redcount'] = TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Zone=3).count()
        
        p['notdonecount'] =  TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Zone=4).count()
        
        p['cancelcount'] = TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Zone=5).count()
        
        p['rejectcount'] =  TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Zone=6).count()

        p['Bonuscount'] =TaskMaster.objects.filter(Week=w,Year=year,AssignTo=userid,Bonus=True).count()

        if 10 <=  p['greencount'] <= 14:
            p['creditcount'] = 3
        elif 15 <=  p['greencount'] <= 19:
            p['creditcount'] = 7
        elif 20 <=  p['greencount'] <= 24:
            p['creditcount'] = 12
        elif 25 <=  p['greencount'] <= 29:
            p['creditcount'] = 18
        else:
            p['creditcount'] = 0

        weekdata.append(p)

    weekdata.reverse()

    return Response({'data':weekdata,"n":1,"Msg":"List fetched successfully","Status":"Success"})





# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def leavenotfscheduler(request):
#     if request.method == 'POST':
#         leaveobj = Leave.objects.filter()
     
    #     for status in Task:
    #         serializer = PostTaskMasterSerializer(
    #             status, data={"Status": 3}, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #     return Response({"n": 1, "Msg": "All Tasks are completed", "Status": "Success"})
    # return Response({"n": 0, "Msg": "Active Tasks present", "Status": "Failed"})


@api_view(['POST'])
def weekListbtn(request):
    year = request.data.get('year')
  
    if year is not None:
        week = TaskMaster.objects.filter(Year=year).order_by(
            'Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)

        
        for j in serializer.data:
            empobj = TaskMaster.objects.filter(Year=year,Week=j['Week'],).distinct("AssignTo")
            if empobj:
                empobjserializer=GetTaskSerializer(empobj,many=True)
                week_counter=0
                for emp in empobjserializer.data:
                    intobj = IntermediateTrackProResult.objects.filter(EmpID=emp['AssignTo'],Year=year,Week=j['Week']).first()
                    if intobj is not None:
                        week_counter += 0
                    else:
                        week_counter += 1
                if week_counter >= 1:
                    j['weekbtnstatus'] = False
                else:
                    j['weekbtnstatus'] = True
            else:
                j['weekbtnstatus'] = False
                
                
                    
        dept = Department.objects.filter(company_code=request.user.company_code,Active=True).order_by("-id")
        deptserializer = DepartmentSerializer(dept, many=True)
        for i in deptserializer.data :
            weeklist = []
            for w in serializer.data:
                weekdict = {}

                weekdict['year'] = year
                weekdict['week'] = str(w['Week'])
                gettaskobj = TaskMaster.objects.filter(Year=year,Week=w['Week'],AssignTo__in=Users.objects.filter(DepartmentID=i['id'])).distinct("AssignTo")

                # getdeptobj = IntermediateTrackProResult.objects.filter(Year=year,Week=w['Week'],EmpID__in=Users.objects.filter(DepartmentID=i['id']),DepartmentwiseRank__isnull = True)
                # if getdeptobj.exists():
                #     weekdict['viewrankbtn'] = False
                # else:
                #     weekdict['viewrankbtn'] = True
              
                if gettaskobj.exists():
                    taskserializer = GetTaskSerializer(gettaskobj,many=True)
                    counter = 0
                    deptcounter=0
                    for t in taskserializer.data:
                        intobj = IntermediateTrackProResult.objects.filter(EmpID=t['AssignTo'],Year=year,Week=w['Week']).first()
                        if intobj is not None:
                            counter += 0
                            deptrankk = intobj.DepartmentwiseRank
                            if deptrankk is not None and deptrankk != "":
                                deptcounter += 0
                            else:
                                deptcounter += 1 
                        else:
                            counter += 1
                            deptcounter += 1 

                    if deptcounter >= 1:
                        weekdict['viewrankbtn'] = False
                    else:
                        weekdict['viewrankbtn'] = True

                    if counter >= 1:
                        weekdict['btnstatus'] = False
                    else:
                        weekdict['btnstatus'] = True
                else:
                    weekdict['btnstatus'] = False
                    weekdict['viewrankbtn'] = False


                weeklist.append(weekdict)

            i['weeklist'] = weeklist
        context={
            'weeklist':serializer.data,
            'deptdata':deptserializer.data
        }
        return Response(context)
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})



@api_view(['POST'])
def getweeklyempinfoapi(request):
    year = request.data.get('getyear')
    week = request.data.get('getweek')
    department = request.data.get('getdept')
    companycode = request.user.company_code


    gettaskobj = TaskMaster.objects.filter(Year=year,Week=week,AssignTo__in=Users.objects.filter(DepartmentID=department)).distinct("AssignTo")

    emplist = []
    if gettaskobj.exists():
        taskserializer = GetTaskSerializer(gettaskobj,many=True)
        for t in taskserializer.data:
            empdict = {}
            intobj = IntermediateTrackProResult.objects.filter(EmpID=t['AssignTo'],Year=year,Week=week).first()
            if intobj is None:
                empdict['status'] = "--"
                empdict['rank'] = "--"
            else:
                perc = intobj.TrackProPercent
                empdict['status'] =  str(perc) + " %"   
                rankk = intobj.DepartmentwiseRank
                if rankk == "" or rankk is None:
                    empdict['rank'] = "--"
                else:
                     empdict['rank'] = rankk
            
            userObject=Users.objects.filter(id=t['AssignTo'],company_code=companycode).first()
            empdict['empname']=userObject.Firstname+" "+userObject.Lastname

            emplist.append(empdict)

        return Response({'data':emplist,"n":1,"Msg":"List fetched successfully","Status":"Success"})
    else:
        return Response({'data':[],"n": 0, "Msg": "No task found", "Status": "failed"})


@api_view(['POST'])
def overall_week_avg_ny_dept_api(request):
    department = request.POST.get('getdept')
    companycode = request.user.company_code
    gettaskobj = TaskMaster.objects.filter(AssignTo__in=Users.objects.filter(DepartmentID=department)).distinct("AssignTo")
    
    def add_employee(employee_list, emp_name, percentage):
        # Create a dictionary for the new employee
        new_employee = {'Name': emp_name, 'Percentage': percentage}

        # Calculate the rank of the new employee based on percentage
        rank = 1
        for employee in employee_list:
            if employee['Percentage'] > percentage:
                rank += 1

        # Insert the new employee at the correct position based on rank
        employee_list.insert(rank - 1, new_employee)

        return employee_list

    emplist = []
    if gettaskobj.exists():
        taskserializer = GetTaskSerializer(gettaskobj,many=True)
        for t in taskserializer.data:
            empdict = {}
            percentagelist=[]
            
            def average_percentage(numbers):
                if not numbers:
                    return 0.0  # Return 0 if the list is empty to avoid division by zero
                total_percentage = sum(numbers) / len(numbers)
                return round(total_percentage)
            
            
            Percentage_Object = IntermediateTrackProResult.objects.filter(EmpID=t['AssignTo'],).exclude(DepartmentwiseRank__isnull=True)
            if Percentage_Object is not None:
                Ser=IntermediateGetTrackProResultSerializer(Percentage_Object,many=True)
                for i in Ser.data:
                    percentagelist.append(i['TrackProPercent'])
                
            empdict['Avg_percentage'] =  str(average_percentage(percentagelist)) + " %"   
            userObject=Users.objects.filter(id=t['AssignTo'],company_code=companycode).first()
            empdict['empname']=userObject.Firstname+" "+userObject.Lastname
            emplist = add_employee(emplist, empdict['empname'], empdict['Avg_percentage'])


        return Response({'data':emplist,"n":1,"Msg":"List fetched successfully","Status":"Success"})
    else:
        return Response({'data':[],"n": 0, "Msg": "No task found", "Status": "failed"})

  
@api_view(['POST'])
def viewweeklyempinfoapi(request):
    year = request.data.get('getyear')
    week = request.data.get('getweek')
    department = request.data.get('getdept')

    companycode = request.user.company_code


    gettaskobj = TaskMaster.objects.filter(Year=year,Week=week,AssignTo__in=Users.objects.filter(DepartmentID=department)).distinct("AssignTo")
    
    emplist = []
    if gettaskobj.exists():
        taskserializer = GetTaskSerializer(gettaskobj,many=True)
        for t in taskserializer.data:
            empdict = {}
            intobj = IntermediateTrackProResult.objects.filter(EmpID=t['AssignTo'],Year=year,Week=week).first()
            if intobj is not None:
                perc = intobj.TrackProPercent
                rankk = intobj.DepartmentwiseRank
                getrank = intobj.DepartmentwiseRank
            else:
                perc ="--"
                rankk = "--"
                getrank = 0
            empdict['status'] =  str(perc) + " %"   
            empdict['getrank'] = getrank
            empdict['rank'] = rankk
            
            userObject=Users.objects.filter(id=t['AssignTo'],company_code=companycode).first()
            empdict['empname']=userObject.Firstname+" "+userObject.Lastname

            emplist.append(empdict)

        newlist = sorted(emplist, key=lambda d: d['getrank']) 
        return Response({'data':newlist,"n":1,"Msg":"List fetched successfully","Status":"Success"})
    else:
        return Response({'data':[],"n": 0, "Msg": "No task found", "Status": "failed"})

                
@api_view(['POST'])
def publishdeptwiserankapi(request):
    year = request.data.get('getyear')
    week = request.data.get('getweek')
    department = request.data.get('getdept')
    companycode = request.user.company_code    

    gettaskobj = IntermediateTrackProResult.objects.filter(Year=year,Week=week,EmpID__in=Users.objects.filter(DepartmentID=department)).order_by('-TrackProPercent')
    if gettaskobj.exists():
        empobjserializer = IntermediateGetTrackProResultSerializer(gettaskobj,many=True)
        rankcount = 1
        for i in empobjserializer.data:
            empobj = IntermediateTrackProResult.objects.filter(id=i['id']).update(DepartmentwiseRank=rankcount)
            rankcount += 1
        
        return Response({'data':[],"n":1,"Msg":"Department Ranks Published successfully","Status":"Success"})
    else:
        return Response({'data':[],"n": 0, "Msg": "Couldn't publish ranks", "Status": "failed"})


def convertdate(date):
    if date != "" and date is not None:
        datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        day = datetime_obj.day
        month = datetime_obj.strftime("%B")
        year = datetime_obj.year

        # convert day to a string with appropriate suffix
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        # format the date in "Dth Month YYYY" format
        formatted_date = f"{day}{suffix} {month} {year}"

        return formatted_date
    return "---"



@api_view(['GET'])
def user_pending_task(request, format=None):

    userid = request.user.id
    current_date =datetime.datetime.now()
    Year, Week, _ = current_date.isocalendar()
    pending_tasks= TaskMaster.objects.filter(
            Year=Year, Week=Week,AssignTo=userid,Zone__isnull= True).exclude(Status=3)

    if pending_tasks:

        serializer = GetPendingTaskMasterSerializer(pending_tasks, many=True)
        for i in serializer.data:

            i['AssignDate']=convertdate(i['AssignDate'])     
            currentzone = pytz.timezone("Asia/Kolkata") 
            currenttime = datetime.datetime.now(currentzone)
            newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

            taskobj = TaskMaster.objects.filter(id=i['id']).first()
            taskidlist = []
            if taskobj.ParentTaskId is not None:
                parenttaskid  = taskobj.ParentTaskId
                taskidlist.append(parenttaskid)
                taskobject = TaskMaster.objects.filter(ParentTaskId=parenttaskid)
                taskser = PostTaskMasterSerializer(taskobject,many=True)
                for t in taskser.data:
                    taskidlist.append(t['id'])
            else:
                taskidlist.append(i['id'])
                taskobject = TaskMaster.objects.filter(ParentTaskId=i['id'])
                taskser = PostTaskMasterSerializer(taskobject,many=True)
                for t in taskser.data:
                    taskidlist.append(t['id'])

            projecttask = ProjectTasks.objects.filter(Task_id__in=taskidlist)
            if projecttask:
                projectser = ProjectTasksSerializer(projecttask,many=True)
                FMT = '%H:%M:%S.%f'
                totaltime=0
            
                for p in projectser.data:
                    startstring = p['StartDate']
                    starttime=startstring
                    t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                    endstring = p['EndDate']
                    if endstring :
                        endtime = p['EndDate']
                    else:
                        endtime = str(newcurrenttime)
                    t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                    tdelta=t2-t1
                
                
                    if "day" in str(tdelta) or "days" in str(tdelta):
                        daystring = str(tdelta).split(",")[0]
                        noofdays = str(daystring).split(" ")[0]
                        daysmins = int(noofdays)*1440

                        thoursstr =  str(tdelta).split(",")[1]
                        thours = str(thoursstr).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(thoursstr).split(":")[1]
                        finalmins = int(hrs)+int(tmins)+int(daysmins)
                    else:
                        thours = str(tdelta).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(tdelta).split(":")[1]
                        finalmins = int(hrs)+int(tmins)
                    totaltime += finalmins

                totalhours =totaltime
                hour = int (totalhours) // 60
                if (len(str(hour)) < 2):
                    hours = "0"+str(hour)
                else:
                    hours = str(hour)

                mins = int (totalhours) % 60
                if (len(str(mins)) < 2):
                    minutes = "0"+str(mins)
                else:
                    minutes = str(mins)

                hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                i['taskhours'] = hourstring

        return Response({'data':serializer.data,'Taskcount':len(serializer.data),"n":1,"Msg":"task found","Status":"Success"})
    return Response({'data':[],'Taskcount':0,"n":1,"Msg":"task not found","Status":"failed"})
   

    
@api_view(['POST'])
@permission_classes((AllowAny,))
def weeklytasks(request, format=None):
    empid = request.data.get('empid')
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    Week = int(week_num)
    Year= int(year)

    taskobj = TaskMaster.objects.filter(Year=Year,Week=Week,AssignTo=empid).order_by('CreatedOn')
    if taskobj is not None:
        ser=PostTaskMasterSerializer(taskobj,many=True)
        for i in ser.data:
            if i['Status'] == 3:
                i['task_status'] = "<img data-bs-toggle='tooltip' data-bs-placement='bottom' title='Completed' src='/static/Media/taskicons/checktrackprocompleted.svg' class='task_status_icon' alt='notdone'>"
            else:
                i['task_status'] = "<img data-bs-toggle='tooltip' data-bs-placement='bottom' title='Inprocess' src='/static/Media/taskicons/checktrackprorunning.svg' class='task_status_icon' alt='notdone'>"
            
            strdate = str(i['AssignDate'])
            startmonth_name = calendar.month_abbr[int(strdate.split('-')[1])]  
            newdate = strdate.split('-')[2] +" "+startmonth_name +" "+strdate.split('-')[0]
            i['AssignDate']=newdate

            userObject=Users.objects.filter(id=i['AssignTo']).first()
            i['CreatedBy']=userObject.Firstname+" "+userObject.Lastname

            currentzone = pytz.timezone("Asia/Kolkata") 
            currenttime = datetime.datetime.now(currentzone) 
           
            newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

            taskobj = TaskMaster.objects.filter(id=i['id']).first()
            taskidlist = []
            if taskobj.ParentTaskId is not None:
                parenttaskid  = taskobj.ParentTaskId
                taskidlist.append(parenttaskid)

                taskobject = TaskMaster.objects.filter(ParentTaskId=parenttaskid)
                taskser = PostTaskMasterSerializer(taskobject,many=True)
                for t in taskser.data:
                    taskidlist.append(t['id'])
            else:
                taskidlist.append(i['id'])
                taskobject = TaskMaster.objects.filter(ParentTaskId=i['id'])
                taskser = PostTaskMasterSerializer(taskobject,many=True)
                for t in taskser.data:
                    taskidlist.append(t['id'])

            
            projecttasktime = ProjectTasks.objects.filter(Task__in=taskidlist).order_by("id")
            if projecttasktime :
                projectser = ProjectTasksSerializer(projecttasktime,many=True)
                FMT = '%H:%M:%S.%f'
                totaltime=0
                for o in projectser.data:
                    startstring = o['StartDate']
                    starttime=startstring
                    t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                    endstring = o['EndDate']
                    if endstring is not None:
                        endtime = o['EndDate']
                    else:
                        endtime = str(newcurrenttime)
                    t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                    tdelta=t2-t1
                  
                   
                    if "day" in str(tdelta) or "days" in str(tdelta):
                        daystring = str(tdelta).split(",")[0]
                        noofdays = str(daystring).split(" ")[0]
                        daysmins = int(noofdays)*1440

                        thoursstr =  str(tdelta).split(",")[1]
                        thours = str(thoursstr).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(thoursstr).split(":")[1]
                        finalmins = int(hrs)+int(tmins)+int(daysmins)
                    else:
                        thours = str(tdelta).split(":")[0]
                        hrs = int(thours)*60
                        tmins = str(tdelta).split(":")[1]
                        finalmins = int(hrs)+int(tmins)
                    totaltime += finalmins

                totalhours =totaltime
                hour = int (totalhours) // 60
                if (len(str(hour)) < 2):
                    hours = "0"+str(hour)
                else:
                    hours = str(hour)

                mins = int (totalhours) % 60
                if (len(str(mins)) < 2):
                    minutes = "0"+str(mins)
                else:
                    minutes = str(mins)

                hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                i['taskhours'] = hourstring

                #  calculate day wise time strings

                protimelist = []
                seconddaylist = []
                finallist=[]
            
                for s in projectser.data:

                    FMT = '%H:%M:%S.%f'
                   
                    startstring = s['StartDate']
                    enddatestr = s['EndDate']

                    a = startstring.split('T')[0]
                    revdate = a.split('-')[2]+"-"+ a.split('-')[1]+"-"+ a.split('-')[0]
                    startdatestring = revdate

                    if enddatestr is not None:
                        b = enddatestr.split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate
                    else:
                        b = str(newcurrenttime).split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate

                    # if task played and closed on same date
                    if startdatestring == enddatestring:

                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")
                     

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        dtdelta=t2-t1
                    
                    
                        if "day" in str(dtdelta) or "days" in str(dtdelta):
                            daystring = str(dtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(dtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            dfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(dtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(dtdelta).split(":")[1]
                            dfinalmins = int(dhrs)+int(dtmins)

                        timeport ={
                            "date":startdatestring,
                            "time":dfinalmins
                        }
                        protimelist.append(timeport)
                    #if task played and closed on different dates
                    else:
                        
                        # for startdate till 12 o'clock calculation
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        startdateendtime = str(a)+"T"+"23:59:00.00000+05:30"
                        strtdatetym = str(startdateendtime)
                        t2=datetime.datetime.strptime(strtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")
                        sdtdelta=t2-t1
                    
                    
                        if "day" in str(sdtdelta) or "days" in str(sdtdelta):
                            daystring = str(sdtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(sdtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            frstdayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(sdtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(sdtdelta).split(":")[1]
                            frstdayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":startdatestring,
                            "time":frstdayfinalmins
                        }
                        seconddaylist.append(secondtimeport)
                    #calculation of second day

                        seconddaystrt = str(b)+"T"+"00:00:00.00000+05:30"
                        seconddaystrtdatetym = str(seconddaystrt)
                        t11=datetime.datetime.strptime(seconddaystrtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)

                        seconddayenddt = endtime
                        t12 = datetime.datetime.strptime(seconddayenddt, "%Y-%m-%dT%H:%M:%S.%f%z")

                        seconddaytdelta=t12-t11

                        if "day" in str(seconddaytdelta) or "days" in str(seconddaytdelta):
                            daystring = str(seconddaytdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(seconddaytdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            secondayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(seconddaytdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(seconddaytdelta).split(":")[1]
                            secondayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":enddatestring,
                            "time":secondayfinalmins
                        }
                        seconddaylist.append(secondtimeport)

                    
                    finallist = protimelist+seconddaylist


                # finaldatetimelist= reduce(lambda d1,d2: {k: d1.get(k,0)+d2.get(k,0)for k in set(d1)|set(d2)}, timelist)
            
                maindata = []
                for p in finallist:
                
                    v=stock_maindictlist("date", p['date'],"time",p['time'], maindata)
                    if v == {}:
                        timecalc={
                            "date":p['date'],
                            "time":p['time'],
                        }
                        maindata.append(timecalc)
                
                for m in maindata:
                    totalhours = m['time']
                    hour = int (totalhours % 1440) // 60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalhours % 1440) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+" Hrs "+str(minutes)+" mins"

                    m['time'] = hourstring

                i['daywisetime']=maindata
            else:
                timelist=[]
                timedict={
                            "date":"--",
                            "time":"--"
                        }
                timelist.append(timedict)
                i['taskhours'] = "--------"
                i['daywisetime'] = timelist

   
    return Response({'data':ser.data,"n":1,"Msg":"List fetched successfully","Status":"Success"})





@api_view(['POST'])
def manager_remark(request):
    log_in_user = request.user.id
    data = {}
    data['created_by'] = request.user.id
    data['created_by_str'] = str(request.user.Firstname) + " " + str(request.user.Lastname)
    data['ismanager'] = True
    data['remark_comment'] = request.POST.get('remark_comment')
    data['user_id'] = request.POST.get('user_id')
    data['task_id'] = request.POST.get('task_id')
    if data['task_id'] is not None and data['user_id'] is not None and data['remark_comment'] is not None and data['task_id'] != "" and data['user_id'] != "" and data['remark_comment'] != "" : 
        if int(log_in_user) != int(data['user_id']):

            user_object = Users.objects.filter(is_active=True,id=int(data['user_id'])).first()
            if user_object is not None:
                data['user_str'] = str(user_object.Firstname) + " " + str(user_object.Lastname)
                task_manager_list = list(UserToManager.objects.filter(Active=True).distinct('ManagerID').values_list('ManagerID', flat=True))
                if log_in_user in task_manager_list:
                    remarkcount = TaskRemark.objects.filter(Active=True,task_id=data['task_id']).count()
                    if remarkcount < 4 :
                        remark_serializer = TaskRemarkSerializer(data=data)
                        if remark_serializer.is_valid():
                            remark_serializer.save()

                            TaskNotification.objects.create(
                                NotificationTitle = "Task Remark Alert",
                                NotificationMsg = "</span>" + data['created_by_str'] +" has provided remark on your task.</span>",
                                UserID_id = data['user_id'],
                                NotificationTypeId_id = 5 ,
                                leaveID = 0,
                                created_by = request.user.id,
                                company_code = request.user.company_code,
                            )

                            firebasemsg =  data['created_by_str'] +" has provided remark on your task."
                            fcmtoken = user_object.FirebaseID
                            notftype = "Task Remark Alert"
                            fcmleaveid = 0
                            fcmtomanager = False
                                            
                            desktoptoken = user_object.desktopToken 
                            # desktopnotf = senddesktopnotf(desktoptoken,firebasemsg)
                            
                            if fcmtoken is not None and fcmtoken != "":
                                firebasenotification = ""
                                # firebasenotification = sendfirebasenotification(fcmtoken,firebasemsg,notftype,fcmleaveid,fcmtomanager)
                            else:
                                firebasenotification = ""   
                                    
                                        
                            data_dict = {
                                        "employeename":user_object.Firstname +' '+user_object.Lastname,
                                        "remarkby":data['created_by_str'] ,
                                        "remark":data['remark_comment'] ,
                                    }
                            task_obj=TaskMaster.objects.filter(id=data['task_id'],Active=True).first()
                            if task_obj is not None:
                                task_serializer=GetTaskSerializer(task_obj)
                                taskdetails=task_serializer.data
                                taskdetails['AssignDate']=convertdate2(taskdetails['AssignDate'])
                                data_dict['task_details']=taskdetails
                            
                            send_async_custom_template_email(
                                'Task Remark Alert',
                                data_dict,
                                "no-reply@onerooftech.com",
                                [str(user_object.email)],
                                "mails/taskremarkmail.html"
                            )
                                
                                
                                
                                
                                
                                
                                
                                
                                
                            return Response({'data':remark_serializer.data,"n": 1, "Msg": "Remark added successfully", "Status": "success"})  
                        else:
                            return Response({'data':[],"n": 0, "Msg": "Error while adding remark ", "Status": "failed"})     
                    else:
                        return Response({'data':[],"n": 0, "Msg": "Remark max limit reached", "Status": "failed"})    
                return Response({'data':[],"n": 0, "Msg": "User can't give remark", "Status": "failed"})
            return Response({'data':[],"n": 0, "Msg": "User not found", "Status": "failed"})
        return Response({'data':[],"n": 0, "Msg": "User can't comment on his own task", "Status": "failed"})
    return Response({'data':[],"n": 0, "Msg": "Please provide necessary requirements", "Status": "failed"})



@api_view(['POST'])
def employee_remark(request):
    log_in_user = request.user.id
    data = {}
    data['created_by'] = request.user.id
    data['created_by_str'] = str(request.user.Firstname) + " " + str(request.user.Lastname)
    data['ismanager'] = False
    data['remark_comment'] = request.POST.get('remark_comment')
    data['user_id'] = request.POST.get('user_id')
    data['task_id'] = request.POST.get('task_id')
    if data['task_id'] is not None and data['user_id'] is not None and data['remark_comment'] is not None and data['task_id'] != "" and data['user_id'] != "" and data['remark_comment'] != "" : 
        if int(log_in_user) == int(data['user_id']):
            user_object = Users.objects.filter(is_active=True,id=int(data['user_id'])).first()
            if user_object is not None:
                data['user_str'] = str(user_object.Firstname) + " " + str(user_object.Lastname)
                remarkcount = TaskRemark.objects.filter(Active=True,task_id=data['task_id']).count()
                if remarkcount < 4 :
                    remark_serializer = TaskRemarkSerializer(data=data)
                    if remark_serializer.is_valid():
                        remark_serializer.save()
                        manager_task_list = list(TaskRemark.objects.filter(task_id=data['task_id'],Active=True,ismanager=True).values_list('created_by', flat=True))

                        manager_list = list(set(manager_task_list))
                        for m in manager_list:
                            TaskNotification.objects.create(
                                NotificationTitle = "Task Remark Alert",
                                NotificationMsg = "<span>" + data['user_str'] +" has Commented on Task remark.</span>",
                                UserID_id = m,
                                NotificationTypeId_id = 5 ,
                                leaveID = 0,
                                created_by = request.user.id,
                                company_code = request.user.company_code,
                            )

                        firebasemsg =  data['user_str'] + " has Commented on Task remark."
                        fcmtoken = user_object.FirebaseID
                        notftype = "Task Remark Alert"
                        fcmleaveid = 0
                        fcmtomanager = False
                        
                        desktoptoken = user_object.desktopToken 
                        # desktopnotf = senddesktopnotf(desktoptoken,firebasemsg)
                        
                        if fcmtoken is not None and fcmtoken != "":
                            firebasenotification = ""

                            # firebasenotification = sendfirebasenotification(fcmtoken,firebasemsg,notftype,fcmleaveid,fcmtomanager)
                        else:
                            firebasenotification = ""





                        return Response({'data':remark_serializer.data,"n": 1, "Msg": "Remark added successfully", "Status": "success"})  
                    else:
                        return Response({'data':[],"n": 0, "Msg": "Error while adding remark ", "Status": "failed"})     
                else:
                    return Response({'data':[],"n": 0, "Msg": "Remark max limit reached", "Status": "failed"})    
            return Response({'data':[],"n": 0, "Msg": "User not found", "Status": "failed"})
        return Response({'data':[],"n": 0, "Msg": "User can't comment on his own task", "Status": "failed"})
    return Response({'data':[],"n": 0, "Msg": "Please provide necessary requirements", "Status": "failed"})


@api_view(['POST'])
def task_remark_list(request):
    data = {}
    data['task_id'] = request.POST.get("task_id")
    if data['task_id'] is not None and data['task_id'] != "":

        remarkobject = TaskRemark.objects.filter(Active=True,task_id=data['task_id']).order_by('id')
        remark_ser = TaskRemarkSerializer(remarkobject,many=True)
        for i in remark_ser.data:
            created_on = i['CreatedOn'].split("T")[0]
            created_date = created_on.split("-")[2] + "-" + created_on.split("-")[1] + "-" + created_on.split("-")[0] 
            created_time = i['CreatedOn'].split("T")[1].split(".")[0]
            i['created_date'] = created_date + " " + created_time
        return Response({'data':remark_ser.data,"n": 1, "Msg": "Remark list fetched successfully", "Status": "success"})  
    return Response({'data':[],"n": 0, "Msg": "Please provide necessary requirements", "Status": "failed"})


@api_view(['POST'])
def dashboardtask_remark_list(request):
    data = {}
    data['task_id'] = request.POST.get("task_id")
    if data['task_id'] is not None and data['task_id'] != "":
        remarkread = TaskRemark.objects.filter(Active=True,task_id=data['task_id']).update(IsRead=True)
        remarkobject = TaskRemark.objects.filter(Active=True,task_id=data['task_id']).order_by('id')
        remark_ser = TaskRemarkSerializer(remarkobject,many=True)
        for i in remark_ser.data:
            created_on = i['CreatedOn'].split("T")[0]
            created_date = created_on.split("-")[2] + "-" + created_on.split("-")[1] + "-" + created_on.split("-")[0] 
            created_time = i['CreatedOn'].split("T")[1].split(".")[0]
            i['created_date'] = created_date + " " + created_time
        return Response({'data':remark_ser.data,"n": 1, "Msg": "Remark list fetched successfully", "Status": "success"})  
    return Response({'data':[],"n": 0, "Msg": "Please provide necessary requirements", "Status": "failed"})


@api_view(['POST'])       
def search_tasks(request):
    userid = request.POST.get('Employee')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    ongoingtasks = request.POST.get('ongoingtasks')
   
    if ongoingtasks.lower() == 'true':
        excludestatuelist=[3]
    elif ongoingtasks.lower() == 'false':
        excludestatuelist=[1,2]
    else:
        excludestatuelist=[]


    
    Projectid = l1l2projectid
    

    if userid != "All":
        searchobj = TaskMaster.objects.filter(AssignTo=userid,AssignDate__range=[start_date, end_date],Project=Projectid).order_by("id").exclude(Status__in=excludestatuelist)
    else:
        searchobj = TaskMaster.objects.filter(AssignDate__range=[start_date, end_date],Project=Projectid).order_by("id").exclude(Status__in=excludestatuelist)

    if searchobj is not None :
        if userid != "All":
            projectobj = TaskMaster.objects.filter(AssignTo=userid,AssignDate__range=[start_date, end_date],Project=Projectid).distinct("AssignTo").exclude(Status__in=excludestatuelist)
        else:
            projectobj = TaskMaster.objects.filter(AssignDate__range=[start_date, end_date],Project=Projectid).distinct("AssignTo").exclude(Status__in=excludestatuelist)

        searchobjser = GetTaskMasterSerializer(projectobj,many=True)


        for h in searchobjser.data:
            projectid = h['Project']
            assignto = h['AssignTo']
            taskobj =  TaskMaster.objects.filter(Project=projectid,AssignTo=assignto,AssignDate__range=[start_date, end_date]).order_by("AssignDate").exclude(Status__in=excludestatuelist)
            taskser = GetTaskMasterSerializer(taskobj,many=True)
            projecthours=0
            count=1

            for i in taskser.data:
                i['count']=count
                count+=1
                projectendtasktime = ProjectTasks.objects.filter(Task=i['id']).order_by("-id").first()
                if projectendtasktime is not None:
                    endtaskstring=projectendtasktime.EndDate
                    if endtaskstring :
                        endtasktimestring = str(endtaskstring)
                        etime = endtasktimestring.split(' ')[0]
                        userendtaskdate = etime.split('-')[2] +"-"+etime.split('-')[1] +"-"+etime.split('-')[0]
                        i['endtaskdate']=userendtaskdate

                strdate = str(i['AssignDate'])
                startmonth_name = calendar.month_abbr[int(strdate.split('-')[1])] 
                newdate = strdate.split('-')[2] +" "+startmonth_name+" "+strdate.split('-')[0]
                i['AssignDate']=newdate

                userObject=Users.objects.filter(id=i['AssignTo']).first()
                i['CreatedBy']=userObject.Firstname+" "+userObject.Lastname
              
                

                currentzone = pytz.timezone("Asia/Kolkata") 
                currenttime = datetime.datetime.now(currentzone)
                newcurrenttime =currenttime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                projecttasktime = ProjectTasks.objects.filter(Task=i['id']).order_by("id")
                if projecttasktime is not None:
                    projectser = ProjectTasksSerializer(projecttasktime,many=True)
                    totaltime=0
                    for o in projectser.data:
                        startstring = o['StartDate']
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = o['EndDate']
                        if endstring is not None:
                            endtime = o['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        tdelta=t2-t1
                    
                    
                        if "day" in str(tdelta) or "days" in str(tdelta):
                            daystring = str(tdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(tdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            finalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            thours = str(tdelta).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(tdelta).split(":")[1]
                            finalmins = int(hrs)+int(tmins)
                        totaltime += finalmins
                    projecthours += totaltime

                    totalhours =totaltime
                    hour = int (totalhours) // 60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalhours) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+":"+str(minutes)+" "+"Hrs"

                    i['taskhours'] = hourstring

                #  calculate day wise time strings

                protimelist = []
                seconddaylist = []
                finallist=[]
            
                for s in projectser.data:
                    startstring = s['StartDate']
                    enddatestr = s['EndDate']

                    a = startstring.split('T')[0]
                    revdate = a.split('-')[2]+"-"+ a.split('-')[1]+"-"+ a.split('-')[0]
                    startdatestring = revdate

                    if enddatestr is not None:
                        b = enddatestr.split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate
                    else:
                        b = str(newcurrenttime).split('T')[0]
                        revenddate = b.split('-')[2]+"-"+ b.split('-')[1]+"-"+ b.split('-')[0]
                        enddatestring = revenddate

                    # if task played and closed on same date

                    if startdatestring == enddatestring:

                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)
                        t2=datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S.%f%z")
                        dtdelta=t2-t1
                    
                    
                        if "day" in str(dtdelta) or "days" in str(dtdelta):
                            daystring = str(dtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(dtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            dfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(dtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(dtdelta).split(":")[1]
                            dfinalmins = int(dhrs)+int(dtmins)

                        timeport ={
                            "date":startdatestring,
                            "time":dfinalmins
                        }
                        protimelist.append(timeport)

                    #if task played and closed on different dates
                    else:
                        
                        # for startdate till 12 o'clock calculation
                        starttime=startstring
                        t1 = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f%z")

                        startdateendtime = str(a)+"T"+"23:59:00.00000+05:30"
                        strtdatetym = str(startdateendtime)
                        t2=datetime.datetime.strptime(strtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")
                        sdtdelta=t2-t1
                    
                    
                        if "day" in str(sdtdelta) or "days" in str(sdtdelta):
                            daystring = str(sdtdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(sdtdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            frstdayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(sdtdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(sdtdelta).split(":")[1]
                            frstdayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":startdatestring,
                            "time":frstdayfinalmins
                        }
                        seconddaylist.append(secondtimeport)


                        seconddaystrt = str(b)+"T"+"00:00:00.00000+05:30"
                        seconddaystrtdatetym = str(seconddaystrt)
                        t11=datetime.datetime.strptime(seconddaystrtdatetym, "%Y-%m-%dT%H:%M:%S.%f%z")

                        endstring = s['EndDate']
                        if endstring is not None:
                            endtime = s['EndDate']
                        else:
                            endtime = str(newcurrenttime)

                        seconddayenddt = endtime
                        t12 = datetime.datetime.strptime(seconddayenddt, "%Y-%m-%dT%H:%M:%S.%f%z")

                        seconddaytdelta=t12-t11

                        if "day" in str(seconddaytdelta) or "days" in str(seconddaytdelta):
                            daystring = str(seconddaytdelta).split(",")[0]
                            noofdays = str(daystring).split(" ")[0]
                            daysmins = int(noofdays)*1440

                            thoursstr =  str(seconddaytdelta).split(",")[1]
                            thours = str(thoursstr).split(":")[0]
                            hrs = int(thours)*60
                            tmins = str(thoursstr).split(":")[1]
                            secondayfinalmins = int(hrs)+int(tmins)+int(daysmins)
                        else:
                            dthours = str(seconddaytdelta).split(":")[0]
                            dhrs = int(dthours)*60
                            dtmins = str(seconddaytdelta).split(":")[1]
                            secondayfinalmins = int(dhrs)+int(dtmins)

                        secondtimeport ={
                            "date":enddatestring,
                            "time":secondayfinalmins
                        }
                        seconddaylist.append(secondtimeport)

                    
                    finallist = protimelist+seconddaylist


            
                maindata = []
                for p in finallist:
                
                    v=stock_maindictlist("date", p['date'],"time",p['time'], maindata)
                    if v == {}:
                        timecalc={
                            "date":p['date'],
                            "time":p['time'],
                        }
                        maindata.append(timecalc)
                
                for m in maindata:
                    totalminutes = m['time']
                    hour = int (totalminutes)//60
                    if (len(str(hour)) < 2):
                        hours = "0"+str(hour)
                    else:
                        hours = str(hour)

                    mins = int (totalminutes) % 60
                    if (len(str(mins)) < 2):
                        minutes = "0"+str(mins)
                    else:
                        minutes = str(mins)

                    hourstring = str(hours)+" Hrs "+str(minutes)+" mins"

                    m['time'] = hourstring

                i['daywisetime']=maindata






                if i['Zone'] == 1:
                    i['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Green'><img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='Paris'></span>"

                if i['Zone'] == 2:
                    i['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Yellow'><img src='/static/Media/taskicons/activeyellowpoints.svg' class='activeicons' alt='Paris'></span>"

                if i['Zone'] == 3:
                    i['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Red'><img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='Paris' ></span>"

                if i['Zone'] == 4:
                    i['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Not Done'><img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='Paris'></span>"

                if i['Zone'] == 5:
                    i['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Cancelled'><img src='/static/Media/taskicons/activecancelledpoints.svg' class='activeicons' alt='Paris'></span>"

                if i['Zone'] == 6:
                    i['grade'] = "<span data-bs-toggle='tooltip' data-bs-placement='bottom' title='Rejected'><img src='/static/Media/taskicons/activerejectpoints.svg' class='activeicons' alt='Paris'></span>"

                if i['Zone'] == "" or h['Zone'] is None:
                    i['grade'] = "--"










            ########################################### project info ########################3333
            h['userprojecttaskdata'] = taskser.data
            h['count']= len(taskser.data)
            projecttotalminutes =projecthours
            phour = int (projecttotalminutes) // 60
            if (len(str(phour)) < 2):
                phours = "0"+str(phour)
            else:
                phours = str(phour)

            pmins = int (projecttotalminutes) % 60
            if (len(str(pmins)) < 2):
                pminutes = "0"+str(pmins)
            else:
                pminutes = str(pmins)

            h['projecthourstring'] = str(phours)+":"+str(pminutes)+" "+"Hrs"



        return Response({"n": 1, "Msg": "Data found successfully", "Status": "Success","count":len(searchobjser.data),"data":searchobjser.data}, status=status.HTTP_201_CREATED)        
    else:
        return Response({"n": 0, "Msg": "Data not found", "Status": "Success","data":""}, status=status.HTTP_201_CREATED)        

  


