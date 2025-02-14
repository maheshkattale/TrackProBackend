import datetime
from re import T
import pytz
import calendar
from Tasks.models import *
import psycopg2
from operator import itemgetter
from Rules.models import *
from Rules.serializers import *
from drf_multiple_model.views import ObjectMultipleModelAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery
from CheckTrackPro.serializers import IntermediateTrackProResult
from CheckTrackPro.serializers import IntermediateGetTrackProResultSerializer
from Users.models import Users
from TrackProBackend.settings import EMAIL_HOST_USER
from Users.serializers import UserSerializer,MappingSerializer
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from django.db.models.manager import Manager
from Users.models import UserToManager
from Tasks.serializers import GetTaskMasterSerializer,GetTaskMasterProjectTimeSerializer, YearSerializer, ZoneSerializer,WeekSerializer,GetTaskSerializer
from Tasks.models import TaskMaster, Zone,ProjectTasks
from Tasks.serializers import WeekSerializer,TaskMasterSerializer,PostTaskMasterSerializer,GetTaskScoreSerializer,ProjectTasksSerializer
from django.shortcuts import render
from .models import IntermediateTrackProResult
from .serializers import IntermediateGetTrackProResultSerializer, IntermediatePostTrackProResultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.http import JsonResponse
from datetime import datetime,timedelta
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import reduce
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
# DISPLAY IntermediateTrackProResult LIST----------------------------------------------------------------------------
import environ
from django.db.models import Avg
from django.utils import timezone



env = environ.Env()
environ.Env.read_env()

@api_view(['GET'])
def IntermediateTrackProResultList(request, format=None):
    if request.method == 'GET':
        dept = IntermediateTrackProResult.objects.all().order_by('TrackProPercent').reverse()
        serializer = IntermediateGetTrackProResultSerializer(dept, many=True)
        return Response(serializer.data)

# ADD IntermediateTrackProResult-------------------------------------------------------------------------------------


@api_view(['POST'])
def addIntermediateTrackProResult(request):
    user = request.user
    if user.is_admin == True:
        Employee = request.data['Employee']
        Week = request.data['Week']
        Year = request.data['Year']
        requestData = request.data.copy()
        requestData['company_code'] = request.user.company_code
        i = IntermediateTrackProResult.objects.filter(
            Employee=Employee, Week=Week, Year=Year)

        if i:
            return Response({"n": 0, "Msg": "TrackPro score for this employee/week has already been locked", "Status": "Failed"})
        try:
            serializer = IntermediatePostTrackProResultSerializer(
                data=requestData, context={'request': request})
        except Exception as e:
            return Response({'Error': 'serializer not accepting data'})
        else:
            if serializer.is_valid():
                serializer.validated_data['CreatedBy'] = user
                serializer.validated_data['EmpID'] = serializer.validated_data['Employee']
                data = {}
                u = serializer.save()

                data["n"] = '1'
                data["Msg"] = 'TrackPro Score added successfully'
                data["Status"] = 'Success'
            else:
                data = serializer.errors
            return Response(data)
    else:
        return Response({'Error': 'User has no permission to create'})

# DELETE IntermediateTrackProResult-------------------------------------------------------------------------------------


@api_view(['POST'])
def deleteIntermediateTrackProResult(request):
    data = {"n": 0, "Msg": "", "Status": ""}
    try:
        week = request.GET.get('week')
        userID = request.GET.get('userID')
        if week is not None and userID is not None:
            trackproresult = IntermediateTrackProResult.objects.filter(
                Week=week, Employee=userID)
            if trackproresult is None:
                data['n'] = 0
                data['Msg'] = 'trackpro RESULT DOES NOT EXIST'
                data['Status'] = "Failed"
            else:
                operation = trackproresult.delete()
                if operation:
                    data['n'] = 1
                    data['Msg'] = 'delete successfull'
                    data['Status'] = "Success"
                else:
                    data['n'] = 0
                    data['Msg'] = 'delete failed'
                    data['Status'] = "Failed"
        else:
            data['n'] = 0
            data['Msg'] = 'trackpro result is none'
            data['Status'] = "Failed"
    except Exception as e:
        data['n'] = 0
        data['Msg'] = 'try method failed'
        data['Status'] = "Failed"
    return Response(data=data)

# UPDATE IntermediateTrackProResult-------------------------------------------------------------------------------------


@api_view(['POST'])
def updateIntermediateTrackProResult(request):
    data = {'n': '', 'Msg': '', 'Status': ''}
    try:
        id = request.query_params.get('id')
        trackproresult = IntermediateTrackProResult.objects.get(id=id)
        if id is None:
            data['n'] = 0
            data['Msg'] = 'task ID is none'
            data['Status'] = "Failed"
        else:
            try:
                trackproresult = IntermediateTrackProResult.objects.get(id=id)
            except Exception as e:
                data['n'] = 0
                data['Msg'] = 'trackpro RESULT DOES NOT EXIST'
                data['Status'] = "Failed"
            else:
                requestData = request.data.copy()
                requestData['company_code'] = request.user.company_code
                serializer = IntermediatePostTrackProResultSerializer(
                    trackproresult, requestData)
                if serializer.is_valid():
                    # serializer.validated_data['UpdatedBy']  = request.task
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

# get object in IntermediateTrackProResult---------------------------------------------------------------------------------------------


@api_view(['GET'])
def getIntermediateTrackProResult(request):
    if request.method == 'GET':
        id = request.query_params.get('id', None)
        if id is not None:
            i = IntermediateTrackProResult.objects.filter(id=id)
            serializer = IntermediateGetTrackProResultSerializer(i, many=True)
            return JsonResponse(serializer.data, safe=False)

# check if trackpro result exists---------------------------------------------------------


@api_view(['POST'])
def CheckIfTrackProScoreExists(request):
    Employee = request.data['Employee']
    Week = request.data['Week']
    Year = request.data['Year']
   
    i = IntermediateTrackProResult.objects.filter(
        Employee=Employee, Week=Week, Year=Year)

    if i:
        return Response({"n": 0, "Msg": "TrackPro has already been checked for this week", "Status": "Failed"})
    else:
        return Response({"n": 1, "Msg": "TrackPro for this week has not been checked", "Status": "Success"})


@api_view(['POST'])
def trackproResultweekList(request, format=None):
    year = request.data.get('Year', None)
    userID = request.data.get('userID', None)
    if year is not None and userID is None:
        week = IntermediateTrackProResult.objects.filter(
            Year=year).order_by('Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)
        return Response(serializer.data)
    elif year is not None and userID is not None:
        week = IntermediateTrackProResult.objects.filter(
            Year=year, Employee=userID).order_by('Week').distinct('Week').reverse()
        serializer = WeekSerializer(week, many=True)
        return Response(serializer.data)
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "Year value is None"})

# three parameter trackpro data
# call on ajax


@api_view(['POST'])
def ThreeParamTrackProData(request, format=None):
    Employee = request.data.get('userID', None)
    year = request.data.get('Year', None)
    week = request.data.get('Week', None)
    if Employee is None or year is None or week is None:
        return Response({"n": 0, "Msg": "Missing Parameter", "Status": "Failed"})
    trackpro = IntermediateTrackProResult.objects.filter(
        Year=year, Employee=Employee, Week=week).order_by('Week').reverse()
    serializer = IntermediatePostTrackProResultSerializer(trackpro, many=True)
    return Response(serializer.data)


class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 1000


