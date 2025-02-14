from .models import *
from  .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.db.models import Q
import datetime
from Users.static_info import frontUrl,imageUrl
from Users.models import *
from Users.serializers import *
from Tasks.models import *
from Users.custom_functions import *
# Create your views here.

@api_view(['POST'])
def applyshiftrequest(request):
    data = request.data.copy()
    data['employeeId'] = request.user.id
    data['AttendanceId'] = request.user.employeeId
    reqexist = Shiftswap.objects.filter(employeeId=data['employeeId'],Shiftdate=data['Shiftdate'],ShiftId=data['ShiftId'],Active=True).first()
    if reqexist is None:
        shiftallotmentobj1=ShiftAllotment.objects.filter(date=data['Shiftdate'],employeeId=data['employeeId'],shiftId=data['ShiftId'],is_active=True).first()
        if shiftallotmentobj1 is not None:
            shiftallotmentobj2=ShiftAllotment.objects.filter(is_active=True,date=data['Swapshiftdate'],employeeId=data['SwapempId'],shiftId=data['SwapShiftId']).first()
            if shiftallotmentobj2 is not None:
                if data['Reason'] !='' and data['Reason'] is not None:
                    serializer = ShiftswapSerializer(data=data)
                    if serializer.is_valid():
                        serializer.validated_data['Active'] = True
                        serializer.validated_data['created_by'] = request.user.id
                        serializer.validated_data['Status'] = 'Pending'
                        serializer.validated_data['Shiftname'] = shiftallotmentobj1.shift_name
                        serializer.validated_data['Swapshiftname'] = shiftallotmentobj2.shift_name
                        serializer.save()
                        RequestId = serializer.data['id']

                        managerlist = []
                        managerobj = shiftmanagers.objects.filter(Active=True)
                        managerser = shiftmanagersSerializer(managerobj,many=True)
                        for m in managerser.data:
                            userobj = Users.objects.filter(id=int(m['employeeId']),is_active=True).first()
                            if userobj is not None :
                                managerlist.append(userobj.id)

                        if managerlist != []:
                            for mm in managerlist:
                                ShiftswapAction.objects.create(RequestId=RequestId,ManagerId=mm,Active=True)
                                
                        return Response({"n":1,"Msg":"Shift Swap requested successfully","Status":"success"})
                    else:
                        return Response({"n":0,"Msg":serializer.errors,"Status":"Error"})
                else:
                    return Response({'n':0,'msg':'Please provide shift swaping reason','status':'error','data':[]})
            else:
                return Response({'n':0,'msg':'swaping employee dont have this shift alloted on this date','status':'error','data':[]})
        else:
            return Response({'n':0,'msg':'You dont have this shift alloted on this date','status':'error','data':[]})
    else:
        return Response({"n":0,"Msg":"Shift swap request already exist for this shift","Status":"Error"})
    
@api_view(['POST'])
@permission_classes((AllowAny,))
def addshiftmanagers(request):
    data={}
    data['employeeId']=request.data.get('employeeId')
    data['created_by']=request.user.id
    data['isActive'] = True
    managerexist = shiftmanagers.objects.filter(Active=True,employeeId=data['employeeId']).first()     
    if managerexist is not None:
        return Response({"data":'',"response": {"n": 0, "msg": "Manager already exist", "Status": "Failed"}})        
    else:
        serializer = shiftmanagersSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Manager added successfully","status":"success"}})
        else:
            return Response({"data":serializer.errors,"response": {"n": 0, "msg": "Manager not added successfully","status":"failure"}})
            
@api_view(['POST'])
@permission_classes((AllowAny,))
def getempshifts(request):
    empid = request.data.get('empid')
    date = request.data.get('date') #yyyy-mm-dd
    shiftsobj = ShiftAllotment.objects.filter(employeeId=empid,date=date,is_active=True)
    if shiftsobj.exists():
        shiftser = ShiftAllotmentSerializer(shiftsobj,many=True)
        return Response({"data":shiftser.data,"response": {"n": 1, "msg": "shifts found successfully","status":"success"}})
    else:
        return Response({"data":[],"response": {"n": 0, "msg": "shifts not found","status":"failure"}})

