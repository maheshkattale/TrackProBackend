from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from  Rules.serializers import *
from Users.models import *
from Users.serializers import *
import json
from django.db.models import Q
from Tasks.views import sendfirebasenotification,senddesktopnotf,send_desktop_notfication_to_all

# Create your views here.

@api_view(['POST'])
def LeaveRulesAPI(request):
    data={}
    user = request.data.get('userid')
    data['Periodof_L']=request.data.get('leaveperiod')
    data['Assignedleaves']=request.data.get('assignedleaves')
    data['maxleaves']=request.data.get('maxlimit')
    data['lapsestatus']=request.data.get('lapse_status')
    if data['lapsestatus']== 'CarryForward':
        data['carryforward']=request.data.get('carryforward')
    data['encashment']=request.data.get('encashment')
    usercode = Users.objects.filter(id=user).first()
    data['company_code']=usercode.company_code
    data['CreatedBy']= request.data.get('userid')

    existleave = Leaverule.objects.filter(company_code= data['company_code']).first()
    if existleave is None:
        serializer = leaveruleserializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "leaverule has been added successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error adding leaverules",
                "status": "failure"
            }
        })
    else:
        serializer = leaveruleserializer(existleave,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "leaverule has been added successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error adding leaverules",
                "status": "failure"
            }
        })

   
@api_view(['POST'])
def AttendanceRulesAPI(request):
    data={}
    user = request.data.get('userid')
    data['Fulldayhrs']=request.data.get('fulldayhrs')
    data['Halfdayhrs']=request.data.get('halfdayhrs')
    data['In_timehrs']=request.data.get('intimehrs')
    data['time_extension']=request.data.get('extension')
    data['leverages']= request.data.get('leverages')
      
    usercode = Users.objects.filter(id=user).first()
    data['company_code']=usercode.company_code
    data['CreatedBy']= request.data.get('userid')

    existatt = Attendancerule.objects.filter(company_code= data['company_code']).first()
    if existatt is None:
        serializer = attendanceruleserializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "ATTENDANCErule has been added successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error adding ATTENDANCErule",
                "status": "failure"
            }
        })
    else:
        serializer = attendanceruleserializer(existatt,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "ATTENDANCErule has been added successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error adding ATTENDANCErule",
                "status": "failure"
            }
        })



@api_view(['POST'])
def TrackProRulesAPI(request):
    data={}
    user = request.user.id
    pointlist = request.data.get('pointlist')
    usercode = Users.objects.filter(id=user).first()
    data['company_code']=usercode.company_code
    data['CreatedBy']= request.data.get('userid')
    for i in json.loads(pointlist):
        existcolor = rulestrackpro.objects.filter(color=i['color'],company_code=data['company_code']).first()
        if existcolor:
             existcolor = rulestrackpro.objects.filter(color=i['color'],company_code=data['company_code']).update(points=i['points'],CreatedBy=data['CreatedBy'])
        else:
            rulestrackpro.objects.create(color=i['color'],points=i['points'],company_code=data['company_code'],CreatedBy=data['CreatedBy'])
    userobj =Users.objects.filter(id=user).update(rules=True)
    return Response({
        "data":'',
        "response": {
            "n": 1,
            "msg": "trackproRULE has been added successfully",
            "status": "success"
        }
    })

@api_view(['GET'])
def dataruleslist(request):
    user = request.user.id

    usercode = Users.objects.filter(id=user).first()
    companycode = usercode.company_code

    leaverules = Leaverule.objects.filter(is_active=True,company_code=companycode).first()
    if leaverules is not None:
        leaveser = leaveruleserializer(leaverules)
        leavedata=leaveser.data
    else:
       leavedata = []
  

    attrules = Attendancerule.objects.filter(is_active=True,company_code=companycode).first()
    if attrules is not None:
        attser = attendanceruleserializer(attrules)
        attdata=attser.data
    else:
        attdata=[]
    trackprodict = {}
    trackprorules = rulestrackpro.objects.filter(is_active=True,company_code=companycode)
    if trackprorules is not None:
        trackproser = trackproruleserializer(trackprorules,many=True)
        trackprodata=trackproser.data
        for w in trackprodata:
            trackprodict.update({
                w['color']:int(w['points'])
            })
    else:
        trackprodata=[]

    
    return Response({
        "leavedata":leavedata,
        "attdata": attdata,
        "trackprodata":trackprodata,
        "marks":trackprodict,
        "response": {
            "n": 1,
            "msg": "successfully got all lists",
            "status": "success"
        }
    })


#Announcement