class ExcludeUserData(ObjectMultipleModelAPIView):
    pagination_class = LimitPagination

    def get_querylist(self):
        userID = self.request.query_params['userID']
        if UserToManager.objects.filter(ManagerID_id=userID):
            usertomanagerobject = UserToManager.objects.filter(ManagerID_id=userID).first()
            if usertomanagerobject.FixedMapping == False or usertomanagerobject.FixedMapping == "" or usertomanagerobject.FixedMapping is None:
                querylist = (
                    {'queryset': Users.objects.exclude(id=userID).order_by(
                        'Firstname'), 'serializer_class': UserSerializer},
                    {'queryset': TaskMaster.objects.exclude(AssignTo=userID).order_by(
                        'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
                    {'queryset': Zone.objects.all().order_by('id').reverse(),
                     'serializer_class': ZoneSerializer},
                    {'queryset': IntermediateTrackProResult.objects.exclude(
                        Employee=userID), 'serializer_class': IntermediateGetTrackProResultSerializer},
                    {'queryset': TaskMaster.objects.exclude(AssignTo=userID).values('Year').distinct(
                    ).order_by('Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
                      {'queryset': TaskMaster.objects.exclude(AssignTo=userID).values('Week').distinct(
                    ).order_by('Week').reverse(), 'serializer_class': WeekSerializer, 'label': 'Week'},
                )
                return querylist
            elif usertomanagerobject.FixedMapping == True:
                mapping = UserToManager.objects.filter(ManagerID_id=userID)
                querylist = (
                    {'queryset': Users.objects.filter(id__in=Subquery(mapping.values(
                        'UserID_id'))).order_by('Firstname'), 'serializer_class': UserSerializer},
                    {'queryset': TaskMaster.objects.exclude(AssignTo=userID).order_by(
                        'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
                    {'queryset': Zone.objects.all().order_by('id').reverse(),
                     'serializer_class': ZoneSerializer},
                    {'queryset': IntermediateTrackProResult.objects.exclude(
                        Employee=userID), 'serializer_class': IntermediateGetTrackProResultSerializer},
                    {'queryset': TaskMaster.objects.filter(AssignTo__in=Subquery(mapping.values('UserID_id'))).values(
                        'Year').distinct().order_by('Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
                    {'queryset': TaskMaster.objects.exclude(AssignTo=userID).values('Week').distinct(
                    ).order_by('Week').reverse(), 'serializer_class': WeekSerializer, 'label': 'Week'},
                )
                return querylist
           

        # those who are not mapped, write querylist here
        else:
            querylist = (
                {'queryset': Users.objects.exclude(id=userID).order_by(
                    'Firstname'), 'serializer_class': UserSerializer},
                {'queryset': TaskMaster.objects.exclude(AssignTo=userID).order_by(
                    'CreatedOn'), 'serializer_class': GetTaskMasterSerializer},
                {'queryset': Zone.objects.all().order_by('id').reverse(),
                 'serializer_class': ZoneSerializer},
                {'queryset': IntermediateTrackProResult.objects.exclude(
                    Employee=userID), 'serializer_class': IntermediateGetTrackProResultSerializer},
                {'queryset': TaskMaster.objects.exclude(AssignTo=userID).values('Year').distinct(
                ).order_by('Year').reverse(), 'serializer_class': YearSerializer, 'label': 'year'},
                 {'queryset': TaskMaster.objects.exclude(AssignTo=userID).values('Week').distinct(
                    ).order_by('Week').reverse(), 'serializer_class': WeekSerializer, 'label': 'Week'},
            )
            return querylist

@csrf_exempt
@api_view(["POST"])

def rank(request):
    selectedyear = int(request.data.get('Year', None))
    selectedweek = int(request.data.get('Week', None))

    previousweek = int(selectedweek)-1

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

    selectedweekstr = "(Week"+" "+str(selectedweek)+")"
    previousweekstr = "(Week"+" "+str(previousweek)+")"
    if selectedyear is None or selectedweek is None:
        return Response({"n": 0, "Msg": "Missing Parameter", "Status": "Failed"})
    else:
        selectedweekempobj = IntermediateTrackProResult.objects.filter(Year=selectedyear,Week=selectedweek).order_by('-TrackProPercent')
        if selectedweekempobj is not None:
            empobjserializer = IntermediateGetTrackProResultSerializer(selectedweekempobj,many=True)
            rankcount = 1
            for i in empobjserializer.data:
                empobj = IntermediateTrackProResult.objects.filter(id=i['id'],Year=selectedyear,Week=selectedweek).update(Rank=rankcount)
                rankcount += 1


            prevweekempobj =  IntermediateTrackProResult.objects.filter(Year=selectedyear,Week=previousweek).order_by('-TrackProPercent')
            if prevweekempobj is not None:
                prevempobjserializer = IntermediateGetTrackProResultSerializer(prevweekempobj,many=True)
                prevrankcount = 1
                for i in prevempobjserializer.data:
                    prevempobj = IntermediateTrackProResult.objects.filter(id=i['id'],Year=selectedyear,Week=previousweek).update(Rank=prevrankcount)
                    prevrankcount += 1


            

            employeeobj = IntermediateTrackProResult.objects.filter(Week=selectedweek,Year=selectedyear).order_by("Rank")
            empobjser = IntermediateGetTrackProResultSerializer(employeeobj,many=True)
            for p in empobjser.data:
                
                trackpropercentavg = IntermediateTrackProResult.objects.filter(Year=selectedyear,Employee=p['EmpID']).aggregate(Avg('TrackProPercent'))
                for k in [trackpropercentavg]:
                    trackpropercnt = k['TrackProPercent__avg']
                p['yearlytrackpropercnt'] = str(round(trackpropercnt,2))+"%"

                userobj = Users.objects.filter(id=p['EmpID']).first()
                p['userstr'] = userobj.Firstname + " " +  userobj.Lastname

                selectedweekrank = p['Rank']
                selectedweekpercent = p['TrackProPercent']
                if selectedweekpercent is not None:
                    p['TrackProPercent'] = str(selectedweekpercent) + "%"


                prevempobj = IntermediateTrackProResult.objects.filter(Employee=p['EmpID'],Week=previousweek,Year=selectedyear).first()
                if prevempobj is not None:
                    prevweekrank = prevempobj.Rank
                    p['prevweekrank'] = prevempobj.Rank
                    prevweekpercent =  prevempobj.TrackProPercent
                    if prevweekpercent is not None:
                        p['prevweekpercent'] = str(prevweekpercent) + "%"

                    rankdiff = prevweekrank - selectedweekrank
                    p['Rank_diff']=rankdiff
                    if rankdiff > 0:
                        p['Rank_diffstr'] = "<i class='fa fa-caret-up' style='color:green'></i> <span style='color:green'>+ "+str(p['Rank_diff'])+"</span>"
                     
                    elif rankdiff < 0 :
                        p['Rank_diffstr'] = "<i class='fa fa-caret-down' style='color:red'></i> <span style='color:red'> "+str(p['Rank_diff'])+"</span>"

                    else:
                        p['Rank_diffstr'] = "<i class='fa fa-circle' style='color:blue;font-size:10px;'></i> <span style='color:blue'>"+str(p['Rank_diff'])+"</span>"
                     
                       
                else:
                    p['prevweekrank'] = "--"
                    p['prevweekpercent'] = "--"
                    p['Rank_diff'] = "--"
                    p['Rank_diffstr']= "--"


                greenmarks = p['Green']
                if greenmarks > 0 :
                    p['greencount'] = int(greenmarks)//greencountmultiple
                else:
                    p['greencount'] = 00

                yellowmarks = p['Yellow'] 
                if yellowmarks > 0 :
                    p['yellowcount'] = int(yellowmarks)//yellowcountmultiple
                else:
                    p['yellowcount'] = 00

                redmarks = p['Red'] 
                if redmarks > 0 :
                    p['redcount'] = int(redmarks)//redcountmultiple
                else:
                    p['redcount'] = 00

                notdonemarks = p['NotDone'] 
                if notdonemarks > 0 :
                    p['notdonecount'] = int(notdonemarks)//notdonecountmultiple
                else:
                    p['notdonecount'] = 00

                cancelmarks = p['Cancelled'] 
                if cancelmarks > 0 :
                    p['cancelcount'] = int(cancelmarks)
                else:
                    p['cancelcount'] = 00

                rejectmarks = p['Rejected'] 
                if rejectmarks > 0 :
                    p['rejectcount'] = int(rejectmarks)//rejectcountmultiple
                else:
                    p['rejectcount'] = 00

                bonusmarks = p['Bonus'] 
                if bonusmarks > 0 :
                    p['Bonuscount'] = int(bonusmarks)//bonuscountmultiple
                else:
                    p['Bonuscount'] = 00

                creditmarks = p['extra_credit'] 
                if creditmarks:
                    if creditmarks > 0 :
                        p['creditcount'] = int(creditmarks)//greencountmultiple
                    else:
                        p['creditcount'] = 00
                    
                if p['DepartmentwiseRank'] is None:
                    p['DepartmentwiseRank']="--"

            context={
                'selectedweek':selectedweekstr,
                'prevweek':previousweekstr
            }  

            return Response({"data":empobjser.data,"context":context,"n": 1, "Msg": "ranks for this week  published", "Status": "success"})

        else:
            return Response({"data":'',"n": 0, "Msg": "ranks for this week not published", "Status": "failure"})


@api_view(['POST'])
def Getemployeerankinfo(request):
    selectedyear = int(request.data.get('Year', None))
    selectedweek = int(request.data.get('Week', None))
    selectedemp = request.POST.get('employee')
    previousweek = int(selectedweek)-1

    selectedweekstr = "(Week"+" "+str(selectedweek)+")"
    previousweekstr = "(Week"+" "+str(previousweek)+")"

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
    
    if selectedyear is None or selectedweek is None:
        return Response({"n": 0, "Msg": "Missing Parameter", "Status": "Failed"})
    else:
        if selectedemp is None or selectedemp == "":
            employeeobj = TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear).distinct('AssignTo')
        else:
            employeeobj =TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=selectedemp).distinct('AssignTo')

        if employeeobj is not None:
            empobjser = GetTaskSerializer(employeeobj,many=True)
            for p in empobjser.data:
                p['selectedweek'] = "Week"+" "+str(selectedweek)
                p['previousweek'] = "Week"+" "+str(previousweek)

                userobj = Users.objects.filter(id=p['AssignTo']).first()
                p['userstr'] = userobj.Firstname + " " +  userobj.Lastname

                trackpropercentavg = IntermediateTrackProResult.objects.filter(Year=selectedyear,Employee=p['AssignTo']).aggregate(Avg('TrackProPercent'))

                for k in [trackpropercentavg]:
                    if k['TrackProPercent__avg'] is not None:
                        trackpropercnt = k['TrackProPercent__avg']
                        p['yearlytrackpropercnt'] = str(round(trackpropercnt,2))+"%"
                    else:
                        p['yearlytrackpropercnt'] = "--"

                empexistinInt = IntermediateTrackProResult.objects.filter(Year=selectedyear,Week=selectedweek,Employee=p['AssignTo']).first()
                
                if empexistinInt is not None:

                    selectedweektrackpropercent = empexistinInt.TrackProPercent
                    if selectedweektrackpropercent is not None:
                        p['TrackProPercent'] = str(selectedweektrackpropercent) + "%"
                    p['TotalScore'] = empexistinInt.TotalScore
                    p['TrackProScore'] = empexistinInt.TrackProScore
                    selectedweekrank =  empexistinInt.Rank
                    


                    prevempobj = IntermediateTrackProResult.objects.filter(Employee=p['AssignTo'],Week=previousweek,Year=selectedyear).first()

                    if prevempobj is not None:
                        prevweekrank = prevempobj.Rank
                        p['prevweekrank'] = prevempobj.Rank
                        prevweektrackpropercent =  prevempobj.TrackProPercent
                        p['prevweekpercent'] = str(prevweektrackpropercent) + "%"
                        if p['prevweekrank'] is not None and selectedweekrank is not None:
                            rankdiff = int(p['prevweekrank']) - int(selectedweekrank)
                            p['Rank_diff']=rankdiff
                            if rankdiff > 0:
                                p['Rank_diffstr'] = "<i class='fa fa-caret-up' style='color:green'></i> <span style='color:green'>+ "+str(p['Rank_diff'])+"</span>"
                            
                            elif rankdiff < 0 :
                                p['Rank_diffstr'] = "<i class='fa fa-caret-down' style='color:red'></i> <span style='color:red'> "+str(p['Rank_diff'])+"</span>"

                            else:
                                p['Rank_diffstr'] = "<i class='fa fa-circle' style='color:blue;font-size:10px;'></i> <span style='color:blue'>"+str(p['Rank_diff'])+"</span>"
                                
                        else:
                            p['Rank_diff'] = "--"
                            p['Rank_diffstr']= ""

                    else:
                        p['prevweekrank'] = "--"
                        p['prevweekpercent'] = "--"
                        p['Rank_diff'] = "--"
                        p['Rank_diffstr']= ""

                    if selectedweekrank is not None:
                        p['Rank'] = selectedweekrank
                        p['listingrank'] = int(selectedweekrank)
                    else:
                        p['Rank'] = "--"
                        p['listingrank'] = 0

                    greenmarks = empexistinInt.Green
                    if greenmarks > 0 :
                        p['greencount'] = int(greenmarks)//greencountmultiple
                    else:
                        p['greencount'] = 00

                    yellowmarks = empexistinInt.Yellow
                    if yellowmarks > 0 :
                        p['yellowcount'] = int(yellowmarks)//yellowcountmultiple
                    else:
                        p['yellowcount'] = 00

                    redmarks =  empexistinInt.Red
                    if redmarks > 0 :
                        p['redcount'] = int(redmarks)//redcountmultiple
                    else:
                        p['redcount'] = 00

                    notdonemarks =  empexistinInt.NotDone 
                    if notdonemarks > 0 :
                        p['notdonecount'] = int(notdonemarks)//notdonecountmultiple
                    else:
                        p['notdonecount'] = 00

                    cancelmarks = empexistinInt.Cancelled 
                    if cancelmarks > 0 :
                        p['cancelcount'] = int(cancelmarks)
                    else:
                        p['cancelcount'] = 00

                    rejectmarks = empexistinInt.Rejected
                    if rejectmarks > 0 :
                        p['rejectcount'] = int(rejectmarks)//rejectcountmultiple
                    else:
                        p['rejectcount'] = 00

                    bonusmarks = empexistinInt.Bonus 
                    if bonusmarks > 0 :
                        p['Bonuscount'] = int(bonusmarks)//bonuscountmultiple
                    else:
                        p['Bonuscount'] = 00

                    if empexistinInt.extra_credit is not None:
                        creditmarks =  empexistinInt.extra_credit
                        if creditmarks > 0 :
                            p['creditcount'] = int(creditmarks)//greencountmultiple
                        else:
                            p['creditcount'] = 00
                    else:
                        p['creditcount'] = 00

                    p['in_Intermediate']= "Present"

                else:
                    prevempobj = IntermediateTrackProResult.objects.filter(Employee=p['AssignTo'],Week=previousweek,Year=selectedyear).first()
                    if prevempobj is not None:
                        prevweekrank = prevempobj.Rank
                        if prevweekrank is not None:
                            p['prevweekrank'] = prevweekrank
                        else:
                            p['prevweekrank'] = '--'

                        prevweektrackprotaskpercent = prevempobj.TrackProPercent
                        if prevweektrackprotaskpercent is not None:
                            p['prevweekpercent'] = str(prevweektrackprotaskpercent) + "%"
                       

                    else:
                        p['prevweekrank'] = "--"
                        p['prevweekpercent'] = "--"

                    p['Rank_diff']= "--"
                    p['Rank_diffstr']= ""

                    p['greencount'] = TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Zone=1).count()

                    p['yellowcount'] = TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Zone=2).count()
                   
                    p['redcount'] = TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Zone=3).count()
                   
                    p['notdonecount'] =  TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Zone=4).count()
                    
                    p['cancelcount'] = TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Zone=5).count()
                   
                    p['rejectcount'] =  TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Zone=6).count()

                    p['Bonuscount'] =TaskMaster.objects.filter(Week=selectedweek,Year=selectedyear,AssignTo=p['AssignTo'],Bonus=True).count()

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


                    p['in_Intermediate']= "Absent"
                    p['TrackProPercent'] = "--"
                    p['TotalScore'] = "--"
                    p['TrackProScore'] = "--"
                    p['Rank'] = "--"
                    p['listingrank'] = 0

            sortlist = empobjser.data
            newlist = sorted(sortlist, key=itemgetter('listingrank'))

            context={
                'selectedweek':selectedweekstr,
                'prevweek':previousweekstr
            }   

            return Response({"data":newlist,"context":context,"n": 1, "Msg": "Data found successfully", "Status": "success"})

        else:
            return Response({"data":'',"n": 0, "Msg": "Data not found", "Status": "failure"})


           
    