@api_view(['GET'])
@permission_classes((AllowAny,))
def shiftreqlist(request):
    #pending list
    Shiftswapobj = Shiftswap.objects.filter(Status = 'Pending',Active=True)
    pendshiftser = ShiftswapSerializer(Shiftswapobj,many=True)
    for i in pendshiftser.data:
        userid = i['employeeId']
        userobj = Users.objects.filter(id=userid).first()
        if userobj is not None:
            i['userstr'] = userobj.Firstname +" "+ userobj.Lastname
        else:
            i['userstr'] = ''

        swapempid = i['SwapempId']
        swapuserobj = Users.objects.filter(id=swapempid).first()
        if swapuserobj is not None:
            i['swapempstr'] = swapuserobj.Firstname +" "+ swapuserobj.Lastname
        else:
            i['swapempstr'] = ''

        

    #Approved list
    appShiftswapobj = Shiftswap.objects.filter(Status = 'Approved',Active=True)
    approvshiftser = ShiftswapSerializer(appShiftswapobj,many=True)
    for a in approvshiftser.data:
        userid = a['employeeId']
        userobj = Users.objects.filter(id=userid).first()
        if userobj is not None:
            a['userstr'] = userobj.Firstname +" "+ userobj.Lastname
        else:
            a['userstr'] = ''

        swapempid = a['SwapempId']
        swapuserobj = Users.objects.filter(id=swapempid).first()
        if swapuserobj is not None:
            a['swapempstr'] = swapuserobj.Firstname +" "+ swapuserobj.Lastname
        else:
            a['swapempstr'] = ''

    
    #Rejected list
    rejShiftswapobj = Shiftswap.objects.filter(Status = 'Rejected',Active=True)
    rejshiftser = ShiftswapSerializer(rejShiftswapobj,many=True)
    for r in rejshiftser.data:
        userid = r['employeeId']
        userobj = Users.objects.filter(id=userid).first()
        if userobj is not None:
            r['userstr'] = userobj.Firstname +" "+ userobj.Lastname
        else:
            r['userstr'] = ''

        swapempid = r['SwapempId']
        swapuserobj = Users.objects.filter(id=swapempid).first()
        if swapuserobj is not None:
            r['swapempstr'] = swapuserobj.Firstname +" "+ swapuserobj.Lastname
        else:
            r['swapempstr'] = ''

    
    context = {
        'Pending_list':pendshiftser.data,
        'Approved_list':approvshiftser.data,
        'Rejected_list':rejshiftser.data
    }

    return Response({"data":context,"response": {"n": 1, "msg": "shifts list found successfully","status":"success"}})