@api_view(['POST'])
def addannouncement(request):
    requestData = request.data.copy()
    requestData['company_code'] = request.user.company_code    
    requestData['CreatedBy'] = request.user.id
    requestData['is_active'] = True
    serializer = annoucementserializer(data=requestData)
    if serializer.is_valid():
        serializer.save()
        
        userlist_obj=Users.objects.filter(is_active=True,company_code=request.user.company_code).exclude(Q(desktopToken__isnull=True)|Q(desktopToken='None')|Q(desktopToken=''))
        user_serializer=UserSerializerDesktopToken(userlist_obj,many=True)
        user_desktoptoken_list=list(user_serializer.data)     
        desktopnotification=send_desktop_notfication_to_all(user_desktoptoken_list,serializer.data['announcementText'])
          
        return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Announcement has been added successfully",
            "status": "success"
        }
    })
    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg": "Error adding Announcement",
            "status": "failure"
        }
    })

@api_view(['POST'])
def updateannouncement(request):
    announcementId = request.POST.get('id')
    announcementObj = AnnounceMent.objects.filter(is_active=True,id=announcementId).first()
    if announcementObj is not None:
        requestData = request.data.copy()
        requestData['company_code'] = request.user.company_code    
        requestData['CreatedBy'] = request.user.id
        requestData['is_active'] = True
        serializer = annoucementserializer(announcementObj,data=requestData)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Announcement has been updated successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error upadting announcement",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": "",
        "response": {
            "n": 0,
            "msg": "Id not found",
            "status": "failure"
        }
    })

@api_view(['GET'])
def announcementlist(request):
    announcementObj = AnnounceMent.objects.filter(is_active=True).order_by('-id')
    if announcementObj is not None:
        serializer = annoucementserializer(announcementObj,many=True)
        for i in serializer.data:
            ddate = i['date']
            strdate = str(ddate)
            newdate = strdate.split('-')[2]+"-"+strdate.split('-')[1]+"-"+strdate.split('-')[0]
            i['date'] = newdate

    if announcementObj is not None:
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Announcement has been found successfully",
                "status": "success"
            }
        })
    else:
        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Announcement not found",
                "status": "failure"
            }
        })

@api_view(['POST'])
def deleteannouncement(request):
    announcementId = request.data.get('id')
    announcementObj = AnnounceMent.objects.filter(is_active=True,id=announcementId).first()
    if announcementObj is not None:
        requestData = request.data.copy()
        requestData['is_active'] = False
        serializer = annoucementserializer(announcementObj,data=requestData,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Announcement has been Deleted successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error deleting announcement",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": "",
        "response": {
            "n": 0,
            "msg": "Id not found",
            "status": "failure"
        }
    })


#News Section

@api_view(['POST'])
def addnews(request):
    requestData = request.data.copy()
    requestData['company_code'] = request.user.company_code    
    requestData['CreatedBy'] = request.user.id
    requestData['is_active'] = True
    serializer = Newsserializer(data=requestData)
    if serializer.is_valid():
        serializer.save()
        return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "News has been added successfully",
            "status": "success"
        }
    })
    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg": "Error adding News",
            "status": "failure"
        }
    })

@api_view(['POST'])
def updatenews(request):
    newsId = request.POST.get('id')
    newsObj = NewsMaster.objects.filter(is_active=True,id=newsId).first()
    if newsObj is not None:
        requestData = request.data.copy()
        requestData['company_code'] = request.user.company_code    
        requestData['CreatedBy'] = request.user.id
        requestData['is_active'] = True
        serializer = Newsserializer(newsObj,data=requestData)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "News has been updated successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error upadting News",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": "",
        "response": {
            "n": 0,
            "msg": "Id not found",
            "status": "failure"
        }
    })

@api_view(['GET'])
def newslist(request):
    newsObj = NewsMaster.objects.filter(is_active=True).order_by('-id')
    serializer = Newsserializer(newsObj,many=True)
    if newsObj is not None:
        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "News has been found successfully",
                "status": "success"
            }
        })
    else:
        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "News not found",
                "status": "failure"
            }
        })

@api_view(['GET'])
def deletenews(request):
    newsId = request.GET.get('id')
    newsObj = NewsMaster.objects.filter(is_active=True,id=newsId).first()
    if newsObj is not None:
        requestData = request.data.copy()
        requestData['is_active'] = False
        serializer = Newsserializer(newsObj,data=requestData,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "News has been Deleted successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error deleting news",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": "",
        "response": {
            "n": 0,
            "msg": "Id not found",
            "status": "failure"
        }
    })
