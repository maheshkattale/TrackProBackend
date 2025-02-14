from .serializers import *
from .static_info import frontUrl, imageUrl
from .models import *
from .views import *
import requests
import math
from Packet.models import *
from Packet.serializers import *
from Leave.models import *
from Leave.serializers import *
from collections import Counter
from django.db.models import Q, Sum, Case, When, Value, FloatField
from datetime import date, datetime, timedelta, time

def date_range_list(start_date,end_date):
    start_date=datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
    date_list=[]
    delta = end_date - start_date    
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_list.append(day)
    return date_list

def dd_mm_yyyy(input_date):
    
    output_date=''
    if input_date !='':
        
        input_date_object = datetime.strptime(input_date, "%Y-%m-%d")
        
         
        output_date = input_date_object.strftime("%d-%m-%Y")
        
        return output_date
    else:
        return output_date
               

def convert_date_dby_to_yyyy_mm_dd(date_str):
     
    input_format = "%d %b %Y"
    
    output_format = "%Y-%m-%d"
    
     
    date_obj = datetime.strptime(str(date_str), input_format)
    
     
    formatted_date = date_obj.strftime(output_format)
    
    return formatted_date


def hh_mm(input_time):
     
    output_time=''
    if input_time !='':
        
        input_time_object = datetime.strptime(input_time, "%H:%M:%S")
        
        
        output_time = input_time_object.strftime("%H:%M")
        
        return output_time
    else:
        return output_time
        
def conver_created_at_date(datestr):
    datetimestr = str(datestr)
    createddate = str(datetimestr.split('T')[0])
    datestr = dd_month_year_format(createddate)
    return datestr

        
def gettodaysshift(shift_data,current_date):
    
    current_time_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_time = datetime.strptime(current_time_string, '%Y-%m-%d %H:%M:%S')

    
    current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
    
    last_runingshift={"shiftname":'','shiftstarttime':'','shiftendtime':''}
    runingshift={'n':0,'data':{"shiftname":'','shiftstarttime':'','shiftendtime':''},'last_runingshift':last_runingshift}
    
    for shift in shift_data:
        start_time = datetime.strptime(str(current_date) +' '+ shift['intime'], '%Y-%m-%d %H:%M')
        start_time_before_2hrs = start_time - timedelta(hours=2)
        if shift['intime'] > shift['outtime']:
            shift_end_date = current_date + timedelta(days=1)
        else:
            shift_end_date = current_date
        end_time = datetime.strptime(str(shift_end_date) +' '+ shift['outtime'], '%Y-%m-%d %H:%M')
        
        
        if start_time_before_2hrs < current_time:
            
            last_runingshift={"shiftname":shift['shiftname'],'shiftstarttime':start_time_before_2hrs,'shiftendtime':end_time}
        
        if start_time_before_2hrs <= current_time <= end_time:
            runingshift={'n':1,'data':{"shiftname":shift['shiftname'],'shiftstarttime':start_time_before_2hrs,'shiftendtime':end_time},'last_runingshift':last_runingshift}
            
            

    runingshift['last_runingshift']=last_runingshift   
    

    return runingshift



def convertdate2(input_date):
    try:
        date_obj = datetime.strptime(input_date, '%Y-%m-%d')

        formatted_date = date_obj.strftime('%d %b %y')

        return formatted_date
    except ValueError:
        return " "

def create_google_maps_url(latitude, longitude):
    base_url = "https://www.google.com/maps/search/?api=1&query={},{}"
    return base_url.format(latitude, longitude)


def get_location_name(latitude, longitude):
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": latitude,
        "lon": longitude,
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        display_name = data.get('display_name', "Location not found")
        return display_name
    else:
        return "Failed to retrieve location"
    

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
     
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

     
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371   
    return r * c * 1000   

def is_within_radius(lat1, lon1, lat2, lon2, radius):
    """
    Check if a point (lat1, lon1) is within a certain radius (in meters)
    of another point (lat2, lon2)
    """
    distance = haversine(lat1, lon1, lat2, lon2)
    return distance <= radius

            
def add_leading_zero(number):
    if 0 <= number <= 9:
        return f'0{number}'
    else:
        return str(number)