@api_view(['GET'])
def empshiftlist(request):
    userid = request.user.id
    #pending list
    Shiftswapobj = Shiftswap.objects.filter(employeeId = userid,Status = 'Pending',Active=True)
    pendshiftser = ShiftswapSerializer(Shiftswapobj,many=True)
    for i in pendshiftser.data:
        swapempid = i['SwapempId']
        swapuserobj = Users.objects.filter(id=swapempid).first()
        if swapuserobj is not None:
            i['swapempstr'] = swapuserobj.Firstname +" "+ swapuserobj.Lastname
        else:
            i['swapempstr'] = ''

        pendingmangrlist =  ShiftswapAction.objects.filter(RequestId=i['id'],Active=True)
        pendingmangrser = ShiftswapActionSerializer(pendingmangrlist,many=True)
        for pd in pendingmangrser.data:
            mngrid = Users.objects.filter(id=pd['ManagerId']).first()
            if swapuserobj is not None:
                pd['managerstr'] = mngrid.Firstname +" "+ mngrid.Lastname
                managerphoto = mngrid.Photo
                if managerphoto is not None and managerphoto != "":
                    pd['managerimage'] = imageUrl + "/media/" + str(managerphoto)
                else:
                    pd['managerimage'] = imageUrl + "/static/assets/images/profile.png"
            else:
                pd['managerstr'] = ''
                pd['managerimage'] = imageUrl + "/static/assets/images/profile.png"
        i['pendingshiftmang'] = pendingmangrser.data

    #Approved list
    appShiftswapobj = Shiftswap.objects.filter(employeeId = userid,Status = 'Approved',Active=True)
    approvshiftser = ShiftswapSerializer(appShiftswapobj,many=True)
    for a in approvshiftser.data:
        userid = a['employeeId']
        userobj = Users.objects.filter(id=userid).first()
        if userobj is not None:
            a['userstr'] = userobj.Firstname +" "+ userobj.Lastname
        else:
            a['userstr'] = ''

        swapempid = a['SwapempId']
        swapuserobj = Users.objects.filter(id=swapempid).first()
        if swapuserobj is not None:
            a['swapempstr'] = swapuserobj.Firstname +" "+ swapuserobj.Lastname
        else:
            a['swapempstr'] = ''

        apprmangrlist =  ShiftswapAction.objects.filter(RequestId=a['id'],Active=True)
        apprmangrser = ShiftswapActionSerializer(apprmangrlist,many=True)
        for ad in pendingmangrser.data:
            mngrid = Users.objects.filter(id=ad['ManagerId']).first()
            if swapuserobj is not None:
                ad['managerstr'] = mngrid.Firstname +" "+ mngrid.Lastname
                managerphoto = mngrid.Photo
                if managerphoto is not None and managerphoto != "":
                    ad['managerimage'] = imageUrl + "/media/" + str(managerphoto)
                else:
                    ad['managerimage'] = imageUrl + "/static/assets/images/profile.png"
            else:
                ad['managerstr'] = ''
                ad['managerimage'] = imageUrl + "/static/assets/images/profile.png"
        a['apprshiftmang'] = apprmangrser.data


    
    #Rejected list
    rejShiftswapobj = Shiftswap.objects.filter(employeeId = userid,Status = 'Rejected',Active=True)
    rejshiftser = ShiftswapSerializer(rejShiftswapobj,many=True)
    for r in rejshiftser.data:
        userid = r['employeeId']
        userobj = Users.objects.filter(id=userid).first()
        if userobj is not None:
            r['userstr'] = userobj.Firstname +" "+ userobj.Lastname
        else:
            r['userstr'] = ''

        swapempid = r['SwapempId']
        swapuserobj = Users.objects.filter(id=swapempid).first()
        if swapuserobj is not None:
            r['swapempstr'] = swapuserobj.Firstname +" "+ swapuserobj.Lastname
        else:
            r['swapempstr'] = ''

        rejmangrlist =  ShiftswapAction.objects.filter(RequestId=a['id'],Active=True)
        rejmangser = ShiftswapActionSerializer(rejmangrlist,many=True)
        for rd in pendingmangrser.data:
            mngrid = Users.objects.filter(id=rd['ManagerId']).first()
            if swapuserobj is not None:
                rd['managerstr'] = mngrid.Firstname +" "+ mngrid.Lastname
                managerphoto = mngrid.Photo
                if managerphoto is not None and managerphoto != "":
                    rd['managerimage'] = imageUrl + "/media/" + str(managerphoto)
                else:
                    rd['managerimage'] = imageUrl + "/static/assets/images/profile.png"
            else:
                rd['managerstr'] = ''
                rd['managerimage'] = imageUrl + "/static/assets/images/profile.png"
        r['rejshiftmang'] = rejmangser.data

    context = {
        'Pending_list':pendshiftser.data,
        'Approved_list':approvshiftser.data,
        'Rejected_list':rejshiftser.data
    }
    return Response({"data":context,"response": {"n": 1, "msg": "shifts list found successfully","status":"success"}})

@api_view(['POST'])
def shiftaction(request):
    reqdata={}
    data = request.data.copy()
    RequestId = data['RequestId']
    ManagerId = data['ManagerId']
    reqexist = Shiftswap.objects.filter(id=RequestId,Active=True).first()
    if reqexist is None:
        manobj = ShiftswapAction.objects.filter(RequestId=RequestId,ManagerId=ManagerId,Active=True).first()
        if manobj is not None :
            reqdata['ActionTaken'] = data['ActionTaken']
            reqdata['RejectionReason'] = data['RejectionReason']
            serializer = ShiftswapActionSerializer(manobj,data=reqdata,partial=True)
            if serializer.is_valid():
                serializer.validated_data['Active'] = True
                serializer.validated_data['updated_by'] = request.user.id
                serializer.save()

                apprvobjs = ShiftswapAction.objects.filter(RequestId=RequestId,ActionTaken='Approved',Active=True).count()
                if apprvobjs >= 2 :
                    Shiftswap.objects.filter(id=RequestId,Active=True).update(Status = 'Approved')

                rejectedobjs = ShiftswapAction.objects.filter(RequestId=RequestId,ActionTaken='Rejected',Active=True).count()
                if rejectedobjs > 2 :
                    Shiftswap.objects.filter(id=RequestId,Active=True).update(Status = 'Rejected')
                
            else:
                return Response({"data":serializer.errors,"response": {"n": 0, "msg": "shift manager action not submitted","status":"failure"}})
        else:
            return Response({"data":[],"response": {"n": 0, "msg": "shift manager not found","status":"failure"}})
    else:
        return Response({"data":[],"response": {"n": 0, "msg": "shift not found","status":"failure"}})