@api_view(['POST'])
def lastFive(request):
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    week = week_num
    year_num = year
    if year_num is not None and week is not None:
        last = IntermediateTrackProResult.objects.filter(
            Year=year_num, Week=week).order_by('TrackProPercent')[:5]
        serializer = IntermediateGetTrackProResultSerializer(last, many=True)
        return Response(serializer.data)
    else:
        return Response({"n": 0, "Msg": "Failed", "Status": "no data found"})


def convertMinute(seconds):
    conMin= "0." + str(seconds)
    convertMin = float(conMin)
    if convertMin == None:
        convertMin = 0
    minutes = round((float(convertMin) * 60),2)
    return minutes 

def convert(seconds):
    if seconds == None:
        seconds = 0
    seconds = seconds % (24 * 3600)
    
    hour = round((seconds / 3600),2)
    seconds %= 3600
    minutes = round((seconds // 60),2)
    seconds %= 60

    return hour

def read_employee_task_detail(employee_id,project):
    try:
        conn = psycopg2.connect(database=env('DATABASE_NAME'), user= env('DATABASE_USER'),
                                    password=env('DATABASE_PASSWORD'), host=env('DATABASE_HOST'), port=env('DATABASE_PORT'), cursor_factory=RealDictCursor)
        cur = conn.cursor()
    except Exception as e:
        return Response({"n": 0, "Msg": "Could not connect to database", "Status": "Failed"})
    else:
        query = f"""SELECT u."id", td."StartDate", td."EndDate",tk."TaskTitle", EXTRACT(EPOCH FROM (COALESCE(td.   "EndDate", Current_timestamp) - td."StartDate"))
                    FROM "Users_users" as u
                    LEFT JOIN "Tasks_taskmaster" as tk on tk."AssignTo_id" = u."id"
                    LEFT JOIN "Tasks_projecttasks" as td on td."Task_id" = tk."id" WHERE tk."AssignTo_id"={employee_id} and tk."Project_id"={project} and td."StartDate" IS NOT NULL;"""
        cur.execute(query)
        report = cur.fetchall()
        total_hrs = 0
        for i in report:  
            total_hrs = total_hrs + convert(i["extract"])
            workedHours = convert(i["extract"])  
            i["hours"] = float(str(workedHours).split('.')[0])
            i['minutes'] = convertMinute(str(workedHours).split('.')[1])          
                
        return report, total_hrs


@api_view(['POST'])
def report_by_project_name_three_tier(request):
    projectName = request.POST.get('projectName')
    try:
        conn = psycopg2.connect(database=env('DATABASE_NAME'), user= env('DATABASE_USER'),
                                    password=env('DATABASE_PASSWORD'), host=env('DATABASE_HOST'), port=env('DATABASE_PORT'), cursor_factory=RealDictCursor)
        cur = conn.cursor()
    except Exception as e:
        return Response({"n": 0, "Msg": "Could not connect to database", "Status": "Failed"})
    else:
        query = f"""SELECT DISTINCT
                    u."id",u."Firstname",u."Lastname", pm."ProjectName", pm."CreatedOn" ,tk."Project_id"
                    FROM "Users_users" as u 
                    LEFT JOIN "Tasks_taskmaster" as tk on tk."AssignTo_id" = u."id"
                    LEFT JOIN "Tasks_projecttasks" as td on td."Task_id" = tk."id"
                    LEFT JOIN "Project_projectmaster" as pm on tk."Project_id" = pm."id"
                    where u."is_active" = 'True' and u."is_admin" = 'True' and tk."ProjectName"='{projectName}';"""

        cur.execute(query)

        report = cur.fetchall()
        projectEndDateString = datetime.datetime.now()
        projectEndDate = str(projectEndDateString).split(" ")[0]
        reportStartDateString = report[0]['CreatedOn']
        projectStartDate = str(reportStartDateString).split(" ")[0]
        date_format = "%Y-%m-%d"
        a = datetime.datetime.strptime(str(projectStartDate), date_format)
        b = datetime.datetime.strptime(str(projectEndDate), date_format)
        delta = b - a
        project_details = {
            "project_name": "",
            "project_created_at": "",
            "project_total_hrs": 0,
            "project_employee":"",
            "project_total_days":"",
        }

        employe_detail_list = []
        employe_detail = {}
        employeeCount = 0
        for i in report:
            employeeCount +=1
            project_details["project_name"] = i["ProjectName"]
            project_details["project_created_at"] = i["CreatedOn"]
            project_details["project_employee"] = employeeCount
            project_details["project_total_days"] = delta.days
            data, hrs = read_employee_task_detail(i["id"],i['Project_id'])
            project_details["project_total_hrs"] = project_details["project_total_hrs"] + hrs
            employe_detail["id"] = i["id"]
            employe_detail["first_name"] = i["Firstname"]
            employe_detail["last_name"] = i["Lastname"]
            employe_detail["total_hours"] = hrs
            employe_detail["hours_distribution"] = data
            employe_detail_list.append(employe_detail.copy())
            employe_detail.clear()
    return Response({"project_details": project_details, "employee_hour_details": employe_detail_list})









@api_view(['POST'])
def getTask(request):
    repeatYear=[]
    uniqueYear=[]
    Year=request.data.get('Year')
    Week=request.data.get('Week')
    Employee=request.data.get('Employee')   
    zoneObject=Zone.objects.all().order_by('-id')
    ZoneSer=ZoneSerializer(zoneObject,many=True)
    taskObject=TaskMaster.objects.filter(Year=Year,Week=Week,CreatedBy=Employee)
    ser=PostTaskMasterSerializer(taskObject,many=True)
    for i in ser.data:
        userObject=Users.objects.filter(id=i['CreatedBy'],is_blocked=False).first()
        i['CreatedBy']=userObject.Firstname+" "+userObject.Lastname
        repeatYear.append(i['Year'])
    for year in repeatYear:
        if year not in uniqueYear:
            uniqueYear.append(year)
    return Response({'n':1,"status":"success","message":"data found successfully","Taskdata":ser.data,"zone":ZoneSer.data,"uniqueYear":uniqueYear})

@api_view(['POST'])
def getParticualrEmployeeTask(request):
    repeatYear=[] 
    uniqueYear=[] 
    Year=request.data.get('Year') 
    Week=request.data.get('Week')
    Employee=request.data.get('Employee')
    AssignBy = request.data.get('AssignBy')   
    zoneObject=Zone.objects.all().order_by('-id')
    ZoneSer=ZoneSerializer(zoneObject,many=True)
    if AssignBy is not None and AssignBy != "" and AssignBy != "Select Supervisor":
        taskObject=TaskMaster.objects.filter(Year=Year,Week=Week,AssignTo=Employee,AssignBy=AssignBy).order_by('CreatedOn')
    else:
        taskObject=TaskMaster.objects.filter(Year=Year,Week=Week,AssignTo=Employee).order_by('CreatedOn')

    othertaskObject=TaskMaster.objects.filter(Year=Year,Week=Week,AssignTo=Employee).order_by('CreatedOn')
    if othertaskObject is not None:
        otherser = PostTaskMasterSerializer(othertaskObject,many=True)

    if taskObject is not None:
        ser=PostTaskMasterSerializer(taskObject,many=True)
        totalalltaskhours = 0
        for i in ser.data:
           
            checkby = i['CheckedBy']
            if checkby is not None and checkby != "":
                checkbyobj = Users.objects.filter(id=checkby).first()
                if checkbyobj is not None:
                    i['CheckedBy'] = checkbyobj.Firstname + " " + checkbyobj.Lastname
                else:
                    i['CheckedBy'] = "--"
            else:
                i['CheckedBy'] = "--"

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

            userObject=Users.objects.filter(id=i['AssignTo']).first()
            i['CreatedBy']=userObject.Firstname+" "+userObject.Lastname
            repeatYear.append(i['Year'])

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
                    totalalltaskhours += m['time']
                   
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

            hovertaskidlist = []
            if taskobj.ParentTaskId is not None:
                hovertaskparentid = taskobj.ParentTaskId
                hovertaskidlist.append(hovertaskparentid)
                ttaskobject = TaskMaster.objects.filter(ParentTaskId=hovertaskparentid).exclude(id=i['id'])
                ttaskser = PostTaskMasterSerializer(ttaskobject,many=True)
                for t in ttaskser.data:
                    hovertaskidlist.append(t['id'])

                hoverobjects = TaskMaster.objects.filter(id__in=hovertaskidlist)
                hovertaskser = PostTaskMasterSerializer(hoverobjects,many=True)
                for h in hovertaskser.data:

                    chdate = str(h['AssignDate'])
                    h['Changeddate'] = chdate.split('-')[2] + "-" + chdate.split('-')[1] + "-" + chdate.split  ('-')[0]

                    hprojecttasktime = ProjectTasks.objects.filter(Task__in=taskidlist).order_by("id")
                    if hprojecttasktime :
                        hprojectser = ProjectTasksSerializer(hprojecttasktime,many=True)
                        FMT = '%H:%M:%S.%f'
                        htotaltime=0
                        for o in hprojectser.data:
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
                                hfinalmins = int(hrs)+int(tmins)
                            htotaltime += hfinalmins

                        htotalhours =htotaltime
                        hhour = int (htotalhours) // 60
                        if (len(str(hhour)) < 2):
                            rhhours = "0"+str(hhour)
                        else:
                            rhhours = str(hhour)

                        hmins = int (htotalhours) % 60
                        if (len(str(hmins)) < 2):
                            rminutes = "0"+str(hmins)
                        else:
                            rminutes = str(hmins)

                        rhourstring = str(rhhours)+":"+str(rminutes)+" "+"Hrs"

                        h['taskhoursstr'] = rhourstring

                    remarkzone = h['Zone']
                    if remarkzone == 1:
                        h['remarkstr'] = "<img src='/static/Media/taskicons/activegreenpoints.svg' class='activeicons' alt='green'>"
                    elif remarkzone == 2:
                        h['remarkstr'] = "<img src='/static/Media/taskicons/activeyellowsvgpoints.svg' class='activeicons' alt='yellow'>"
                    elif remarkzone == 3:
                        h['remarkstr'] = "<img src='/static/Media/taskicons/activeredpoints.svg' class='activeicons' alt='red'>"
                    elif remarkzone == 4:
                        h['remarkstr'] = "<img src='/static/Media/taskicons/activenotdonepoints.svg' class='activeicons' alt='notdone'>"
                    elif remarkzone == 5:
                        h['remarkstr'] = "<img src='/static/Media/taskicons/activecancelledpoints.svg' class='activeicons' alt='notdone'>"
                    elif remarkzone == 6:
                        h['remarkstr'] = "<img src='/static/Media/taskicons/activerejectpoints.svg' class='activeicons' alt='notdone'>"
                    else:
                        h['remarkstr'] = "----"


                    bonusstr = h['Bonus']
                    if bonusstr == True:
                        h['bonusstr'] = "<img src='/static/Media/taskicons/activebonuspoints.svg' alt='bonus'>"
                    else:
                        h['bonusstr'] = ""

                i['Hovertaskdata']  = hovertaskser.data
            else:
                i['Hovertaskdata'] = []


            if i['ParentTaskId'] is None:
                    i['ParentTaskId'] = ""


           
        tt_hour = int (totalalltaskhours //60)
        if (len(str(tt_hour)) < 2):
            tt_hours = "0"+str(tt_hour)
        else:
            tt_hours = str(tt_hour)

        tt_mins = int (totalalltaskhours % 60)
        if (len(str(tt_mins)) < 2):
            tt_minutes = "0"+str(tt_mins)
        else:
            tt_minutes = str(tt_mins)

        tt_hourstring = str(tt_hours)+" Hrs "+str(tt_minutes)+" mins"
        
        
        for year in repeatYear:
            if year not in uniqueYear:
                uniqueYear.append(year)

    return Response({'n':1,"status":"success","message":"data found successfully","Taskdata":ser.data,"zone":ZoneSer.data,"uniqueYear":uniqueYear,'othermanagerser':otherser.data,'totaltaskhours':tt_hourstring})


def stock_maindictlist(key, value ,qtykey,qty, my_dictlist):
    if my_dictlist !=[]:
        for entry in my_dictlist:
            if entry[key] == value:
                entry[qtykey] = entry['time'] + qty
                return entry
        return {}
    return {}


@api_view(['POST'])
def getYear(request):
    uniqueWeek=[]
    week=[]
    Year=request.data.get('Year')
    Employee=request.data.get('Employee')
    YearObject=TaskMaster.objects.filter(Year=Year,CreatedBy=Employee)
    ser=TaskMasterSerializer(YearObject,many=True)
    for i in ser.data:
        week.append(i['Week'])
    for rweek in week:
        if rweek not in uniqueWeek:
            uniqueWeek.append(rweek)
            uniqueWeek.sort(reverse=True)
    return Response({'n':1,"status":"success","message":"data found successfully","uniqueWeek":uniqueWeek})


@api_view(['POST'])
def getlasttask(request):
    repeatWeek=[]
    repeatYear=[]
    uniqueYear=[]
    uniqueWeek=[]
    employee=request.data.get('employee')
    assignBylist = []
    year=request.data.get('year')
    taskObject=TaskMaster.objects.filter(AssignTo=employee)
    ser=TaskMasterSerializer(taskObject,many=True)
    if year is not None:
        taskObject=TaskMaster.objects.filter(AssignTo=employee,Year=year)
        ser=TaskMasterSerializer(taskObject,many=True)
    for i in ser.data:
        assignSet = {
            'AssignBy' : i['AssignBy'],
            'AssignByStr' : i['AssignByStr']
        }
        assignBylist.append(assignSet)
        repeatYear.append(i['Year'])
        repeatWeek.append(i['Week'])
    pop = [dict(t) for t in {tuple(d.items()) for d in assignBylist}]
    assignBysetlist = pop
    for year in repeatYear:
        if year not in uniqueYear:
            uniqueYear.append(year)
            uniqueYear.sort(reverse=True)
    for week in repeatWeek:
        if week not in uniqueWeek:
            uniqueWeek.append(week)
            uniqueWeek.sort(reverse=True)
    return Response({'n':1,"status":"success","message":"data found successfully","Taskdata":ser.data,"uniqueYear":uniqueYear,"uniqueWeek":uniqueWeek,"assignBysetlist":assignBysetlist})

@api_view(['POST'])
def getemployeelasttask(request):
    repeatWeek=[]
    repeatYear=[]
    uniqueYear=[]
    uniqueWeek=[]
    employee=request.data.get('employee')
    year=request.data.get('year')
    assignedBy = request.data.get('assignedBy')
    taskObject=TaskMaster.objects.filter(CreatedBy=employee,AssignBy=assignedBy)
    ser=TaskMasterSerializer(taskObject,many=True)
    if year is not None:
        taskObject=TaskMaster.objects.filter(CreatedBy=employee,Year=year,AssignBy=assignedBy)
        ser=TaskMasterSerializer(taskObject,many=True)
    for i in ser.data:
        repeatYear.append(i['Year'])
        repeatWeek.append(i['Week'])
    for year in repeatYear:
        if year not in uniqueYear:
            uniqueYear.append(year)
            uniqueYear.sort(reverse=True)
    for week in repeatWeek:
        if week not in uniqueWeek:
            uniqueWeek.append(week)
            uniqueWeek.sort(reverse=True)
    return Response({'n':1,"status":"success","message":"data found successfully","Taskdata":ser.data,"uniqueYear":uniqueYear,"uniqueWeek":uniqueWeek})

@api_view(['POST'])
def getScore(request):
    week=request.data.get('Week')
    Employee=request.data.get('Employee')
    scoreObject=IntermediateTrackProResult.objects.filter(Week=week,Employee=Employee).first()
    if scoreObject is not None:
        Ser=IntermediateGetTrackProResultSerializer(scoreObject)
        return Response({'n':1,"status":"success","message":"data found successfully","data":Ser.data})
    return Response({'n':0,"status":"failed","message":"data not found"})


# @api_view(['POST'])
# def get_trackpro_percentege_by_empid(request):
#     Employee=request.data.get('Employee')
#     Percentage_Object=IntermediateTrackProResult.objects.filter(Employee=Employee).order_by('Week','Year')
#     if Percentage_Object is not None:
#         Ser=IntermediateGetTrackProResultSerializer(Percentage_Object,many=True)
#         return Response({'n':1,"status":"success","message":"data found successfully","data":Ser.data})
#     return Response({'n':0,"status":"failed","message":"data not found",'data':{}})


@api_view(['POST'])
def getTaskScore(request):
    taskZoneList =[]
    GreenZoneTask = 0
    YellowZoneTask = 0
    RedZoneTask = 0
    NotdoneZoneTask = 0
    bonus = 0
    cancelledZoneTask=0
    rejectedZoneTask=0

    getTaskScoretaskpointsper = 0
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

    year=request.data.get('Year')
    week=request.data.get('Week')
    Employee=request.data.get('Employee')
    AssignedBy = request.data.get('AssignBy')
    final_submit = ""
    scoreObject=IntermediateTrackProResult.objects.filter(Year=year,Week=week,Employee=Employee).first()
    if scoreObject is not None:
        final_submit = "Yes"
    else:
        final_submit = "No"
    scoreObjectCount = TaskMaster.objects.filter(Week=week,Year=year,AssignTo=Employee).count()
    scoreObject=TaskMaster.objects.filter(Week=week,Year=year,AssignTo=Employee)
    if scoreObject is not None:
        Ser=GetTaskScoreSerializer(scoreObject,many=True)
        for i in Ser.data:
            taskZoneList.append(i['Zone'])
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
        ZoneNoneList = ""  
        if None in taskZoneList: 
            ZoneNoneList = "None"
        totalTrackProScore = (GreenZoneTask + YellowZoneTask + RedZoneTask  + bonus) - (NotdoneZoneTask + rejectedZoneTask)
        totalScore = (scoreObjectCount-cancelledZoneTask) * greencountmultiple
        trackpropercentcal = (100 * (((GreenZoneTask + YellowZoneTask + RedZoneTask + bonus) - (NotdoneZoneTask + rejectedZoneTask)) / totalScore))
        trackpropercent = round(trackpropercentcal, 2)
        ScoreDict = {
            'GreenZoneTask':GreenZoneTask,
            'YellowZoneTask':YellowZoneTask,
            'RedZoneTask':RedZoneTask,
            'NotdoneZoneTask':NotdoneZoneTask,
            'cancelledZoneTask':cancelledZoneTask,
            'rejectedZoneTask':rejectedZoneTask,
            'bonus':bonus,
            'totalTrackProScore':totalTrackProScore,
            'ZoneNoneList':ZoneNoneList,
            'scoreObjectCount':scoreObjectCount,
            'trackpropercent':trackpropercent,
            'TotalScore':totalScore
        } 
        return Response({'n':1,"status":"success","message":"data found successfully","data":Ser.data,'score':ScoreDict,"final_submit":final_submit})
    return Response({'n':0,"status":"failed","message":"data not found"})


@api_view(['POST'])
def addParticualrIntermediateTrackProResult(request):
    users = request.user.id
    GreenZoneTask = 0
    YellowZoneTask = 0
    RedZoneTask = 0
    NotdoneZoneTask = 0
    bonus = 0
    cancelledZoneTask=0
    rejectedZoneTask=0
    extracredits=0

    taskpointsper = 0
    greencountmultiple = 0
    yellowcountmultiple = 0
    redcountmultiple = 0
    notdonecountmultiple = 0
    rejectcountmultiple = 0
    bonuscountmultiple = 0

    Employee = request.data['Employee']
    Week = request.data['Week']
    Year = request.data['Year']
    requestData = request.data.copy()
    requestData['company_code'] = request.user.company_code
    scoreObjectCount = TaskMaster.objects.filter(Week=Week,Year=Year,AssignTo=Employee).count()
    scoreObject=TaskMaster.objects.filter(Week=Week,Year=Year,AssignTo=Employee)

    trackprorules = rulestrackpro.objects.filter(is_active=True,company_code=requestData['company_code'])
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

    if scoreObject is not None:
        Ser=GetTaskScoreSerializer(scoreObject,many=True)
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
        totalScore = (scoreObjectCount-cancelledZoneTask) * taskpointsper 
        trackpropercentcal = (100 * (((GreenZoneTask + YellowZoneTask + RedZoneTask + bonus + extracredits) - (NotdoneZoneTask + rejectedZoneTask)) / totalScore))
        trackpropercent = round(trackpropercentcal, 2)
        requestData['Green'] = GreenZoneTask
        requestData['Yellow'] = YellowZoneTask
        requestData['Red'] = RedZoneTask
        requestData['NotDone'] = NotdoneZoneTask
        requestData['Cancelled'] = cancelledZoneTask
        requestData['Rejected'] = rejectedZoneTask
        requestData['Bonus'] = bonus
        requestData['extra_credit']=extracredits
        requestData["TotalScore"] = totalScore
        requestData["TrackProScore"] = totalTrackProScore
        requestData["TrackProPercent"] = trackpropercent
        requestData["TotalTask"] = scoreObjectCount
        requestData["CreatedBy"] = users

        i = IntermediateTrackProResult.objects.filter(
            Employee=Employee, Week=Week, Year=Year)

        if i:
            return Response({"n": 0, "Msg": "TrackPro score for this employee/week has already been locked", "Status": "Failed"})
        try:
            serializer = IntermediatePostTrackProResultSerializer(
                data=requestData, context={'request': request})
        except Exception as e:
            return Response({'Error': 'serializexr not accepting data'})
        else:
            if serializer.is_valid():
                serializer.validated_data['EmpID'] = serializer.validated_data['Employee']
                data = {}
                u = serializer.save()

                data["n"] = '1'
                data["Msg"] = 'TrackPro Score added successfully'
                data["Status"] = 'Success'
            else:
                data = serializer.errors
            return Response(data)
    

@api_view(['POST'])
def getTaskSubmit(request):
    taskZoneList = []
    ZoneNoneList = ""
    year=request.data.get('Year')
    week=request.data.get('Week')
    Employee=request.data.get('Employee')
    scoreObject=TaskMaster.objects.filter(Week=week,Year=year,AssignTo=Employee)
    if scoreObject is not None:
        Ser=GetTaskScoreSerializer(scoreObject,many=True)
        for i in Ser.data:
            taskZoneList.append(i['Zone'])
        if None not in taskZoneList:
            ZoneNoneList = "None"
            return Response({'n':1,"status":"success","message":"data found successfully","data":Ser.data})
        return Response({'n':0,"status":"failed","message":"data not found"})
    return Response({'n':0,"status":"failed","message":"data not found"})


@api_view(['POST'])
def getAllZone(request):
    zoneObject=Zone.objects.all()
    zoneSer=ZoneNameSerializer(zoneObject,many=True)
    return Response({'n':1,"status":"success","message":"data found successfully","data":zoneSer.data})


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def trackprocheck_managerscheduler(request):
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    currweek = week_num
    manageridlist=[]
    yearlist=[]
    company_code = "O001"
    # manageridlist= list(TaskMaster.objects.filter(company_code=company_code).distinct('AssignBy').values_list('AssignBy', flat=True))
   
    taskobj = TaskMaster.objects.filter(company_code=company_code).distinct('AssignBy')
    taskmgser = TaskMasterSerializer(taskobj,many=True)
    for t in taskmgser.data:
        manageridlist.append(t['AssignBy'])
    
    # yearlist = list(TaskMaster.objects.filter(company_code=company_code).distinct('Year').order_by('Year').values_list('Year', flat=True))
   
    yearobj = TaskMaster.objects.filter(company_code=company_code).distinct('Year').order_by('Year')
    yearmgser = TaskMasterSerializer(yearobj,many=True)
    for o in yearmgser.data:
        yearlist.append(o['Year'])
    managerlist = []
    for m in manageridlist:
        managerdict = {}
        weeklydatalist=[]
        uncheckbym_count = 0
        allunheckedemplist = []
        for y in yearlist:
            weeklist=[]
            weekobj = TaskMaster.objects.filter(Year=y,AssignBy=m).distinct('Week').order_by('Week')
            if weekobj is not None:
                weekser = TaskMasterSerializer(weekobj,many=True)
                for w in weekser.data:
                    weeklist.append(w['Week'])
                
                if currweek in weeklist:
                    weeklist.remove(currweek)

                for s in weeklist:
                    uncheckedinweek = 0
                    weeklyempcount = 0
                    totalmanagerweektask = 0
                    weekdict = {}

                    empdatalist=[]
                    empobj = TaskMaster.objects.filter(Year=y,AssignBy=m,Week=s).distinct('AssignTo').order_by('AssignTo')
                    taskempser = GetTaskSerializer(empobj,many=True)

                    for i in taskempser.data:
                        empdata={}

                        alltaskobjs = TaskMaster.objects.filter(Week=s,Year=y,AssignTo=i['AssignTo']).count()

                        checkedalltaskobj = TaskMaster.objects.filter(Week=s,Year=y,AssignTo=i['AssignTo'],Zone__isnull=False).count()

                        allmanageremptaskobjs = TaskMaster.objects.filter(Week=s,Year=y,AssignBy=m,AssignTo=i['AssignTo']).count()
                        totalmanagerweektask += allmanageremptaskobjs

                        checkedbymanagertaskobjs = TaskMaster.objects.filter(Week=s,Year=y,AssignBy=m,AssignTo=i['AssignTo'],Zone__isnull=False).count()

                        uncheckedtaskobjs = TaskMaster.objects.filter(Week=s,Year=y,AssignBy=m,AssignTo=i['AssignTo'],Zone__isnull=True).count()

                        uncheckbym_count += uncheckedtaskobjs
                        uncheckedinweek += uncheckedtaskobjs

                        if alltaskobjs == allmanageremptaskobjs :
                            if allmanageremptaskobjs == checkedbymanagertaskobjs:
                                checkfinalsubmit = IntermediateTrackProResult.objects.filter(Week=s,Year=y,EmpID=i['AssignTo']).first()
                                if checkfinalsubmit is None:
                                    weeklyempcount += 1
                                    allunheckedemplist.append(i['AssignTo'])
                                    empdata['finalsubmit']="Not Done"
                                    empdata['empid']=i['AssignTo']
                                    userobj = Users.objects.filter(id=i['AssignTo']).first()
                                    empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                    empdata['checkedcount']="All Checked"
                                    empdata['uncheckedcount'] = "--"
                                    empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                    empdata['allemptask'] = alltaskobjs
                            else:
                                weeklyempcount += 1
                                allunheckedemplist.append(i['AssignTo'])
                                empdata['finalsubmit']="Not Done"
                                empdata['empid']=i['AssignTo']
                                userobj = Users.objects.filter(id=i['AssignTo']).first()
                                empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                empdata['checkedcount']=checkedbymanagertaskobjs
                                empdata['uncheckedcount'] = uncheckedtaskobjs
                                empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                empdata['allemptask'] = alltaskobjs
                        else:
                            if alltaskobjs == checkedalltaskobj:
                                checkfinalsubmit = IntermediateTrackProResult.objects.filter(Week=s,Year=y,EmpID=i['AssignTo']).first()
                                if checkfinalsubmit is None:
                                    weeklyempcount += 1
                                    allunheckedemplist.append(i['AssignTo'])
                                    empdata['finalsubmit']="Not Done"
                                    empdata['empid']=i['AssignTo']
                                    userobj = Users.objects.filter(id=i['AssignTo']).first()
                                    empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                    empdata['checkedcount']="All Checked"
                                    empdata['uncheckedcount'] = "--"
                                    empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                    empdata['allemptask'] = alltaskobjs
                            else:
                                if allmanageremptaskobjs != checkedbymanagertaskobjs:
                                    weeklyempcount += 1
                                    allunheckedemplist.append(i['AssignTo'])
                                    empdata['finalsubmit']="Not Done"
                                    empdata['empid']=i['AssignTo']
                                    userobj = Users.objects.filter(id=i['AssignTo']).first()
                                    empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                    empdata['checkedcount']=checkedbymanagertaskobjs
                                    empdata['uncheckedcount'] = uncheckedtaskobjs
                                    empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                    empdata['allemptask'] = alltaskobjs

                        if len(empdata) != 0:
                            empdatalist.append(empdata)

                    if empdatalist != []:
                        weekdict['Week'] = s
                        weekdict['Year'] = y
                        weekdict['Totaltaskinweek'] = totalmanagerweektask
                        weekdict['uncheckedinweek']=uncheckedinweek
                        weekdict['weeklyempcount'] = weeklyempcount
                        weekdict['Empdata'] = empdatalist
                       

                    if len(weekdict) != 0:
                        weeklydatalist.append(weekdict)

        allunhecked_empset = set(allunheckedemplist)
        allunhecked_empcount = len(allunhecked_empset)
        
        if weeklydatalist != []:
            managerobj = Users.objects.filter(id=m).first()
            managername = managerobj.Firstname + " " + managerobj.Lastname
            managerdict['managerId'] = m
            managerdict['managername'] = managername
            managerdict['manageremail'] = managerobj.email
            managerdict['allunheckedtask'] = uncheckbym_count
            managerdict['allunhecked_empcount'] = allunhecked_empcount
            managerdict['empweeklydata'] = weeklydatalist

        if len(managerdict) != 0:
            managerlist.append(managerdict)

    for p in managerlist:
        if p['allunheckedtask'] != 0:
            notificationmsg = "<span class='highlighttext'> Reminder </span> for <span class='notfmaintext'> Weekly trackpro Evaluation </span> !<br> <div class='notftaskinfo'> Unchecked Tasks : <span class='highlighttext'>"+str(p['allunheckedtask'])+"</span><br> Total Employees : <span class='highlighttext'>"+str(p['allunhecked_empcount'])+ "</span></div> Kindly take necessary action and for more details check your email. "

            TaskNotification.objects.create(UserID_id=p['managerId'],company_code=company_code,leaveID=0,NotificationTypeId_id=5,NotificationTitle="Reminder",NotificationMsg=notificationmsg)

            wholecontent =""
            unchecktask = str(p['allunheckedtask'])
            empcount = str(p['allunhecked_empcount'])

            greetingcontent = "Dear Sir/Madam," +"<br>" +"<span style='padding-left:40px;'>" +" We hope this email finds you well. We want to inform you that For ideal performance, Weekly Assessment is an essential step to generate weekly rank and also to audit the progress of employees, and build a bright outlook."+"</span>""<br>"+"We are sharing a trackpro check Report. You can see a breakdown of "+ empcount +" Employees and "+unchecktask+ " Tasks" +" below which are unchecked. Your prompt action will help us improve the system."+"<br>"

            footercontent = "<br><br>"+"Regards ,"+"<br>"+ "Zentro Team"
            for e in p['empweeklydata']:
                weeklymessage = ""
                message = ""
                headingmessage =""
                weeklymessage += "<b> Year :</b>"+ str(e['Year']) + "  <b> Week : </b>" + str(e['Week']) +"<br>"
                
                for k in e['Empdata']:
                    message += """
                                <tr>
                                    <td style="border: 1px solid #dddddd;">"""+ k['empname'] + """</td>
                                    <td style="border: 1px solid #dddddd; text-align: center;">"""+ str(k['uncheckedcount']) +"""</td>
                                    <td style="border: 1px solid #dddddd;">"""+ k['finalsubmit'] +"""</td>
                                </tr>
                            """
                headingmessage += """<table>
                        <tr>
                            <th style="border: 1px solid #dddddd; padding: 4px;">Employee Name</th>
                            <th style="border: 1px solid #dddddd; padding: 4px;">Unchecked task</th>
                            <th style="border: 1px solid #dddddd; padding: 4px;">Final Submit</th>
                        </tr> 
                        """+message+"""
                        
                        </table>"""
                wholecontent += "<br>" + weeklymessage + headingmessage
            mailcontent = greetingcontent + wholecontent + footercontent
            msg = EmailMessage(
                    'TrackPro Check Report',
                    mailcontent,
                    EMAIL_HOST_USER,
                    [p['manageremail']],
                    )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

    return Response({'n':1,"status":"success","message":"data found successfully","data":managerlist})






@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def trackprocheck_employeescheduler(request):
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    currweek = week_num
    employeelist=[]
    yearlist=[]
    company_code = "O001"
    taskobj = TaskMaster.objects.filter(company_code=company_code).distinct('AssignTo')
    taskmgser = PostTaskMasterSerializer(taskobj,many=True)
    for t in taskmgser.data:
        empobj = Users.objects.filter(id=t['AssignTo'],is_active=True).first()
        if empobj is not None:
            employeelist.append(t['AssignTo'])

  
    yearobj = TaskMaster.objects.filter(company_code=company_code).distinct('Year').order_by('Year')
    yearmgser = PostTaskMasterSerializer(yearobj,many=True)
    for o in yearmgser.data:
        yearlist.append(o['Year'])

    empdatalist = []
    for i in employeelist:
        allweekcount = 0
        empdict={}
        weekdatalist=[]
        for y in yearlist:
            weeklist=[]
            weekobj = TaskMaster.objects.filter(Year=y,AssignTo=i).distinct('Week').order_by('Week')
            if weekobj is not None:
                weekser = PostTaskMasterSerializer(weekobj,many=True)
                for ws in weekser.data:
                    weeklist.append(ws['Week'])

                if currweek in weeklist:
                    weeklist.remove(currweek)
              
                for w in weeklist:
                    weekdict = {}
                    allTaskcount = TaskMaster.objects.filter(Week=w,Year=y,AssignTo=i).count()

                    uncheckedtaskobjs = TaskMaster.objects.filter(Week=w,Year=y,AssignTo=i,Zone__isnull=True).count()

                    checkedtaskobjs = TaskMaster.objects.filter(Week=w,Year=y,AssignTo=i,Zone__isnull=False).count()

                    allweekcount += uncheckedtaskobjs

                    if checkedtaskobjs == allTaskcount:
                        finalsubobj = IntermediateTrackProResult.objects.filter(Week=w,Year=y,EmpID=i).first()
                        if finalsubobj is None:
                            weekdict['Final Submit'] = "Pending"
                            weekdict['Year'] = y
                            weekdict['Week'] = w
                            weekdict['alltaskcount'] = allTaskcount
                            weekdict['uncheckedcount'] = "--"
                    else:
                        weekdict['Final Submit'] = "Pending"
                        weekdict['Year'] = y
                        weekdict['Week'] = w
                        weekdict['alltaskcount'] = allTaskcount
                        weekdict['uncheckedcount'] = uncheckedtaskobjs

                    if len(weekdict) != 0:
                        weekdatalist.append(weekdict)

        if weekdatalist != []:
            empdict['empid'] = i
            empobj = Users.objects.filter(id=i,is_active=True).first()
            empdict['empname'] = empobj.Firstname +""+empobj.Lastname
            empdict['email'] = empobj.email
            empdict['uncheckedcount']=allweekcount
            empdict['weekdata'] = weekdatalist

        if len(empdict) != 0: 
            empdatalist.append(empdict)

    elist=[]
    for i in empdatalist:
        elist.append(i['empid'])

    for o in empdatalist:
        if o['uncheckedcount'] != 0:
            notificationmsg = "<span class='highlighttext'>Reminder</span> for <span class='notfmaintext'> Weekly trackpro Evaluation </span> !<br> you have <span class='highlighttext'>"+ str(o['uncheckedcount']) + " Unchecked Tasks. </span><br>Please reach out to your respective managers and For more details check your Email." 

            TaskNotification.objects.create(UserID_id=o['empid'],company_code=company_code,leaveID=0,NotificationTypeId_id=5,NotificationTitle="Reminder",NotificationMsg=notificationmsg)

            wholecontent =""
            unchecktask = str(o['uncheckedcount'])

            greetingcontent = "Dear Sir/Madam,"+"<br>" +"<span style='padding-left:40px;'>" +" We hope this email finds you well. We want to inform you that For ideal performance, Weekly Assessment is an essential step to generate weekly rank and also to audit the progress of employees, and build a bright outlook."+"</span>""<br>"+"We are sharing a trackpro check Report. You can see a breakdown of " +unchecktask+ " Tasks" +" below which are unchecked. Please Inform your respective managers."+"<br>"

            footercontent = "<br><br>"+"Regards ,"+"<br>"+ "Zentro Team"
            message = ""
            headingmessage =""
            for k in o['weekdata']:
                message += """
                            <tr>
                                <td style="border: 1px solid #dddddd;">"""+ str(k['Year']) + """</td>
                                <td style="border: 1px solid #dddddd; text-align: center;">"""+ str(k['Week']) +"""</td>
                                <td style="border: 1px solid #dddddd; text-align:center;">"""+ str(k['uncheckedcount']) +"""</td>
                                <td style="border: 1px solid #dddddd; text-align:center;">"""+ str(k['alltaskcount']) +"""</td>
                                <td style="border: 1px solid #dddddd;">"""+ str(k['Final Submit']) +"""</td>
                            </tr>
                        """
            headingmessage += """<table>
                    <tr>
                        <th style="border: 1px solid #dddddd; padding: 6px;">Year</th>
                        <th style="border: 1px solid #dddddd; padding: 6px;">Week</th>
                        <th style="border: 1px solid #dddddd; padding: 6px; text-align:center;">Unchecked Tasks</th>
                        <th style="border: 1px solid #dddddd; padding: 6px; text-align:center;">All Tasks</th>
                        <th style="border: 1px solid #dddddd; padding: 6px;">Final Submit</th>
                    </tr> 
                    """+message+"""
                    
                    </table>"""
            wholecontent += "<br>" + headingmessage
            mailcontent = greetingcontent + wholecontent + footercontent

            msg = EmailMessage(
                    'TrackProCheck Reminder',
                    mailcontent,
                    EMAIL_HOST_USER,
                    [o['email']],
                    )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()


    return Response({'n':1,"status":"success","message":"data found successfully","data":empdatalist})






@api_view(['POST'])
def trackprocheck_report(request):
    year=request.POST.get('Year')
    week=request.POST.get('Week')
    company_code = request.user.company_code
    weeklist = []
    if year is not None and  week is not None:
        if week == 'All':
            weekobj = TaskMaster.objects.filter(Year=year).distinct('Week')
            # weektaskmgser = TaskMasterSerializer(weekobj,many=True)
            for t in weekobj:
                weeklist.append(t.Week)
        else:
            weeklist.append(week)

        managerlist=[]

        alltaskcount = TaskMaster.objects.filter(Week__in=weeklist,Year=year).count()
        checkedtaskcount =  TaskMaster.objects.filter(Week__in=weeklist,Year=year,Zone__isnull=False).count()
        uncheckedtaskcount =  TaskMaster.objects.filter(Week__in=weeklist,Year=year,Zone__isnull=True).count()

        task_allempcount = TaskMaster.objects.filter(Week__in=weeklist,Year=year).distinct('AssignTo').count()
        task_allmangcount = TaskMaster.objects.filter(Week__in=weeklist,Year=year).distinct('AssignBy').count()

        taskmanagerobjs = TaskMaster.objects.filter(Week__in=weeklist,Year=year,AssignBy__isnull = False).distinct('AssignBy')
        # taskmgser = TaskMasterSerializer(taskmanagerobjs,many=True)
        for t in taskmanagerobjs:
            managerlist.append(t.AssignBy_id)
        if managerlist != []:
            managerdatalist = []
            uncheckedmanager_count = 0
            allunheckedemplist = []
            mcount = 0
            for m in managerlist:
                uncheckbym_count=0
                manager_empcount = 0
                managerdict={}
                empdatalist=[]
                taskempobjs = TaskMaster.objects.filter(Week__in=weeklist,Year=year,AssignBy=m).distinct('AssignTo')
                # taskempser = GetTaskSerializer(taskempobjs,many=True)
                employeesrno = 0
                for i in taskempobjs:
                    empdata={}

                    alltaskobjs = TaskMaster.objects.filter(Week__in=weeklist,Year=year,company_code=company_code,AssignTo=i.AssignTo_id).count()

                    checkedalltaskobj = TaskMaster.objects.filter(Week__in=weeklist,Year=year,company_code=company_code,AssignTo=i.AssignTo_id,Zone__isnull=False).count()

                    allmanageremptaskobjs = TaskMaster.objects.filter(Week__in=weeklist,Year=year,company_code=company_code,AssignBy=m,AssignTo=i.AssignTo_id).count()

                    checkedbymanagertaskobjs = TaskMaster.objects.filter(Week__in=weeklist,Year=year,company_code=company_code,AssignBy=m,AssignTo=i.AssignTo_id,Zone__isnull=False).count()

                    uncheckedtaskobjs = TaskMaster.objects.filter(Week__in=weeklist,Year=year,company_code=company_code,AssignBy=m,AssignTo=i.AssignTo_id,Zone__isnull=True).count()

                    uncheckbym_count += uncheckedtaskobjs

                    if alltaskobjs == allmanageremptaskobjs :
                        if allmanageremptaskobjs == checkedbymanagertaskobjs:
                            checkfinalsubmit = IntermediateTrackProResult.objects.filter(Week__in=weeklist,company_code=company_code,Year=year,EmpID=i.AssignTo_id).first()
                            if checkfinalsubmit is None:
                                manager_empcount += 1
                                employeesrno += 1
                                empdata['empsrno'] = employeesrno
                                allunheckedemplist.append(i.AssignTo_id)
                                empdata['empid']=i.AssignTo_id
                                empdata['strmanagerid'] = str(m)
                                empdata['strempid'] = str(i.AssignTo_id)
                                empdata['finalsubmit']="Not Done"
                                empdata['finalsubmitstr'] = "<span class='btn finalbtn' onclick='finalsubmitemp("+str(i.AssignTo_id)+","+str(m)+")'>Final Submit</span>"
                                userobj = Users.objects.filter(id=i.AssignTo_id).first()
                                empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                empdata['checkedcount']="All Checked"
                                empdata['uncheckedcount'] = "--"
                                empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                empdata['allemptask'] = alltaskobjs
                        else:
                            manager_empcount += 1
                            employeesrno += 1
                            empdata['empsrno'] = employeesrno
                            empdata['strmanagerid'] = str(m)
                            empdata['strempid'] = str(i.AssignTo_id)
                            allunheckedemplist.append(i.AssignTo_id)
                            empdata['finalsubmit']="Not Done"
                            empdata['finalsubmitstr'] = "<span class='btn finaldisablebtn'>Final Submit</span>"
                            empdata['empid']=i.AssignTo_id
                            userobj = Users.objects.filter(id=i.AssignTo_id).first()
                            empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                            empdata['checkedcount']=checkedbymanagertaskobjs
                            empdata['uncheckedcount'] = uncheckedtaskobjs
                            empdata['allmanagertaskcount'] = allmanageremptaskobjs
                            empdata['allemptask'] = alltaskobjs
                    else:
                        if alltaskobjs == checkedalltaskobj:
                            checkfinalsubmit = IntermediateTrackProResult.objects.filter(Week__in=weeklist,Year=year,EmpID=i.AssignTo_id).first()
                            if checkfinalsubmit is None:
                                manager_empcount += 1
                                employeesrno += 1
                                empdata['empsrno'] = employeesrno
                                empdata['strmanagerid'] = str(m)
                                empdata['strempid'] = str(i.AssignTo_id)
                                allunheckedemplist.append(i.AssignTo_id)
                                empdata['empid']=i.AssignTo_id
                                empdata['finalsubmit']="Not Done"
                                empdata['finalsubmitstr'] = "<span class='btn finalbtn' onclick='finalsubmitemp("+str(i.AssignTo_id)+","+str(m)+")'>Final Submit</span>" 
                                userobj = Users.objects.filter(id=i.AssignTo_id).first()
                                empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                empdata['checkedcount']="All Checked"
                                empdata['uncheckedcount'] = "--"
                                empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                empdata['allemptask'] = alltaskobjs
                        else:
                            if allmanageremptaskobjs != checkedbymanagertaskobjs:
                                manager_empcount += 1
                                allunheckedemplist.append(i.AssignTo_id)
                                empdata['finalsubmit']="Not Done"
                                empdata['finalsubmitstr'] = "<span class='btn finaldisablebtn'>Final Submit</span>"
                                employeesrno += 1
                                empdata['empsrno'] = employeesrno
                                empdata['strmanagerid'] = str(m)
                                empdata['strempid'] = str(i.AssignTo_id)
                                empdata['empid']=i.AssignTo_id
                                userobj = Users.objects.filter(id=i.AssignTo_id).first()
                                empdata['empname'] = userobj.Firstname + " " + userobj.Lastname
                                empdata['checkedcount']=checkedbymanagertaskobjs
                                empdata['uncheckedcount'] = uncheckedtaskobjs
                                empdata['allmanagertaskcount'] = allmanageremptaskobjs
                                empdata['allemptask'] = alltaskobjs
                    if len(empdata) != 0:
                        empdatalist.append(empdata)

                if empdatalist != []:
                    mcount += 1
                    managerdict['managersrno'] = mcount
                    managerdict['id'] = m
                    uncheckedmanager_count += 1
                    managerobj = Users.objects.filter(id=m).first()
                    managername = managerobj.Firstname + " " + managerobj.Lastname
                    managerdict['managername'] = managername
                    managerdict['TotaluncheckedTask'] = uncheckbym_count
                    managerdict['TotalEmployees'] = manager_empcount
                    managerdict['empdata'] = empdatalist

                if len(managerdict) != 0:
                    managerdatalist.append(managerdict)


            allunhecked_empset = set(allunheckedemplist)
            allunhecked_empcount = len(allunhecked_empset)

            context={
                'alltaskcount':alltaskcount,
                'uncheckedtaskcount':uncheckedtaskcount,
                'checkedtaskcount':checkedtaskcount,
                'task_allempcount':task_allempcount,
                'uncheckedempcount':allunhecked_empcount,
                'task_allmangcount':task_allmangcount,
                'Uncheckedmanagercount':uncheckedmanager_count,
                'Managerdata':managerdatalist,
            }
            return Response({'n':1,"status":"success","message":"data found successfully","data":context})
        else:
            return Response({'n':0,"status":"Failed","message":"Managers not found","data":''})
    else:
        return Response({'n':0,"status":"Failed","message":"Please Enter valid inputs","data":''})





        
@api_view(['GET'])
def testemail(request):
    wholecontent ="hellooo"
    footercontent = "<br><br>"+"Regards ,"+"<br>"+ "Zentro Team"
    mailcontent = wholecontent + footercontent
    msg = EmailMessage(
            'testemail',
            mailcontent,
            EMAIL_HOST_USER,
            ['shadabshaikh567@gmail.com'],
            )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    return Response({'n':1,"status":"success","message":"data found successfully"})

@api_view(['POST'])
def reportfinalsubmitapi(request):
    Year=request.data.get('Year')
    Week=request.data.get('Week')
    Employee=int(request.data.get('empid'))
    managerid = request.user.id

    reportfinalsubmitapigetTaskScoretaskpointsper = 0
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
    year_num, week_num, day_of_week = my_date.isocalendar()
    currweek = week_num
    curryear = year_num

    if int(Year) == int(curryear) and int(Week) == int(currweek):
        return Response({'n':0,"status":"failed","message":"Cannot Final Submit for current week","data":{}}) 
    else:
        requestData ={}
        GreenZoneTask = 0
        YellowZoneTask = 0
        RedZoneTask = 0
        NotdoneZoneTask = 0
        bonus = 0
        cancelledZoneTask=0
        rejectedZoneTask=0
        extracredits=0
        requestData['company_code'] = request.user.company_code

        scoreObject=TaskMaster.objects.filter(Week=Week,Year=Year,AssignTo=Employee)
        if scoreObject is not None:

            scoreObjectCount = TaskMaster.objects.filter(Week=Week,Year=Year,AssignTo=Employee,company_code=requestData['company_code']).count()

            checkedalltaskobj = TaskMaster.objects.filter(Week=Week,Year=Year,AssignTo=Employee,company_code=requestData['company_code'],Zone__isnull=False).count()

            if scoreObjectCount == checkedalltaskobj:
                Ser=GetTaskScoreSerializer(scoreObject,many=True)
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
                totalScore = (scoreObjectCount-cancelledZoneTask) * greencountmultiple 
                trackpropercentcal = (100 * (((GreenZoneTask + YellowZoneTask + RedZoneTask + bonus + extracredits) - (NotdoneZoneTask + rejectedZoneTask)) / totalScore))
                trackpropercent = round(trackpropercentcal, 2)
                requestData['Green'] = GreenZoneTask
                requestData['Yellow'] = YellowZoneTask
                requestData['Red'] = RedZoneTask
                requestData['NotDone'] = NotdoneZoneTask
                requestData['Cancelled'] = cancelledZoneTask
                requestData['Rejected'] = rejectedZoneTask
                requestData['Bonus'] = bonus
                requestData['extra_credit']=extracredits
                requestData["TotalScore"] = totalScore
                requestData["TrackProScore"] = totalTrackProScore
                requestData["TrackProPercent"] = trackpropercent
                requestData["TotalTask"] = scoreObjectCount
                requestData["EmpID"] = Employee
                requestData["Employee"] = Employee
                requestData["Week"] = Week
                requestData["Year"] = Year
                requestData["CreatedBy"] = managerid


                i = IntermediateTrackProResult.objects.filter(
                    Employee=Employee, Week=Week, Year=Year)

                if i:
                    return Response({"n": 0, "Msg": "TrackPro score for this employee/week has already been locked", "Status": "Failed"})
                else:
                    serializer = IntermediatePostTrackProResultSerializer(
                        data=requestData, context={'request': request})
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'n':1,"status":"success","message":"TrackPro score for this employee/week is  saved","data":{}})
                    else:
                        return Response({'n':0,"status":"failed","message":"TrackPro Score of week not submitted","data":serializer.errors})
                    
            else:
                return Response({'n':0,"status":"failed","message":"All Tasks are not checked","data":{}})      
        else:
            return Response({'n':0,"status":"failed","message":"Task not found","data":{}}) 




@api_view(['POST'])
def gettaskassignbymodal(request):
    taskid = request.data.get('taskid')
    task = TaskMaster.objects.filter(id=taskid).first()

    if task is None:
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
        
        usermapping = UserToManager.objects.filter(UserID=task.AssignTo)
        usermappingser = MappingSerializer(usermapping,many=True)

        return Response({
            "data": serializer.data,
            "manager_data":usermappingser.data,
            "response": {
                "n": 1,
                "msg": "Task Information Found Successfully",
                "status": "Success"
            }
        })
    



@api_view(['POST'])
def updateassignby(request):
    
    data={}
    taskid = request.data.get('taskid')
    assignby =  request.data.get('Taskassignby')
    if taskid is not None and assignby is not None:
        data['AssignBy'] = assignby
        assignbyobj = Users.objects.filter(id=data['AssignBy']).first()
        
        assbystr = assignbyobj.Firstname+" "+ assignbyobj.Lastname
        data['AssignByStr'] = assbystr
        taskobj = TaskMaster.objects.filter(id=taskid).first()
        if taskobj is not None:
            taskser = GetTaskSerializer(taskobj,data=data,partial=True) 
            assigntoobject = Users.objects.filter(id=taskobj.AssignTo_id).first()
            asstostr = assigntoobject.Firstname+" "+ assigntoobject.Lastname
            if taskser.is_valid():
                taskser.save()
                return Response({'n':1,"status":"success","message":"Task Manager is Updated","data":taskser.data,'asstostr':asstostr})
            else:
                return Response({'n':0,"status":"failed","message":"","data":taskser.errors}) 
        else:
            return Response({'n':0,"status":"failed","message":"Task not found","data":{}})
    else:
        return Response({'n':0,"status":"failed","message":"Please enter valid inputs","data":{}})



@api_view(['POST'])
def get_employee_working_history(request):
    employeeId=request.user.id
    Week=request.POST.get('Week')
    AssignBy=request.POST.get('AssignBy')
    current_year = datetime.datetime.now().year
    allTaskcount = TaskMaster.objects.filter(AssignTo=employeeId,Year=current_year)
    uncheckedtaskobjs = TaskMaster.objects.filter(AssignTo=employeeId,Year=current_year,Zone__isnull=True)
    checkedtaskobjs = TaskMaster.objects.filter(AssignTo=employeeId,Year=current_year,Zone__isnull=False)
    searchobj = TaskMaster.objects.filter(AssignTo=employeeId,Year=current_year).order_by("id")
    projectobj = TaskMaster.objects.filter(AssignTo=employeeId,Year=current_year).distinct("Project")

    if Week is not None and Week !="":

        allTaskcount=allTaskcount.filter(Week=Week)
        uncheckedtaskobjs=uncheckedtaskobjs.filter(Week=Week)
        checkedtaskobjs=checkedtaskobjs.filter(Week=Week)
        searchobj=searchobj.filter(Week=Week)
        projectobj=projectobj.filter(Week=Week)

    if AssignBy is not None and AssignBy !="":

        allTaskcount=allTaskcount.filter(AssignBy=AssignBy)
        uncheckedtaskobjs=uncheckedtaskobjs.filter(AssignBy=AssignBy)
        checkedtaskobjs=checkedtaskobjs.filter(AssignBy=AssignBy)
        searchobj=searchobj.filter(AssignBy=AssignBy)
        projectobj=projectobj.filter(AssignBy=AssignBy)


    allTaskcount=allTaskcount.count()
    uncheckedtaskobjs=uncheckedtaskobjs.count()
    checkedtaskobjs=checkedtaskobjs.count()

    if searchobj is not None :
        searchobjser = GetTaskMasterProjectTimeSerializer(projectobj,many=True)
        for h in searchobjser.data:
            projectid = h['Project']
            taskobj =  TaskMaster.objects.filter(Project=projectid,AssignTo=employeeId,Year=current_year).order_by("AssignDate")
            if Week is not None and Week !="":
                taskobj=taskobj.filter(Week=Week)
            if AssignBy is not None and AssignBy !="":
                taskobj=taskobj.filter(AssignBy=AssignBy)

            taskser = GetTaskMasterProjectTimeSerializer(taskobj,many=True)
            projecthours=0
            for i in taskser.data:
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
            h['hours']=int(phours)
            h['minutes']=int(pminutes)



        return Response({"n": 1, "Msg": "Data found successfully","Status": "Success","data":{"allTaskcount":allTaskcount,
                                                                 "uncheckedtaskobjs":uncheckedtaskobjs,
                                                                 "checkedtaskobjs":checkedtaskobjs,
                                                                 "projects":searchobjser.data}}, status=status.HTTP_201_CREATED)        
    else:
        return Response({'n':0,"status":"Success","message":"No project found","data":{"allTaskcount":allTaskcount,
                                                                 "uncheckedtask":uncheckedtaskobjs,
                                                                 "checkedtask":checkedtaskobjs,
                                                                 "projects":[]
                                                                 }})