def get_date_shift_details(date,attendanceId):
    office_location=Location.objects.filter(Active=True).exclude(Q(lattitude='',meter='',longitude='') |Q(lattitude=None,meter=None,longitude=None)|Q(lattitude__isnull=True,meter__isnull=True,longitude__isnull=True))
    location_serializer=LocationSerializer(office_location,many=True)
    
    current_date_shift_list=[]
    new_current_date_shift_list=[]
    return_dict={}
                
    shiftdate = datetime.strptime(date, '%Y-%m-%d').date()
    tomarrow_date = shiftdate +timedelta(days=1)
    yesterday_date = shiftdate -timedelta(days=1)
    current_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=attendanceId,date=str(date),is_active=True)
    current_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(current_shiftallotment_objs,many=True)
    current_shiftId_list=list(current_shiftallotment_serializers.data)
    current_shift_obj=ShiftMaster.objects.filter(id__in=current_shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
    current_shift_serializer=ShiftMasterSerializer(current_shift_obj,many=True)
    current_shiftlist=current_shift_serializer.data
                
    tomarrow_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=attendanceId,date=str(tomarrow_date),is_active=True)
    tomarrow_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(tomarrow_shiftallotment_objs,many=True)
    tomarrow_shiftId_list=list(tomarrow_shiftallotment_serializers.data)
    tomarrow_shift_obj=ShiftMaster.objects.filter(id__in=tomarrow_shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
    tomarrow_shift_serializer=ShiftMasterSerializer(tomarrow_shift_obj,many=True)
    tomarrow_shiftlist=tomarrow_shift_serializer.data

    count=1

    for shift in current_shiftlist:
        start_time =datetime.strptime(str(shiftdate) +' '+ shift['intime'], '%Y-%m-%d %H:%M')
        start_time_before_2hrs = start_time - timedelta(hours=2)
        
        if shift['intime'] > shift['outtime']:
            shift_end_date = shiftdate + timedelta(days=1)
        else:
            shift_end_date = shiftdate
            
        end_time =datetime.strptime(str(shift_end_date) +' '+ shift['outtime'], '%Y-%m-%d %H:%M')
        check_login_till=''
        if len(current_shiftlist) >= count+1:
        
            check_next_shift_in =datetime.strptime(str(shiftdate) +' '+ current_shiftlist[count]['intime'], '%Y-%m-%d %H:%M')
            check_login_till = check_next_shift_in - timedelta(hours=2)

            
        elif check_login_till=='':
                
            if len(tomarrow_shiftlist) >= 1:
                
                check_next_shift_in =datetime.strptime(str(tomarrow_date) +' '+ tomarrow_shiftlist[0]['intime'], '%Y-%m-%d %H:%M')
                check_login_till = check_next_shift_in - timedelta(hours=2)
            else:
            
                if_no_shift_check_shift=ShiftAllotment.objects.filter(attendanceId=attendanceId,date=str(tomarrow_date),is_active=True)
                tomerrow_shiftlist=ShiftAllotmentshiftIdSerializer(if_no_shift_check_shift,many=True)
                next_date_shiftId_list=list(tomerrow_shiftlist.data)
                check_weekly_off=ShiftMaster.objects.filter(id__in=next_date_shiftId_list,intime='00:00',outtime='00:00',is_active=True).order_by('intime').first()
                if check_weekly_off is not None:
                    
                    if shift['outtime'] < shift['intime']:
                
                        check_current_shift_out =datetime.strptime(str(tomarrow_date) +' '+ shift['outtime'], '%Y-%m-%d %H:%M')
                        check_current_shift_out_time = check_current_shift_out + timedelta(hours=2)
                        given_datetime =datetime.strptime(str(check_current_shift_out_time), '%Y-%m-%d %H:%M:%S')

                        truncated_datetime_str = given_datetime.strftime('%Y-%m-%d %H:%M')

                        
                        shift_end_date_time=str(truncated_datetime_str)
                    else:
                        shift_end_date_time=str(date) +' '+ '23:59'
                        
                    check_login_till =datetime.strptime(shift_end_date_time, '%Y-%m-%d %H:%M')
                else:
                
                    check_login_till =datetime.strptime(str(tomarrow_date) +' '+ '07:30', '%Y-%m-%d %H:%M')
                    
        shift_data={
            'shiftname':shift['shiftname'],
            'indatetime':str(start_time_before_2hrs),
            'outdatetime':str(check_login_till),
            'intime':shift['intime'],
            'outtime':shift['outtime'],
        }
        current_date_shift_list.append(shift_data)
        new_current_date_shift_list.append(shift_data)
        count+=1





    if len(current_shiftlist) == 0:       
    
        if_no_shift_check_shift=ShiftAllotment.objects.filter(attendanceId=attendanceId,date=str(date),is_active=True)
        todays_shiftlist=ShiftAllotmentshiftIdSerializer(if_no_shift_check_shift,many=True)
        toadys_shiftId_list=list(todays_shiftlist.data)
        check_weekly_off=ShiftMaster.objects.filter(id__in=toadys_shiftId_list,intime='00:00',outtime='00:00',is_active=True).order_by('intime').first()
        if check_weekly_off is not None:

            get_previous_day_shift=ShiftAllotment.objects.filter(attendanceId=attendanceId,date=str(yesterday_date),is_active=True)
            previous_day_shiftlist=ShiftAllotmentshiftIdSerializer(get_previous_day_shift,many=True)
            previous_shiftId_list=list(previous_day_shiftlist.data)
            get_previous_last_shift=ShiftMaster.objects.filter(id__in=previous_shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime').last()
            
            if get_previous_last_shift is not None:
                if get_previous_last_shift.outtime < get_previous_last_shift.intime:
                    shift_end_date_time=str(date) +' '+ str(get_previous_last_shift.outtime)
                else:
                    shift_end_date_time=str(yesterday_date) +' '+ '23:59'
                        
                check_previous_shift_out =datetime.strptime(str(shift_end_date_time), '%Y-%m-%d %H:%M')
                previous_shift_in_time = check_previous_shift_out + timedelta(hours=2)  
            else:

                
                previous_shift_in_time= str(date)+' 00:00:00'
             
            get_net_day_shift=ShiftAllotment.objects.filter(attendanceId=attendanceId,date=str(tomarrow_date),is_active=True)
            nest_day_shiftlist=ShiftAllotmentshiftIdSerializer(get_net_day_shift,many=True)
            next_date_shiftId_list=list(nest_day_shiftlist.data)
            get_next_day_first_shift=ShiftMaster.objects.filter(id__in=next_date_shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime').first()
            if get_next_day_first_shift is not None:
                check_next_shift_in =datetime.strptime(str(tomarrow_date) +' '+ str(get_next_day_first_shift.intime), '%Y-%m-%d %H:%M')
                next_shift_in_time = check_next_shift_in - timedelta(hours=2)
                shift_data={
                    'shiftname':str(check_weekly_off.shiftname),
                    'indatetime':str(previous_shift_in_time),
                    'outdatetime':str(next_shift_in_time),
                    'intime':check_weekly_off.intime,
                    'outtime':check_weekly_off.outtime,
                }
                current_date_shift_list.append(shift_data)
                new_current_date_shift_list.append(shift_data)
                
            else:
                shift_data={
                    'shiftname':str(check_weekly_off.shiftname),
                    'indatetime':str(previous_shift_in_time),
                    'outdatetime':str(date)+' 23:59:59',
                    'intime':check_weekly_off.intime,
                    'outtime':check_weekly_off.outtime,
                }
                current_date_shift_list.append(shift_data)
                new_current_date_shift_list.append(shift_data)

        else:
            shift_data={
                'shiftname':'General',
                'indatetime':str(date)+' 07:30:00',
                'outdatetime':str(tomarrow_date)+' 07:30:00',
                'intime':'09:30',
                'outtime':'18:30',
            }
            current_date_shift_list.append(shift_data)
            new_current_date_shift_list.append(shift_data)

            
    current_date_first_in_datetime=''
    current_date_last_out_datetime=''
    extra_days=''
    total_working_hrs=''
    for s in new_current_date_shift_list:
        intime=''
        intimedate=''
        
        
        getallattendance = attendance.objects.filter(Q(employeeId=str(attendanceId),time__gte=s['indatetime'].split(' ')[1],date=s['indatetime'].split(' ')[0])|Q(employeeId=str(attendanceId),time__lte=str(s['outdatetime']).split(' ')[1],date=str(s['outdatetime']).split(' ')[0])).order_by('date','time')
                            
        attendance_serializer=attendanceserializer(getallattendance,many=True)
    
        
        sorted_data = sorted(attendance_serializer.data, key=lambda x: (x['date'], x['time']))
        
        mindatetime =datetime.strptime(s['indatetime'], '%Y-%m-%d %H:%M:%S')
        maxdatetime =datetime.strptime(s['outdatetime'], '%Y-%m-%d %H:%M:%S')
    
        sorted_data = [entry for entry in sorted_data if (mindatetime <=datetime.strptime(entry['date'] +' '+entry['time'],'%Y-%m-%d %H:%M:%S') <= maxdatetime)]
        if len(sorted_data) > 0:
            intimedate=sorted_data[0]['date']
            intime=str(sorted_data[0]['time'])
            
        if intimedate !='' and intimedate is not None:
            user_sdt =datetime.strptime(str(intimedate) + ' ' + str(intime), '%Y-%m-%d %H:%M:%S')
            shif_sdt =datetime.strptime(s['indatetime'].split(' ')[0] + ' ' + s['indatetime'].split(' ')[1], '%Y-%m-%d %H:%M:%S')
            if user_sdt < shif_sdt :
                intimedate=''
                intime=''

                
        checkin_time = None
        total_working_time = 0
        attendance_log=[]
        attendance_history=[]

        for index, entry in enumerate(sorted_data):

            if entry['checkout']:
                if entry['deviceId'] is not None and entry['deviceId'] !='':
                    attendance_type="Machine Checkout"
                    attendance_type_resaon=""
                    if entry['deviceId'] == 20:
                        remote_map_location=create_google_maps_url(18.566064883698555, 73.77574703366226)
                        remote_map_name='Zentro Pune Office'
                    elif entry['deviceId'] == 19:
                        remote_map_location=create_google_maps_url(19.1764898841813, 72.95988765068624)
                        remote_map_name='Zentro Mumbai Office'
                    else:
                        remote_map_location=''
                        remote_map_name=''
                elif entry['Remote_Reason'] is not None and entry['Remote_Reason'] !='':
                    attendance_type="Remote Checkout"
                    attendance_type_resaon=entry['Remote_Reason']
                    remote_map_location=create_google_maps_url(entry['remote_latitude'],entry['remote_longitude'])
                    remote_map_name=get_location_name(entry['remote_latitude'],entry['remote_longitude'])

                else:
                    attendance_type="Web Checkout"
                    attendance_type_resaon=''
                    
                    if entry['attendance_type'] !='' and  entry['attendance_type'] is not None:
                        attendance_type = entry['attendance_type'] +' '+ 'Checkout'
                        
                                
                    if entry['remote_latitude'] is not None and  entry['remote_latitude'] !='' and entry['remote_longitude'] is not None and entry['remote_longitude'] !='':

                        for location in location_serializer.data:
                            within_radius = is_within_radius(float(entry['remote_latitude']), float(entry['remote_longitude']), float(location['lattitude']), float(location['longitude']), float(location['meter']))
                            if within_radius:
                                remote_map_location=create_google_maps_url(entry['remote_latitude'],entry['remote_longitude'])
                                remote_map_name='Zentro '+str(location['LocationName']) +' Office'
                        if remote_map_location == '' or  remote_map_name =='' or remote_map_location is None or  remote_map_name  is  None:
                            remote_map_location=create_google_maps_url(entry['remote_latitude'],entry['remote_longitude'])
                            remote_map_name=get_location_name(entry['remote_latitude'],entry['remote_longitude'])
                    else:
                        remote_map_location=''
                        remote_map_name=''                        

                attendance_history.append({'Status':'Check-Out','datetime':entry['date']+' '+entry['time'],'attendance_type':attendance_type,'attendance_type_resaon':attendance_type_resaon,'remote_map_location':remote_map_location,'remote_map_name':remote_map_name})
                    
                attendance_log.append({'checkout':entry['date']+' '+entry['time']})
                
                
                if checkin_time:
                    checkout_datetime =datetime.strptime(entry['date'] + ' ' + entry['time'], '%Y-%m-%d %H:%M:%S')
                    checkin_datetime =datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                    working_time = checkout_datetime - checkin_datetime
                    total_working_time += working_time.total_seconds()
                    checkin_time = None
                    
            elif not entry['checkout']:
                remote_map_location=''
                remote_map_name='' 
                if entry['deviceId'] is not None and entry['deviceId'] !='':
                    attendance_type="Machine Checkin"
                    attendance_type_resaon=''
                    if entry['deviceId'] == 20:
                        remote_map_location=create_google_maps_url(18.566064883698555, 73.77574703366226)
                        remote_map_name='Zentro Pune Office'
                    elif entry['deviceId'] == 19:
                        remote_map_location=create_google_maps_url(19.1764898841813, 72.95988765068624)
                        remote_map_name='Zentro Mumbai Office'
                    else:
                        remote_map_location=''
                        remote_map_name=''
                        
                elif entry['Remote_Reason'] is not None and entry['Remote_Reason'] !='':
                    attendance_type="Remote Checkin"
                    attendance_type_resaon=entry['Remote_Reason']
                    remote_map_location=create_google_maps_url(entry['remote_latitude'],entry['remote_longitude'])
                    remote_map_name=get_location_name(entry['remote_latitude'],entry['remote_longitude'])
                else:
                    attendance_type="Web Checkin"
                    attendance_type_resaon='' 
                    if entry['attendance_type'] !='' and  entry['attendance_type'] is not None:
                        attendance_type = entry['attendance_type'] +' '+ 'Checkin'
                    
                    if entry['remote_latitude'] is not None and  entry['remote_latitude'] !='' and entry['remote_longitude'] is not None and entry['remote_longitude'] !='':
    
    
                        for location in location_serializer.data:
                            within_radius = is_within_radius(float(entry['remote_latitude']), float(entry['remote_longitude']), float(location['lattitude']), float(location['longitude']), float(location['meter']))
                            if within_radius:
                                remote_map_location=create_google_maps_url(entry['remote_latitude'],entry['remote_longitude'])
                                remote_map_name='Zentro '+str(location['LocationName']) +' Office'
                        if remote_map_location == '' or  remote_map_name =='' or remote_map_location is None or  remote_map_name  is  None:
                            remote_map_location=create_google_maps_url(entry['remote_latitude'],entry['remote_longitude'])
                            remote_map_name=get_location_name(entry['remote_latitude'],entry['remote_longitude'])
                    else:
                        remote_map_location=''
                        remote_map_name='' 
                        
                checkin_time = entry['date'] + ' ' + entry['time']
                attendance_log.append({'checkin':entry['date']+' '+entry['time']})
                attendance_history.append({'Status':'Check-In','datetime':entry['date']+' '+entry['time'],'attendance_type':attendance_type,'attendance_type_resaon':attendance_type_resaon,'remote_map_location':remote_map_location,'remote_map_name':remote_map_name})
         
        if checkin_time and index == len(sorted_data) - 1:
            
             

            if int(int(index)-1) >=0:
                if sorted_data[index-1]['checkout']==False:
                    previous_checkin_date_time=sorted_data[index-1]['date']+ ' '+sorted_data[index-1]['time']
                    checkout_datetime =datetime.strptime(previous_checkin_date_time, '%Y-%m-%d %H:%M:%S')
                    checkin_datetime =datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                    working_time = checkin_datetime-checkout_datetime 
                    total_working_time += working_time.total_seconds()


         
        hours, remainder = divmod(total_working_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        s['total_hrs']=str(add_leading_zero(int(hours))) +':' +str(add_leading_zero(int(minutes))) +':'+str(add_leading_zero(int(seconds)))

        if total_working_hrs == '':

            total_working_hrs=s['total_hrs']
        else:
            time_str_1 = total_working_hrs
            time_str_2 = s['total_hrs']



             
            total_time_delta = timedelta(hours=int(time_str_1[:2]), minutes=int(time_str_1[3:5]), seconds=int(time_str_1[6:])) + \
                            timedelta(hours=int(time_str_2[:2]), minutes=int(time_str_2[3:5]), seconds=int(time_str_2[6:]))
            total_working_hrs=str(total_time_delta)
            
        s['attendance_log']=attendance_log
        s['attendance_history']=attendance_history
        if len(attendance_log) !=0:
            infirst_key = next(iter(attendance_log[0]))
            outfirst_key = next(iter(attendance_log[-1]))

            s['usersintime']=attendance_log[0][infirst_key]
            s['usersouttime']=attendance_log[-1][outfirst_key]
            if s['usersouttime'] == s['usersintime']:
                s['usersouttime']= ''
                
        else:
            s['usersintime']=''
            s['usersouttime']=''


        
        if current_date_first_in_datetime =='':
            if s['usersintime'] !='':
                current_date_first_in_datetime=s['usersintime']
        elif s['usersintime'] !='':
            if datetime.strptime(current_date_first_in_datetime, '%Y-%m-%d %H:%M:%S') >datetime.strptime(s['usersintime'], '%Y-%m-%d %H:%M:%S'):
                current_date_first_in_datetime=s['usersintime']

        if current_date_last_out_datetime =='':
            if s['usersouttime'] !='':
                current_date_last_out_datetime=s['usersouttime']
        elif s['usersouttime'] !='':
            if datetime.strptime(current_date_last_out_datetime, '%Y-%m-%d %H:%M:%S') < datetime.strptime(s['usersouttime'], '%Y-%m-%d %H:%M:%S'):
                current_date_last_out_datetime=s['usersouttime']
        
        
        
        

        if current_date_last_out_datetime != '' and current_date_first_in_datetime !='':
            if current_date_last_out_datetime.split(' ')[0] != current_date_first_in_datetime.split(' ')[0]:
                current_date_last_out_datetime1 =datetime.strptime(str(current_date_last_out_datetime).split(' ')[0], '%Y-%m-%d')
                current_date_first_in_datetime1 =datetime.strptime(str(current_date_first_in_datetime).split(' ')[0], '%Y-%m-%d')
                extradaysdiff = current_date_last_out_datetime1 - current_date_first_in_datetime1
                if extradaysdiff.days > 0:
                    extra_days='+'+str(extradaysdiff.days)
            
            
    return_dict['employeeId']=attendanceId
    return_dict['fulldate']=date
    return_dict['shifts_list']=current_date_shift_list

    return_dict['shift']=new_current_date_shift_list[0]
    
    if len(new_current_date_shift_list) > 1:
        shift_name=new_current_date_shift_list[0]['shiftname']
        return_dict['shift']['shiftname'] = str(shift_name) +  ' <span class="text-danger"> +1 </span>'
        new_current_date_shift_list[0]['swap']=''

    else:

        new_current_date_shift_list[0]['swap']=''
        
    
    if current_date_first_in_datetime !='':
        return_dict['inTime']=str(current_date_first_in_datetime).split(' ')[1]
        return_dict['inTime_date']=convertdate2(str(str(current_date_first_in_datetime).split(' ')[0]))
    else:
        return_dict['inTime']=''
        return_dict['inTime_date']=''
        
    if current_date_last_out_datetime !='':
        return_dict['outTime']=str(current_date_last_out_datetime).split(' ')[1]
        return_dict['outTime_date']=convertdate2(str(str(current_date_last_out_datetime).split(' ')[0]))
    else:
        return_dict['outTime']=''
        return_dict['outTime_date']=''
        
    return_dict['extra_days']=extra_days
    return_dict['Total']=total_working_hrs
    if return_dict['shift']['usersintime'] is not None and return_dict['shift']['usersintime'] !='':
        user_punchin=return_dict['shift']['usersintime'].split(' ')[1]
        late_time_obj = datetime.strptime(return_dict['shift']['intime'], '%H:%M') + timedelta(minutes=30)
        halfday_time_obj = datetime.strptime(return_dict['shift']['intime'], '%H:%M') + timedelta(minutes=90)

        if halfday_time_obj > datetime.strptime(user_punchin, '%H:%M:%S') > late_time_obj:
            return_dict['latemark']=True
            return_dict['latetime']=user_punchin
        else:
            return_dict['latemark']=False
            
    else:
        return_dict['latemark']=False
      
    return return_dict
                

def get_current_shift_details(current_date_time,employeeId):
    current_date = datetime.strptime(current_date_time.split(' ')[0], '%Y-%m-%d').date()
    yesterday_date = current_date - timedelta(days=1)
    current_datetime = datetime.strptime(current_date_time, '%Y-%m-%d %H:%M:%S')
    intime=''
    outtime=''
    intimedate=''
    outtimedate=''
    userobj = Users.objects.filter(employeeId = employeeId).first()
    if userobj is not None:
        userser = UserSerializer(userobj)
        locationid = userser.data['locationId']
        if locationid is not None and locationid != "":
            locationobj = Location.objects.filter(id=int(locationid)).first()
            if locationobj is not None:
                location = locationobj.LocationName
            else:
                location = ""
        else:
            location = ""
    else:
        location = ""
    if userobj is not None:

        check_user_type=userobj.employeetype
        if check_user_type is not None:
            check_last_checkin = attendance.objects.filter(employeeId=str(employeeId),date=str(current_date),checkout=False).order_by('time').last()
            check_last_checkout=None
            if check_last_checkin is not None:
                check_last_checkout = attendance.objects.filter(employeeId=str(employeeId),time__gt=check_last_checkin.time,date=str(current_date),checkout=True).order_by('time').last()

            else:
                check_last_checkin = attendance.objects.filter(employeeId=str(employeeId),date=str(yesterday_date),checkout=False).order_by('time').last()
                if check_last_checkin is not None:
                    check_last_checkout = attendance.objects.filter(Q(employeeId=str(employeeId),time__gt=check_last_checkin.time,date=str(yesterday_date),checkout=True)|Q(employeeId=str(employeeId),date=str(current_date),checkout=True)).order_by('date','time').last()
              
            if check_last_checkin is not None :
                intime = check_last_checkin.time
                intimedate=check_last_checkin.date
                punchout = 0
                get_data=1
                outtime = ''
                outtimedate=''
            else:
                get_data=0
                punchout = 1
                intime = ''
                intimedate=''
                outtime = ''
                outtimedate=''
            if check_last_checkout is not None:
                outtime = check_last_checkout.time
                outtimedate=check_last_checkout.date
                punchout = 1
                get_data=0
            else:
                if check_last_checkin is not None :
                    punchout = 0
                    get_data=1
                    outtime = ''
                    outtimedate=''
                else:
                    punchout = 1
                    get_data=0
                    outtime = ''
                    outtimedate=''
                    
            currentshiftname=''
            currentshiftstarttime=''
            currentshiftendtime=''
            currentshiftstartdate=''
            currentshiftenddate=''
            todays_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=employeeId,date=str(current_date),is_active=True)
            todays_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(todays_shiftallotment_objs,many=True)
            shiftId_list=list(todays_shiftallotment_serializers.data)
            shift_obj=ShiftMaster.objects.filter(id__in=shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
            shift_serializer=ShiftMasterSerializer(shift_obj,many=True)
            
            
             
            todays_runnningshift=gettodaysshift(shift_serializer.data,str(current_date))
            if todays_runnningshift['n'] == 1:
                currentshiftname=todays_runnningshift['data']['shiftname']
                currentshiftstarttime=str(todays_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftendtime=str(todays_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftstartdate=str(todays_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                currentshiftenddate=str(todays_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                
            elif todays_runnningshift['last_runingshift']['shiftstarttime'] !='':
                currentshiftname=todays_runnningshift['last_runingshift']['shiftname']
                currentshiftstarttime=str(todays_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftendtime=str(todays_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftstartdate=str(todays_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                currentshiftenddate=str(todays_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
            
            else:
                yesterday_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=employeeId,date=str(yesterday_date),is_active=True)
                yesterday_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(yesterday_shiftallotment_objs,many=True)
                shiftId_list=list(yesterday_shiftallotment_serializers.data)
                shift_obj=ShiftMaster.objects.filter(id__in=shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
                yesterday_shift_serializer=ShiftMasterSerializer(shift_obj,many=True)
                    
                
                yesterday_runnningshift=gettodaysshift(yesterday_shift_serializer.data,str(yesterday_date))
                if yesterday_runnningshift['n'] == 1:
                    currentshiftname=yesterday_runnningshift['data']['shiftname']
                    currentshiftstarttime=str(yesterday_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftendtime=str(yesterday_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftstartdate=str(yesterday_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                    currentshiftenddate=str(yesterday_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                    
                elif yesterday_runnningshift['last_runingshift']['shiftstarttime'] !='':
                    currentshiftname=yesterday_runnningshift['last_runingshift']['shiftname']
                    currentshiftstarttime=str(yesterday_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftendtime=str(yesterday_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftstartdate=str(yesterday_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                    currentshiftenddate=str(yesterday_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                else:
                    currentshiftname='General'
                    currentshiftstarttime='07:30:00'
                    currentshiftendtime='18:30:00'
                    currentshiftstartdate=str(current_date)
                    currentshiftenddate=str(current_date)

            shiftdetails={
                        "shiftname":currentshiftname,
                        "shiftstarttime":currentshiftstarttime,
                        "shiftendtime":currentshiftendtime,
                        "shiftstartdate":currentshiftstartdate,
                        "shiftenddate":currentshiftenddate,
                    }
            

            getallattendance = attendance.objects.filter(Q(employeeId=str(employeeId),time__gte=currentshiftstarttime,date=str(currentshiftstartdate))|Q(employeeId=str(employeeId),time__lte=str(current_datetime).split(' ')[1],date=str(current_datetime).split(' ')[0])).order_by('date','time')            
            attendance_serializer=attendanceserializer(getallattendance,many=True)
            
            sorted_data = sorted(attendance_serializer.data, key=lambda x: (x['date'], x['time']))
            
            mindate = datetime.strptime(currentshiftstartdate, '%Y-%m-%d')
            mintime = datetime.strptime(currentshiftstarttime, '%H:%M:%S').time()

            sorted_data = [entry for entry in sorted_data if (datetime.strptime(entry['date'],'%Y-%m-%d').date() > mindate.date() or (datetime.strptime(entry['date'],'%Y-%m-%d').date() == mindate.date() and datetime.strptime(entry['time'], '%H:%M:%S').time() > mintime))]

            if len(sorted_data) > 0:
                intimedate=sorted_data[0]['date']
                intime=str(sorted_data[0]['time'])
                
            if intimedate !='' and intimedate is not None:
                user_sdt = datetime.strptime(str(intimedate) + ' ' + str(intime), '%Y-%m-%d %H:%M:%S')
                shif_sdt = datetime.strptime(str(currentshiftstartdate) + ' ' + str(currentshiftstarttime), '%Y-%m-%d %H:%M:%S')
                if user_sdt < shif_sdt :
                    intimedate=''
                    intime=''
                    outtime=''
                    outtimedate=''
                    punchout = 1
                    get_data=0
                    
            checkin_time = None
            total_working_time = 0
            for index, entry in enumerate(sorted_data):
                if entry['checkout']:
                    if checkin_time:
                        checkout_datetime = datetime.strptime(entry['date'] + ' ' + entry['time'], '%Y-%m-%d %H:%M:%S')
                        checkin_datetime = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                        working_time = checkout_datetime - checkin_datetime
                        total_working_time += working_time.total_seconds()
                        checkin_time = None
                elif not entry['checkout']:
                    checkin_time = entry['date'] + ' ' + entry['time']

             
            if checkin_time and index == len(sorted_data) - 1:
                checkout_datetime = datetime.now()
                checkin_datetime = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                working_time = checkout_datetime - checkin_datetime
                total_working_time += working_time.total_seconds()


             
            hours, remainder = divmod(total_working_time, 3600)
            minutes, seconds = divmod(remainder, 60)


            

            
            
            current_shift_start_datetime = datetime.strptime(shiftdetails['shiftstartdate'] + ' ' + shiftdetails['shiftstarttime'], '%Y-%m-%d %H:%M:%S')
            current_shift_end_datetime = datetime.strptime(shiftdetails['shiftenddate'] + ' ' + shiftdetails['shiftendtime'], '%Y-%m-%d %H:%M:%S')
            shift_total_working_hrs = current_shift_end_datetime - current_shift_start_datetime
            shift_total_working_hrs -= timedelta(hours=2)   
            rules_obj=TypeRules.objects.filter(TypeId=check_user_type.id,is_active=True).first()

                
                
            total_hrs=str(add_leading_zero(int(hours))) +':' +str(add_leading_zero(int(minutes))) +':'+str(add_leading_zero(int(seconds)))

            if get_data == 1:
                if total_hrs >=str(shift_total_working_hrs):
                    if rules_obj is not None:
                        shift_total_compoff_hrs = shift_total_working_hrs + timedelta(hours=int(rules_obj.CompOffTime)) 

                    
           
            return {
                'indatetime':str(dd_mm_yyyy(str(intimedate))) + ' ' + str(intime),
                'outdatetime':str(dd_mm_yyyy(str(outtimedate))) + ' ' + str(outtime),
                'total_hrs':total_hrs,
                'shift_total_working_hrs':str(shift_total_working_hrs),
                'data':get_data,
                'intime':intime,
                'outtime':outtime,
                'intimedate':intimedate,
                'outtimedate':outtimedate,
                'punchout':punchout,
                'location':location,
                'hours':int(hours),
                'minutes':int(minutes),
                'seconds':int(seconds),
                    "response":{
                        "n" : 1,
                        "msg" : "pass",
                        "status" : "success"
                    }
                    }
            
        else:
            
            check_last_checkin = attendance.objects.filter(employeeId=str(employeeId),date=str(current_date),checkout=False).order_by('time').last()
            check_last_checkout=None
            if check_last_checkin is not None:
                check_last_checkout = attendance.objects.filter(employeeId=str(employeeId),time__gt=check_last_checkin.time,date=str(current_date),checkout=True).order_by('time').last()

            else:
                check_last_checkin = attendance.objects.filter(employeeId=str(employeeId),date=str(yesterday_date),checkout=False).order_by('time').last()
                if check_last_checkin is not None:
                    check_last_checkout = attendance.objects.filter(Q(employeeId=str(employeeId),time__gt=check_last_checkin.time,date=str(yesterday_date),checkout=True)|Q(employeeId=str(employeeId),date=str(current_date),checkout=True)).order_by('date','time').last()

            
            # 1 disable
            # 0 enable
            
            if check_last_checkin is not None :
                
                intime = check_last_checkin.time
                intimedate=check_last_checkin.date
                punchout = 0
                get_data=1
                outtime = ''
                outtimedate=''
            else:
                get_data=0
                punchout = 1
                intime = ''
                intimedate=''
                outtime = ''
                outtimedate=''
               
               
            if check_last_checkout is not None:
                outtime = check_last_checkout.time
                outtimedate=check_last_checkout.date
                punchout = 1
                get_data=0
         
            else:
                if check_last_checkin is not None :
                    punchout = 0
                    get_data=1
                
                    outtime = ''
                    outtimedate=''
                else:
                    punchout = 1
                    get_data=0
                    outtime = ''
                    outtimedate=''
                    
            


            currentshiftname=''
            currentshiftstarttime=''
            currentshiftendtime=''
            currentshiftstartdate=''
            currentshiftenddate=''
            todays_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=employeeId,date=str(current_date),is_active=True)
            todays_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(todays_shiftallotment_objs,many=True)
            shiftId_list=list(todays_shiftallotment_serializers.data)
            shift_obj=ShiftMaster.objects.filter(id__in=shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
            shift_serializer=ShiftMasterSerializer(shift_obj,many=True)
            
            
             
            todays_runnningshift=gettodaysshift(shift_serializer.data,str(current_date))
            if todays_runnningshift['n'] == 1:
                currentshiftname=todays_runnningshift['data']['shiftname']
                currentshiftstarttime=str(todays_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftendtime=str(todays_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftstartdate=str(todays_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                currentshiftenddate=str(todays_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                
            elif todays_runnningshift['last_runingshift']['shiftstarttime'] !='':
                currentshiftname=todays_runnningshift['last_runingshift']['shiftname']
                currentshiftstarttime=str(todays_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftendtime=str(todays_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftstartdate=str(todays_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                currentshiftenddate=str(todays_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
            
            else:
                yesterday_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=employeeId,date=str(yesterday_date),is_active=True)
                yesterday_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(yesterday_shiftallotment_objs,many=True)
                shiftId_list=list(yesterday_shiftallotment_serializers.data)
                shift_obj=ShiftMaster.objects.filter(id__in=shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
                yesterday_shift_serializer=ShiftMasterSerializer(shift_obj,many=True)
                    
                
                yesterday_runnningshift=gettodaysshift(yesterday_shift_serializer.data,str(yesterday_date))
                if yesterday_runnningshift['n'] == 1:
                    currentshiftname=yesterday_runnningshift['data']['shiftname']
                    currentshiftstarttime=str(yesterday_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftendtime=str(yesterday_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftstartdate=str(yesterday_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                    currentshiftenddate=str(yesterday_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                    
                elif yesterday_runnningshift['last_runingshift']['shiftstarttime'] !='':
                    currentshiftname=yesterday_runnningshift['last_runingshift']['shiftname']
                    currentshiftstarttime=str(yesterday_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftendtime=str(yesterday_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                    currentshiftstartdate=str(yesterday_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                    currentshiftenddate=str(yesterday_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                else:
                    currentshiftname='General'
                    currentshiftstarttime='07:30:00'
                    currentshiftendtime='18:30:00'
                    currentshiftstartdate=str(current_date)
                    currentshiftenddate=str(current_date)

            shiftdetails={
                        "shiftname":currentshiftname,
                        "shiftstarttime":currentshiftstarttime,
                        "shiftendtime":currentshiftendtime,
                        "shiftstartdate":currentshiftstartdate,
                        "shiftenddate":currentshiftenddate,
                    }
            

            getallattendance = attendance.objects.filter(Q(employeeId=str(employeeId),time__gte=currentshiftstarttime,date=str(currentshiftstartdate))|Q(employeeId=str(employeeId),time__lte=str(current_datetime).split(' ')[1],date=str(current_datetime).split(' ')[0])).order_by('date','time')
            
             
            
            attendance_serializer=attendanceserializer(getallattendance,many=True)
            
            sorted_data = sorted(attendance_serializer.data, key=lambda x: (x['date'], x['time']))
            
            mindate = datetime.strptime(currentshiftstartdate, '%Y-%m-%d')
            mintime = datetime.strptime(currentshiftstarttime, '%H:%M:%S').time()

            sorted_data = [entry for entry in sorted_data if (datetime.strptime(entry['date'],'%Y-%m-%d').date() > mindate.date() or (datetime.strptime(entry['date'],'%Y-%m-%d').date() == mindate.date() and datetime.strptime(entry['time'], '%H:%M:%S').time() > mintime))]

            if len(sorted_data) > 0:
                intimedate=sorted_data[0]['date']
                intime=str(sorted_data[0]['time'])
                
            if intimedate !='' and intimedate is not None:
                user_sdt = datetime.strptime(str(intimedate) + ' ' + str(intime), '%Y-%m-%d %H:%M:%S')
                shif_sdt = datetime.strptime(str(currentshiftstartdate) + ' ' + str(currentshiftstarttime), '%Y-%m-%d %H:%M:%S')
                if user_sdt < shif_sdt :
                    intimedate=''
                    intime=''
                    outtime=''
                    outtimedate=''
                    punchout = 1
                    get_data=0
                    
            checkin_time = None
            total_working_time = 0
            for index, entry in enumerate(sorted_data):
                if entry['checkout']:
                    if checkin_time:
                        checkout_datetime = datetime.strptime(entry['date'] + ' ' + entry['time'], '%Y-%m-%d %H:%M:%S')
                        checkin_datetime = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                        working_time = checkout_datetime - checkin_datetime
                        total_working_time += working_time.total_seconds()
                        checkin_time = None
                elif not entry['checkout']:
                    checkin_time = entry['date'] + ' ' + entry['time']

             
            if checkin_time and index == len(sorted_data) - 1:
                checkout_datetime = datetime.now()
                checkin_datetime = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                working_time = checkout_datetime - checkin_datetime
                total_working_time += working_time.total_seconds()


            
            hours, remainder = divmod(total_working_time, 3600)
            minutes, seconds = divmod(remainder, 60)


            
            # 1 checkout True disable checkin
            # 0 checkout True enable checkin
            


                    
                    
            return {
                'indatetime':str(dd_mm_yyyy(str(intimedate))) + ' ' + str(intime),
                'outdatetime':str(dd_mm_yyyy(str(outtimedate))) + ' ' + str(outtime),
                'total_hrs':str(add_leading_zero(int(hours))) +':' +str(add_leading_zero(int(minutes))) +':'+str(add_leading_zero(int(seconds))),
                'data':get_data,
                'intime':intime,
                'outtime':outtime,
                'intimedate':intimedate,
                'outtimedate':outtimedate,
                'punchout':punchout,
                'location':location,
                'hours':int(hours),
                'minutes':int(minutes),
                'seconds':int(seconds),
                    "response":{
                        "n" : 1,
                        "msg" : "pass",
                        "status" : "success"
                    }
            }
            

    else:
        
        return {
                    'indatetime':'',
                    'outdatetime':'',
                    'data':'',
                    'intime':'',
                    'outtime':'',
                    'intimedate':'',
                    'outtimedate':'',
                    'punchout':'',
                    'location':'',
                        "response":{
                            "n" : 0,
                            "msg" : "user not found",
                            "status" : "errror"
                        }
                        }
      
def compoff_eligiblity(employeeId):
    current_date = date.today()
    yesterday_date = current_date - timedelta(days=1)
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    intime=''
    outtime=''
    intimedate=''
    outtimedate=''
    userobj = Users.objects.filter(employeeId=employeeId,is_active=True).first()
    if userobj is not None:   
        check_user_type=userobj.employeetype
        check_last_checkin = attendance.objects.filter(employeeId=str(employeeId),date=str(current_date),checkout=False).order_by('time').last()
        check_last_checkout=None
        if check_last_checkin is not None:
            check_last_checkout = attendance.objects.filter(employeeId=str(employeeId),time__gt=check_last_checkin.time,date=str(current_date),checkout=True).order_by('time').last()

        else:
            check_last_checkin = attendance.objects.filter(employeeId=str(employeeId),date=str(yesterday_date),checkout=False).order_by('time').last()
            if check_last_checkin is not None:
                check_last_checkout = attendance.objects.filter(Q(employeeId=str(employeeId),time__gt=check_last_checkin.time,date=str(yesterday_date),checkout=True)|Q(employeeId=str(employeeId),date=str(current_date),checkout=True)).order_by('date','time').last()


        
        if check_last_checkin is not None :
            
            intime = check_last_checkin.time
            intimedate=check_last_checkin.date
            punchout = 0
            get_data=1
            outtime = ''
            outtimedate=''
        else:
            get_data=0
            punchout = 1
            intime = ''
            intimedate=''
            outtime = ''
            outtimedate=''
            
            
        if check_last_checkout is not None:
            
            outtime = check_last_checkout.time
            outtimedate=check_last_checkout.date
            punchout = 1
            get_data=0
 
        else:
            if check_last_checkin is not None :
                punchout = 0
                get_data=1
                outtime = ''
                outtimedate=''
            else:
                punchout = 1
                get_data=0
                outtime = ''
                outtimedate=''
                

        currentshiftname=''
        currentshiftstarttime=''
        currentshiftendtime=''
        currentshiftstartdate=''
        currentshiftenddate=''
        todays_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=employeeId,date=str(current_date),is_active=True)
        todays_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(todays_shiftallotment_objs,many=True)
        shiftId_list=list(todays_shiftallotment_serializers.data)
        shift_obj=ShiftMaster.objects.filter(id__in=shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
        shift_serializer=ShiftMasterSerializer(shift_obj,many=True)
        
        
         
        todays_runnningshift=gettodaysshift(shift_serializer.data,str(current_date))
        if todays_runnningshift['n'] == 1:
            currentshiftname=todays_runnningshift['data']['shiftname']
            currentshiftstarttime=str(todays_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
            currentshiftendtime=str(todays_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
            currentshiftstartdate=str(todays_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
            currentshiftenddate=str(todays_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
            
        elif todays_runnningshift['last_runingshift']['shiftstarttime'] !='':
            currentshiftname=todays_runnningshift['last_runingshift']['shiftname']
            currentshiftstarttime=str(todays_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
            currentshiftendtime=str(todays_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
            currentshiftstartdate=str(todays_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
            currentshiftenddate=str(todays_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
        
        else:
            yesterday_shiftallotment_objs=ShiftAllotment.objects.filter(attendanceId=employeeId,date=str(yesterday_date),is_active=True)
            yesterday_shiftallotment_serializers=ShiftAllotmentshiftIdSerializer(yesterday_shiftallotment_objs,many=True)
            shiftId_list=list(yesterday_shiftallotment_serializers.data)
            shift_obj=ShiftMaster.objects.filter(id__in=shiftId_list,is_active=True).exclude(intime='00:00',outtime='00:00').order_by('intime')
            yesterday_shift_serializer=ShiftMasterSerializer(shift_obj,many=True)
                
            
            yesterday_runnningshift=gettodaysshift(yesterday_shift_serializer.data,str(yesterday_date))
            if yesterday_runnningshift['n'] == 1:
                currentshiftname=yesterday_runnningshift['data']['shiftname']
                currentshiftstarttime=str(yesterday_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftendtime=str(yesterday_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftstartdate=str(yesterday_runnningshift['data']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                currentshiftenddate=str(yesterday_runnningshift['data']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                
            elif yesterday_runnningshift['last_runingshift']['shiftstarttime'] !='':
                currentshiftname=yesterday_runnningshift['last_runingshift']['shiftname']
                currentshiftstarttime=str(yesterday_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftendtime=str(yesterday_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[1]+':00'
                currentshiftstartdate=str(yesterday_runnningshift['last_runingshift']['shiftstarttime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
                currentshiftenddate=str(yesterday_runnningshift['last_runingshift']['shiftendtime'].strftime('%Y-%m-%d %H:%M')).split(' ')[0]
            else:
                currentshiftname='General'
                currentshiftstarttime='07:30:00'
                currentshiftendtime='18:30:00'
                currentshiftstartdate=str(current_date)
                currentshiftenddate=str(current_date)

        shiftdetails={
                    "shiftname":currentshiftname,
                    "shiftstarttime":currentshiftstarttime,
                    "shiftendtime":currentshiftendtime,
                    "shiftstartdate":currentshiftstartdate,
                    "shiftenddate":currentshiftenddate,
                }
        

        getallattendance = attendance.objects.filter(Q(employeeId=str(employeeId),time__gte=currentshiftstarttime,date=str(currentshiftstartdate))|Q(employeeId=str(employeeId),time__lte=str(current_datetime).split(' ')[1],date=str(current_datetime).split(' ')[0])).order_by('date','time')
        
 
        
        attendance_serializer=attendanceserializer(getallattendance,many=True)
        
        sorted_data = sorted(attendance_serializer.data, key=lambda x: (x['date'], x['time']))
        
        mindate = datetime.strptime(currentshiftstartdate, '%Y-%m-%d')
        mintime = datetime.strptime(currentshiftstarttime, '%H:%M:%S').time()

        sorted_data = [entry for entry in sorted_data if (datetime.strptime(entry['date'],'%Y-%m-%d').date() > mindate.date() or (datetime.strptime(entry['date'],'%Y-%m-%d').date() == mindate.date() and datetime.strptime(entry['time'], '%H:%M:%S').time() > mintime))]

        if len(sorted_data) > 0:
            intimedate=sorted_data[0]['date']
            intime=str(sorted_data[0]['time'])
            
        if intimedate !='' and intimedate is not None:
            user_sdt = datetime.strptime(str(intimedate) + ' ' + str(intime), '%Y-%m-%d %H:%M:%S')
            shif_sdt = datetime.strptime(str(currentshiftstartdate) + ' ' + str(currentshiftstarttime), '%Y-%m-%d %H:%M:%S')
            if user_sdt < shif_sdt :
                intimedate=''
                intime=''
                outtime=''
                outtimedate=''

                
        checkin_time = None
        total_working_time = 0
        for index, entry in enumerate(sorted_data):
            if entry['checkout']:
                if checkin_time:
                    checkout_datetime = datetime.strptime(entry['date'] + ' ' + entry['time'], '%Y-%m-%d %H:%M:%S')
                    checkin_datetime = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
                    working_time = checkout_datetime - checkin_datetime
                    total_working_time += working_time.total_seconds()
                    checkin_time = None
            elif not entry['checkout']:
                checkin_time = entry['date'] + ' ' + entry['time']

         
        if checkin_time and index == len(sorted_data) - 1:
            checkout_datetime = datetime.now()
            checkin_datetime = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S')
            working_time = checkout_datetime - checkin_datetime
            total_working_time += working_time.total_seconds()


         
        hours, remainder = divmod(total_working_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        current_shift_start_datetime = datetime.strptime(shiftdetails['shiftstartdate'] + ' ' + shiftdetails['shiftstarttime'], '%Y-%m-%d %H:%M:%S')
        current_shift_end_datetime = datetime.strptime(shiftdetails['shiftenddate'] + ' ' + shiftdetails['shiftendtime'], '%Y-%m-%d %H:%M:%S')
        shift_total_working_hrs = current_shift_end_datetime - current_shift_start_datetime
        shift_total_working_hrs -= timedelta(hours=2) 
        current_shift_start_datetime += timedelta(hours=2)

        if intime is not None and intime !='' and intimedate is not None and intimedate !='':
            current_user_checkin_datetime = datetime.strptime(intimedate + ' ' + intime, '%Y-%m-%d %H:%M:%S')
            if current_user_checkin_datetime > (current_shift_start_datetime + timedelta(minutes=30)):
                LateMark=True
            else:
                LateMark=False    
            present=True
        else:
            present=False
            LateMark=False  

        current_shift_details={
            'shiftname':shiftdetails['shiftname'],
            'current_shift_start_datetime':current_shift_start_datetime,
            'current_shift_end_datetime':current_shift_end_datetime,
        }
        
        total_hrs=str(add_leading_zero(int(hours))) +':' +str(add_leading_zero(int(minutes))) +':'+str(add_leading_zero(int(seconds)))
        fifteen_hours= timedelta(hours=15)
        nine_hours = timedelta(hours=9)
        over_time=False
        eligible=False
        work_duration = datetime.strptime(total_hrs, '%H:%M:%S') - datetime.strptime('00:00:00', '%H:%M:%S')
        if work_duration > nine_hours:
            if outtime == '' or outtime is None:
                over_time=True

        if work_duration > fifteen_hours:
            eligible=True

        return {
            'total_hrs':total_hrs,
            'in_time':intime,
            'out_time':outtime,
            'in_date':intimedate,
            'out_date':outtimedate,
            'shift_details':current_shift_details,
            'present':present,
            'LateMark':LateMark,
            'over_time':over_time,
            'eligible':eligible,
            "response":{
                "n" : 1,
                "msg" : "pass",
                "status" : "success"
            }
            }
        

    else:
        
        return  {

                    'total_hrs':'',
                    'in_time':'',
                    'out_time':'',
                    'in_date':'',
                    'out_date':'',
                    'shift_details':{},
                    'present':False,
                    'LateMark':False,
                    'over_time':False,
                    'eligible':False,
                    "response":{
                        "n" : 0,
                        "msg" : "user not found",
                        "status" : "errror"
                    }
                }
      
def ddmonthyy(date):
    import datetime
    date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
    formatted_date = date.strftime("%d %B %Y")
    return formatted_date

def dateformat_ddmmyy(datestr):
    date_object = datetime.strptime(datestr, '%Y-%m-%d')
    formatted_date = date_object.strftime('%d-%m-%Y')
    return(formatted_date)

def is_weeklyoff(date):
    date = datetime.strptime(date, "%Y-%m-%d").date()
    if date.weekday() == 6:
        return ({"data":[],"response":{"n" : 0,"msg" : "Request of date "+dateformat_ddmmyy(str(date))+" Fall on Weekly off Sunday","status" : "warning"}})
    if date.weekday() == 5: 
        week_number = (date.day - 1) // 7 + 1
        if week_number == 2 or week_number == 4:
            return ({"data":[],"response":{"n" : 0,"msg" : "Request of date "+dateformat_ddmmyy(str(date))+" Fall on Weekly off saturday","status" : "warning"}})
        
def validate_leave_rules(EmployeeId,company_code,LeaveTypeId,StartDate,EndDate,StartDayLeaveType,EndDayLeaveType,AttachmentStatus):
    current_date = date.today()

    employee_obj=Users.objects.filter(id=EmployeeId,company_code=company_code,is_active=True).first()
    if employee_obj is not None:
        packet_mapping_obj=PacketEmployeeMapping.objects.filter(EmployeeId=EmployeeId,company_code=company_code,is_active=True).first()
        if packet_mapping_obj is not None:
            packet_obj=PacketMaster.objects.filter(id=packet_mapping_obj.PacketId,is_active=True,company_code=company_code).first()
            if packet_obj is not None:
                PacketId=packet_obj.id
                print("LeaveTypeId",LeaveTypeId,company_code)
                leave_type_obj=LeaveTypeMaster.objects.filter(id=LeaveTypeId,company_code=company_code,is_active=True).first()


                if leave_type_obj is not None:
                    LeaveTypeId=leave_type_obj.id
                    packet_rules_obj=PacketLeaveRules.objects.filter(company_code=company_code,PacketId=PacketId,LeaveTypeId=LeaveTypeId).first()
                    if packet_rules_obj is not None:
                        start_date = datetime.strptime(StartDate, '%Y-%m-%d').date()
                        end_date = datetime.strptime(EndDate, '%Y-%m-%d').date()
                        print("start_date",start_date)
                        print("end_date",end_date)
                        if start_date > end_date:
                            return {
                                    'n': 0,
                                    'msg': f"Start date must be greater than equal to end date",
                                    'status': 'error'
                                }

                        if packet_rules_obj.Rule2:
                            if packet_rules_obj.ApplicableEmployements !='All':
                                if employee_obj.employeementStatus != packet_rules_obj.ApplicableEmployements:
                                    return {'n':0,'msg':'this leave type is not applicable to you.','status':'error'}

                        if packet_rules_obj.Rule5:
                            if start_date > current_date:
                                future_date_difference = (start_date - current_date).days
                                if future_date_difference > int(packet_rules_obj.ApplyUptoFuture):
                                    return {
                                        'n': 0,
                                        'msg': f"This leave type can only be applied up to {packet_rules_obj.ApplyUptoFuture} days in advance.",
                                        'status': 'error'
                                    }

                        if packet_rules_obj.Rule6:
                            if start_date < current_date:
                                past_date_difference = abs(start_date - current_date).days   
                                if past_date_difference > int(packet_rules_obj.ApplyUptoPast):
                                    return {
                                        'n': 0,
                                        'msg': f"This leave type can only be applied up to {packet_rules_obj.ApplyUptoPast} days in the past.",
                                        'status': 'error'
                                    }

                        if packet_rules_obj.Rule7:
                            if start_date > current_date:
                                current_date_difference = abs(start_date - current_date).days   
                                if current_date_difference < int(packet_rules_obj.ApplyBefore):
                                    return {
                                        'n': 0,
                                        'msg': f"This leave type can only be applied before {packet_rules_obj.ApplyBefore} days.",
                                        'status': 'error'
                                    }
                        
                        if packet_rules_obj.Rule8:
                            number_of_leave_days=calculate_total_leave_days(StartDate, StartDayLeaveType, EndDate, EndDayLeaveType)
                            if int(number_of_leave_days) > int(packet_rules_obj.LeaveLongerThan):
                                if packet_rules_obj.AttachmentRequired:
                                    if AttachmentStatus == False:
                                        return {
                                            'n': 0,
                                            'msg': f"Please provide valid attachments for leave",
                                            'status': 'error'
                                        }
                            
                        if packet_rules_obj.Rule9:
 
                            weekly_off_dates = []
                            
                            
                            shift_allotmet_obj=ShiftAllotment.objects.filter(employeeId=EmployeeId,is_active=True,date=StartDate,shift_name__in=['weekly off','weeklyoff']).first()
                            if shift_allotmet_obj is None:
                                shift_allotmet_obj=ShiftAllotment.objects.filter(employeeId=EmployeeId,is_active=True,date=EndDate,shift_name__in=['weekly off','weeklyoff']).first()



                            if shift_allotmet_obj is not None:
                                weekly_off_dates.append(StartDate)
                                if weekly_off_dates:
                                    return {
                                        'n': 0,
                                        'msg': f"Leave cannot be applied on these weekly off days: {', '.join(str(d) for d in weekly_off_dates)}",
                                        'status': 'error'
                                    }


                            else:
 

                                if is_weekly_off(start_date,packet_rules_obj):
                                        return {
                                            'n': 0,
                                            'msg': f"Leave cannot start on a weekly off day ({start_date}).",
                                            'status': 'error'
                                        }
                                
                                if is_weekly_off(end_date,packet_rules_obj):
                                    return {
                                        'n': 0,
                                        'msg': f"Leave cannot end on a weekly off day ({end_date}).",
                                        'status': 'error'
                                    }



                            



                        start_holiday = Holidays.objects.filter(
                                Date=start_date,
                                company_code=company_code,
                                Active=True
                            ).first()

                        
                        end_holiday = Holidays.objects.filter(
                                Date=end_date,
                                company_code=company_code,
                                Active=True
                            ).first()

                        if start_holiday:
                            return {
                                    'n': 0,
                                    'msg': f"Leave cannot start on a holiday: {start_holiday.Date} ({start_holiday.Festival})",
                                    'status': 'error'
                                }

                        if end_holiday:
                            return {
                                    'n': 0,
                                    'msg': f"Leave cannot end on a holiday: {end_holiday.Date} ({end_holiday.Festival})",
                                    'status': 'error'
                                }

                        overlapping_leaves = Leave.objects.filter(
                                employeeId=EmployeeId,
                                company_code=company_code,
                                Active=True
                            ).filter(
                                start_date__lte=end_date,   
                                end_date__gte=start_date    
                            ).exclude(Q(leave_status='Draft')|Q(leave_status='Withdraw')|Q(leave_status='Rejected'))

                        for leave in overlapping_leaves:
                            existing_start = leave.start_date
                            existing_end = leave.end_date
                            existing_start_type = leave.startdayleavetype
                            existing_end_type = leave.enddayleavetype

                             
                            if existing_start == start_date and existing_end == end_date:
                                if (existing_start_type == StartDayLeaveType and existing_end_type == EndDayLeaveType) or \
                                (existing_start_type == 'Fullday' or StartDayLeaveType == 'Fullday') or \
                                (existing_end_type == 'Fullday' or EndDayLeaveType == 'Fullday'):
                                    return {
                                        'n': 0,
                                        'msg': "You have already applied for leave on these dates.",
                                        'status': 'error'
                                    }

                 
                            if start_date <= existing_end and start_date >= existing_start:
                                return {
                                    'n': 0,
                                    'msg': f"Your leave overlaps with an existing leave on {existing_start} to {existing_end}.",
                                    'status': 'error'
                                }

                           
                            if end_date >= existing_start and end_date <= existing_end:
                                return {
                                    'n': 0,
                                    'msg': f"Your leave overlaps with an existing leave on {existing_start} to {existing_end}.",
                                    'status': 'error'
                                }

                            
                            if existing_start <= start_date and existing_end >= end_date:
                                return {
                                    'n': 0,
                                    'msg': f"Your leave period is completely within an existing leave from {existing_start} to {existing_end}.",
                                    'status': 'error'
                                }

                             
                            if start_date <= existing_start and end_date >= existing_end:
                                return {
                                    'n': 0,
                                    'msg': f"Your leave period overlaps with an existing leave from {existing_start} to {existing_end}.",
                                    'status': 'error'
                                }

                        return {'n':1,'msg':'allow to apply','status':'success'}

                    else:
                        return {'n':0,'msg':'Leave rules are not set for the selected leave type in your package.','status':'error'}
                else:
                    return {'n':0,'msg':'The selected leave type is no longer available.','status':'error'}
            else:
                return {'n':0,'msg':'The assigned packet for the employee is no longer available.','status':'error'}
        else:
            return {'n':0,'msg':'The employee is not assigned to any packet.','status':'error'}
    else:
        return {'n':0,'msg':'user not found.','status':'error'}

def get_employee_leave_balance(EmployeeId, company_code, LeaveTypeId, Year, PacketLeaveCount):
    employee_obj = Users.objects.filter(id=EmployeeId, company_code=company_code, is_active=True).first()
    if not employee_obj:
        return {'n': 0, 'msg': 'User not found.', 'status': 'error', 'data': {}}

    leave_type_obj = LeaveTypeMaster.objects.filter(id=LeaveTypeId, company_code=company_code, is_active=True).first()
    if not leave_type_obj:
        return {'n': 0, 'msg': 'The selected leave type is no longer available.', 'status': 'error', 'data': {}}

    LeaveTypeId = leave_type_obj.id

     
    carry_forwarded_leave_counts_obj = CarryForwardedLeave.objects.filter(
        Year=Year, EmployeeId=EmployeeId, LeaveTypeId=LeaveTypeId, company_code=company_code, is_active=True
    ).first()
    
    carry_forwarded_leave_counts = carry_forwarded_leave_counts_obj.LeaveCount if carry_forwarded_leave_counts_obj else 0

     
    alloted_packet_leave_for_this_year = round(float(PacketLeaveCount) + float(carry_forwarded_leave_counts), 2)

     
    leaves = Leave.objects.filter(
        Q(employeeId=EmployeeId),
        Q(company_code=company_code),
        Q(LeaveTypeId=LeaveTypeId),  
        Q(start_date__year=Year) | 
        Q(end_date__year=Year) | 
        (Q(start_date__lte=date(Year, 12, 31)) & Q(end_date__gte=date(Year, 1, 1))),
        Active=True
    )

     
    leave_days_count = leaves.annotate(
        leave_day_count=Case(
            When(startdayleavetype="FullDay", enddayleavetype="FullDay", then=F('number_of_days')),
            When(startdayleavetype="FirstHalf", enddayleavetype="FirstHalf", then=F('number_of_days') - Value(0.5)),
            When(startdayleavetype="SecondHalf", enddayleavetype="SecondHalf", then=F('number_of_days') - Value(0.5)),
            When(startdayleavetype="FirstHalf", enddayleavetype="SecondHalf", then=F('number_of_days') - Value(1.0)),
            When(startdayleavetype="SecondHalf", enddayleavetype="FirstHalf", then=F('number_of_days') - Value(1.0)),
            When(startdayleavetype="FullDay", enddayleavetype="FirstHalf", then=F('number_of_days') - Value(0.5)),
            When(startdayleavetype="FullDay", enddayleavetype="SecondHalf", then=F('number_of_days') - Value(0.5)),
            default=F('number_of_days'),
            output_field=FloatField()
        )
    ).aggregate(total_leave_days=Sum('leave_day_count'))

     
    leave_taken_by_employee = leave_days_count['total_leave_days'] or 0

     
    leave_balance = round(alloted_packet_leave_for_this_year - leave_taken_by_employee, 2)
    show_leave_balance = max(leave_balance, 0)   

    data = {
        'show_leave_balance': show_leave_balance,
        'leave_balance': leave_balance,
        'leave_taken_by_employee': leave_taken_by_employee,
        'carry_forwarded_leave': carry_forwarded_leave_counts,
        'alloted_packet_leave_for_this_year': alloted_packet_leave_for_this_year,
    }

    return {'n': 1, 'msg': 'Leave balance found successfully.', 'status': 'success', 'data': data}




def calculate_total_leave_days(startdate, startdayleavetype, enddate, enddayleavetype):
     
    start_date = datetime.strptime(startdate, '%Y-%m-%d').date()
    end_date = datetime.strptime(enddate, '%Y-%m-%d').date()

     
    total_days = (end_date - start_date).days + 1   

     
    if startdayleavetype in ["FirstHalf", "SecondHalf"]:
        total_days -= 0.5   

    if enddayleavetype in ["FirstHalf", "SecondHalf"]:
        total_days -= 0.5   

    return total_days



def is_weekly_off(date,packet_rules_obj):
    """ Check if the given date is a weekly off """
    if packet_rules_obj.WeeklyOffConsider == '5':
         
        return date.weekday() in [5, 6]   

    elif packet_rules_obj.WeeklyOffConsider == '6' and packet_rules_obj.IfWeeklyOff6:
        if packet_rules_obj.WeeklyOffPattern == 'even':
            
            if date.weekday() == 6:  
                return True
            elif date.weekday() == 5:   
                week_num = (date.day - 1) // 7 + 1   
                return week_num in [2, 4]   

        elif packet_rules_obj.WeeklyOffPattern == 'odd':
             
            if date.weekday() == 6:   
                return True
            elif date.weekday() == 5:  
                week_num = (date.day - 1) // 7 + 1  
                return week_num in [1, 3, 5]   

    return False

def generate_leave_applicationid(employee_id):
    user_obj=Users.objects.filter(id=employee_id,is_active=True).first()
    if user_obj is not None:
        unique_id=user_obj.uid
        leave_objs = Leave.objects.filter(employeeId=employee_id).order_by('-id').exclude(ApplicationId=None)
        leaves_obj_serializer=leaveserializer(leave_objs,many=True)
            
        appnumberlist=[]
        for y in leaves_obj_serializer.data:
            number_obj = y['ApplicationId'].split("/")[3]
            appnumberlist.append(int(number_obj))
        if len(appnumberlist) < 1:
            Idnumber = "1"
            application_ID = str(year)+"/"+unique_id+"/"+Idnumber
            return application_ID
        else:
            maxnumber=int(max(appnumberlist))
            maxnumber=maxnumber+1
            Idnumber = str(maxnumber)
            application_ID =str(year)+"/"+unique_id+"/"+Idnumber
            return application_ID
    else:
        return None








