@api_view(['POST'])    
def get_manager_pending_shift_swap_applications(request):
    user_id = request.user.id
    shift_approval_obj=ShiftswapAction.objects.filter(ManagerId=user_id,ActionTaken='Pending',Active=True).distinct('RequestId')
    shift_ids_serializer=shift_id_serializer(shift_approval_obj,many=True)
    pending_shift_swaping = Shiftswap.objects.filter(id__in=list(shift_ids_serializer.data),Active=True,Status='Pending').order_by('-Shiftdate')
    if pending_shift_swaping.exists():
        shift_swap_serializer = CustomShiftswapSerializer(pending_shift_swaping,many=True)
        shift_swaps=shift_swap_serializer.data
        for shift_swap in shift_swaps:
            shift_swap_approvals_obj=ShiftswapAction.objects.filter(RequestId=shift_swap['id'],Active=True)
            shift_swap_managers_serializer=CustomShiftswapActionSerializer(shift_swap_approvals_obj,many=True)
            manager_status=shift_swap_approvals_obj.filter(RequestId=shift_swap['id'],ManagerId=user_id).first()
            if manager_status is not None:
                if manager_status.ActionTaken=='Pending':
                    shift_swap['manager_action']=None
                elif manager_status.ActionTaken=='Approved':
                    shift_swap['manager_action']=True
                elif manager_status.ActionTaken=='Rejected':
                    shift_swap['manager_action']=False
                else:
                    shift_swap['manager_action']=False
            else:
                shift_swap['manager_action']=False

            shift_swap['managers']=shift_swap_managers_serializer.data
            
        return Response ({"data":shift_swap_serializer.data,"response":{"n" : 1,"msg" : "Pending Swaps found ","status" : "success"}})
    else:
        return Response ({"data":[],"response":{"n" : 0,"msg" : "No pending swaps found ","status" : "error"}})

@api_view(['POST'])    
def get_manager_approved_shift_swap_applications(request):
    user_id = request.user.id
    shift_approval_obj=ShiftswapAction.objects.filter(ManagerId=user_id,ActionTaken='Approved',Active=True).distinct('RequestId')
    shift_ids_serializer=shift_id_serializer(shift_approval_obj,many=True)
    Approved_shift_swaping = Shiftswap.objects.filter(id__in=list(shift_ids_serializer.data),Active=True).exclude(Status='Rejected').order_by('-Shiftdate')
    if Approved_shift_swaping.exists():
        shift_swap_serializer = CustomShiftswapSerializer(Approved_shift_swaping,many=True)
        shift_swaps=shift_swap_serializer.data
        for shift_swap in shift_swaps:
            shift_swap_approvals_obj=ShiftswapAction.objects.filter(RequestId=shift_swap['id'],Active=True)
            shift_swap_managers_serializer=CustomShiftswapActionSerializer(shift_swap_approvals_obj,many=True)
            shift_swap['managers']=shift_swap_managers_serializer.data
            
        return Response ({"data":shift_swap_serializer.data,"response":{"n" : 1,"msg" : "Approved Swaps found ","status" : "success"}})
    else:
        return Response ({"data":[],"response":{"n" : 0,"msg" : "No Approved swaps found ","status" : "error"}})
    
@api_view(['POST'])    
def get_manager_rejected_shift_swap_applications(request):
    user_id = request.user.id
    shift_approval_obj=ShiftswapAction.objects.filter(ManagerId=user_id,ActionTaken='Rejected',Active=True).distinct('RequestId')
    shift_ids_serializer=shift_id_serializer(shift_approval_obj,many=True)
    Rejected_shift_swaping = Shiftswap.objects.filter(id__in=list(shift_ids_serializer.data),Active=True,Status='Rejected').order_by('-Shiftdate')
    if Rejected_shift_swaping.exists():
        shift_swap_serializer = CustomShiftswapSerializer(Rejected_shift_swaping,many=True)
        shift_swaps=shift_swap_serializer.data
        for shift_swap in shift_swaps:
            shift_swap_approvals_obj=ShiftswapAction.objects.filter(RequestId=shift_swap['id'],Active=True)
            shift_swap_managers_serializer=CustomShiftswapActionSerializer(shift_swap_approvals_obj,many=True)
            shift_swap['managers']=shift_swap_managers_serializer.data
            
        return Response ({"data":shift_swap_serializer.data,"response":{"n" : 1,"msg" : "Rejected Swaps found ","status" : "success"}})
    else:
        return Response ({"data":[],"response":{"n" : 0,"msg" : "No Rejected swaps found ","status" : "error"}})
    
@api_view(['POST'])    
def approve_shift_swap_applications(request):
    user_id = request.user.id
    shift_swap=request.POST.get('id')
    company_code=request.user.company_code
    if shift_swap is not None and shift_swap !='':
        Shiftswap_obj=Shiftswap.objects.filter(id=shift_swap,Active=True).first()
        if Shiftswap_obj is not None:
            Shiftswap_serializer=CustomShiftswapSerializer(Shiftswap_obj)
            Shiftswap_approval_obj = ShiftswapAction.objects.filter(RequestId=Shiftswap_serializer.data['id'],ManagerId=user_id,Active=True).first()
            if Shiftswap_approval_obj is not None:
                shiftallotmentobj1=ShiftAllotment.objects.filter(is_active=True,date=convert_date_dby_to_yyyy_mm_dd(Shiftswap_serializer.data['Shiftdate']),employeeId=Shiftswap_serializer.data['employeeId'],shiftId=Shiftswap_serializer.data['ShiftId']).first()

                if shiftallotmentobj1 is not None:
                    serializer1 = ShiftAllotmentSerializer(shiftallotmentobj1)
                    shiftallotmentobj2=ShiftAllotment.objects.filter(is_active=True,date=convert_date_dby_to_yyyy_mm_dd(Shiftswap_serializer.data['Swapshiftdate']),employeeId=Shiftswap_serializer.data['SwapempId'],shiftId=Shiftswap_serializer.data['SwapShiftId']).first()
                    if shiftallotmentobj2 is not None:
                        serializer2 = ShiftAllotmentSerializer(shiftallotmentobj2)
                        Shiftswap_approval_serializer=CustomShiftswapActionSerializer(Shiftswap_approval_obj)
                        if Shiftswap_obj.Status == 'Pending':
                            Shiftswap_approval_obj.ActionTaken='Approved'
                            Shiftswap_approval_obj.save() #approved the manager status
                            check_2_approvals=ShiftswapAction.objects.filter(RequestId=Shiftswap_serializer.data['id'],ActionTaken='Approved',Active=True).count()
                            
                            if check_2_approvals >=2: #check 2  approvals
                                Shiftswap_obj.Status='Approved'
                                Shiftswap_obj.save()
                                shift_1={
                                    'date':shiftallotmentobj1.date,
                                    'shift_name':shiftallotmentobj1.shift_name,
                                    'shiftId':shiftallotmentobj1.shiftId,
                                }
                                shift_2={
                                    'date':shiftallotmentobj2.date,
                                    'shift_name':shiftallotmentobj2.shift_name,
                                    'shiftId':shiftallotmentobj2.shiftId,
                                }



                                shiftallotmentobj1.date = shift_2['date']
                                shiftallotmentobj1.shift_name = shift_2['shift_name']
                                shiftallotmentobj1.shiftId = shift_2['shiftId']
                                shiftallotmentobj1.is_swaped = True
                                shiftallotmentobj1.swapper = True
                                shiftallotmentobj1.swap_request_id = Shiftswap_serializer.data['id']
                                shiftallotmentobj1.save()

                                shiftallotmentobj2.date = shift_1['date']
                                shiftallotmentobj2.shift_name = shift_1['shift_name']
                                shiftallotmentobj2.shiftId = shift_1['shiftId']
                                shiftallotmentobj2.is_swaped = True
                                shiftallotmentobj2.swapper = False
                                shiftallotmentobj2.swap_request_id = Shiftswap_serializer.data['id']
                                shiftallotmentobj2.save()

                                notificationmsg = "Your shift swap request dated on <span class='notfappid'>" +Shiftswap_serializer.data['Shiftdate']+"</span> has been <span class='rejectedmsg'> Approved </span>"
                                TaskNotification.objects.create(UserID_id=Shiftswap_obj.employeeId,company_code=company_code,NotificationTypeId_id=9,NotificationTitle="Shift-swap Approved",NotificationMsg=notificationmsg,leaveID=0)

                            else:
                                notificationmsg = "Your Shiftswap request dated on <span class='notfappid'>" +Shiftswap_serializer.data['Shiftdate']+"</span> has been partially approved by <span class='rejectedmsg'>" +Shiftswap_approval_serializer.data['manager_name'] +" </span>"
                                TaskNotification.objects.create(UserID_id=Shiftswap_obj.employeeId,company_code=company_code,NotificationTypeId_id=9,NotificationTitle="Shift-swap Approved",NotificationMsg=notificationmsg,leaveID=0)
                            
                            notfmsg = "You have approved shift-swap request of <span class='actionuser'>" + Shiftswap_serializer.data['first_employee_name'] + "</span> dated <span class='notfleavedate'>" +Shiftswap_serializer.data['Shiftdate']+" </span>"
                            TaskNotification.objects.create(UserID_id=int(request.user.id),To_manager=True,company_code=company_code,action_Taken=None,NotificationTypeId_id=9,NotificationTitle="Shift-swap",leaveID=0,NotificationMsg=notfmsg)

                            Shiftswap_managers=ShiftswapAction.objects.filter(RequestId=Shiftswap_serializer.data['id'],Active=True).exclude(ManagerId=user_id).distinct('ManagerId')  

                            managers_serializer=CustomShiftswapActionSerializer(Shiftswap_managers,many=True)
                            for manager in managers_serializer.data:
                                manager_msg = Shiftswap_approval_serializer.data['manager_name'] +" has approved Shift-swap request of <span class='actionuser'>" + Shiftswap_serializer.data['first_employee_name'] + "</span> dated on <span class='notfleavedate'>" +Shiftswap_serializer.data['Shiftdate']+" </span>"
                                TaskNotification.objects.create(UserID_id=manager['ManagerId'],To_manager=True,company_code=company_code,action_Taken=None,NotificationTypeId_id=9,NotificationTitle="Shift-swap",leaveID=0,NotificationMsg=manager_msg)
                            return Response ({"data":[],"response":{"n" : 1,"msg" : "Shift-swap approved successfully","status" : "success"}})
                        elif Shiftswap_obj.Status == 'Rejected':
                            Shiftswap_rejected_obj=ShiftswapAction.objects.filter(RequestId=Shiftswap_serializer.data['id'],ActionTaken='Rejected',Active=True).first()
                            if Shiftswap_rejected_obj is not None:
                                rejected_Shiftswap_serializer=CustomShiftswapActionSerializer(Shiftswap_rejected_obj)
                                mesg='by '+ rejected_Shiftswap_serializer.data['manager_name']
                            else:
                                mesg=''
                            return Response ({"data":[],"response":{"n" : 0,"msg" : "Shift-swap is already rejected "+mesg,"status" : "error"}})
                        else:
                            Shiftswap_approval_obj.ActionTaken='Approved'
                            Shiftswap_approval_obj.save() #approved the manager status
                            return Response ({"data":[],"response":{"n" : 0,"msg" : "Shift-swap is already approved","status" : "error"}})
                    else:
                        return Response ({"data":[],"response":{"n" : 0,"msg" : "Second employee alloted shift not found","status" : "error"}})
                else:
                    return Response ({"data":[],"response":{"n" : 0,"msg" : "First employee alloted shift not found","status" : "error"}})
            else:
                return Response ({"data":[],"response":{"n" : 0,"msg" : "Sorry you dont have access to approve this Shiftswap","status" : "error"}})
        else:
            return Response ({"data":[],"response":{"n" : 0,"msg" : "No Shift-swap found ","status" : "error"}})
    else:
        return Response ({"data":[],"response":{"n" : 0,"msg" : "Please provide Shift-swaps id ","status" : "error"}})

@api_view(['POST'])    
def reject_shift_swap_applications(request):
    user_id = request.user.id
    company_code = request.user.company_code
    shift_swap_id=request.POST.get('id')
    if shift_swap_id is not None and shift_swap_id !='':
        shift_swap_obj=Shiftswap.objects.filter(id=shift_swap_id,Active=True).first()
        if shift_swap_obj is not None:
            shift_swap_serializer=CustomShiftswapSerializer(shift_swap_obj)
            shift_swap_approval_obj = ShiftswapAction.objects.filter(RequestId=shift_swap_serializer.data['id'],ManagerId=user_id,Active=True).first()
            if shift_swap_approval_obj is not None:
                shift_swap_approval_serializer=CustomShiftswapActionSerializer(shift_swap_approval_obj)
                if shift_swap_obj.Status == 'Pending':
                    reason=request.POST.get('reason')
                    if reason is not None and reason !='':
                        shift_swap_approval_obj.ActionTaken='Rejected'
                        shift_swap_approval_obj.RejectionReason=reason
                        shift_swap_approval_obj.save() #reject the manager status
                        shift_swap_obj.Status='Rejected'
                        shift_swap_obj.save()

                        notificationmsg = "Your shift swap request dated on <span class='notfappid'>" +shift_swap_serializer.data['Shiftdate']+"</span> has been rejected by <span class='rejectedmsg'>" +shift_swap_approval_serializer.data['manager_name'] +" </span>"
                        TaskNotification.objects.create(UserID_id=shift_swap_serializer.data['employeeId'],company_code=company_code,NotificationTypeId_id=9,NotificationTitle="Shift-swap Rejected",NotificationMsg=notificationmsg,leaveID=0)
                    
                        notfmsg = "You have rejected shift swap request of <span class='actionuser'>" + shift_swap_serializer.data['first_employee_name'] + "</span> dated <span class='notfleavedate'>" +shift_swap_serializer.data['Shiftdate']+" </span>"
                        TaskNotification.objects.create(UserID_id=int(request.user.id),To_manager=True,company_code=company_code,action_Taken=None,NotificationTypeId_id=9,NotificationTitle="Shift-swap",leaveID=0,NotificationMsg=notfmsg)


                        shift_swap_managers=ShiftswapAction.objects.filter(RequestId=shift_swap_serializer.data['id'],Active=True).exclude(ManagerId=user_id).distinct('ManagerId')  
                        
                        managers_serializer=CustomShiftswapActionSerializer(shift_swap_managers,many=True)
                        for manager in managers_serializer.data:
                            manager_msg = shift_swap_approval_serializer.data['manager_name'] +" has rejected shift swap request of <span class='actionuser'>" + shift_swap_serializer.data['first_employee_name'] + "</span> dated on <span class='notfleavedate'>" +shift_swap_serializer.data['Shiftdate']+" </span>"
                            TaskNotification.objects.create(UserID_id=manager['ManagerId'],To_manager=True,company_code=company_code,action_Taken=None,NotificationTypeId_id=9,NotificationTitle="Shift-swap",leaveID=0,NotificationMsg=manager_msg)
                        return Response ({"data":[],"response":{"n" : 1,"msg" : "Shift-swap rejected successfully","status" : "success"}})
                    else:
                        return Response ({"data":[],"response":{"n" : 0,"msg" : "Please provide rejection reason","status" : "error"}})
                elif shift_swap_obj.Status =='Rejected':
                    shift_swap_rejected_obj=ShiftswapAction.objects.filter(RequestId=shift_swap_serializer.data['id'],ActionTaken='Rejected',Active=True).first()
                    if shift_swap_rejected_obj is not None:
                        rejected_shift_swap_serializer=CustomShiftswapActionSerializer(shift_swap_rejected_obj)
                        mesg='by '+ rejected_shift_swap_serializer.data['manager_name']
                    else:
                        mesg=''
                    return Response ({"data":[],"response":{"n" : 0,"msg" : "Shift-swap is already rejected "+mesg,"status" : "error"}})
                
                
                else:
                    shift_swap_approval_obj.Status='Rejected'
                    shift_swap_approval_obj.save() #approved the manager status
                    return Response ({"data":[],"response":{"n" : 0,"msg" : "Shift-swap is already rejected by you ","status" : "error"}})
            else:
                return Response ({"data":[],"response":{"n" : 0,"msg" : "Sorry you dont have access to reject this shift swap","status" : "error"}})        
        else:
       
            return Response ({"data":[],"response":{"n" : 0,"msg" : "No Shift-swap found ","status" : "error"}})
    else:
        return Response ({"data":[],"response":{"n" : 0,"msg" : "Please provide Shift-swaps id ","status" : "error"}})
