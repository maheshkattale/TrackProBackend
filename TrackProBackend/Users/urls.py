from os import name
from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [
    

    # path('admin/', admin.site.urls),

    path('api/api-key', v.ApiKeygenerate, name='ApiKeygenerate'),
    path('api/login', v.login, name='login'),
    path('api/logout', v.logout, name='logout'),

    path('api/passwordupdate', v.passwordUpdate, name='passwordupdate'),
    # chk if email exists
    path('api/chkemail', v.chkEmailExists, name='chkEmailExists'),
    # reset password
    path('api/resetpassword', v.resetPassword, name='resetPassword'),

    # API - User - userlist
    path('api/userlist', v.UserListAPI, name='userlistapi'),
    path('api/adduser', v.addUser, name='addUser'),
    # path('api/adduser', addUser.as_view(), name = 'addUser'),

    path('api/userdelete', v.userDelete, name='userdelete'),
    path('api/userblock', v.userBlock, name='userblock'),
    path('api/userunblock', v.userUnblock, name='userUnblock'),
    path('api/userupdate', v.userUpdate, name='userupdate'),
    path('api/getuser', v.getUser, name='getUser'),
    path('api/getuserdetails', v.getUserDetailsForSecondaryInfo, name='getUser'),

    # role
    path('api/rolelist', v.RoleListAPI, name='RoleListAPI'),
    path('api/addrole', v.addRole, name='addRole'),
    path('api/updaterole', v.updateRole, name='updateRole'),
    path('api/getrole', v.getRole, name='getRole'),
    path('api/deleteroleapi', v.deleteroleapi, name='deleteroleapi'),
    path('api/editrolenameapi', v.editrolenameapi, name='editrolenameapi'),
    path('api/updatemultipleroleapi', v.updatemultipleroleapi, name='updatemultipleroleapi'),


    

    # Designation
    path('api/designationlist', v.DesignationListAPI, name='DesignationListAPI'),
    path('api/adddesignation', v.addDesignationAPI, name='addDesignationAPI'),
    path('api/updatedesignation', v.updateDesignation, name='updateDesignation'),
    path('api/getdesignation', v.getDesignation, name='getDesignation'),
    path('api/delete_designation', v.delete_designation, name='delete_designation'),
    path('api/deletelocation', v.deletelocation, name='deletelocation'),

    # Location
    path('api/locationlist', v.LocationListAPI, name='LocationListAPI'),
    path('api/addlocation', v.addLocation, name='addLocation'),
    path('api/updatelocation', v.updateLocation, name='updateLocation'),
    path('api/getlocation', v.getLocation, name='getLocation'),

    # Financial Year
    path('api/financialyearlist', v.FinYearListAPI, name='FinYearListAPI'),
    path('api/addfinyear', v.addFinYear, name='addFinYear'),
    path('api/updatefinyear', v.updateFinYear, name='updateFinYear'),
    path('api/getfinyear', v.getFinYear, name='getFinYear'),

    # Mapping
    path('api/mappinglist', v.mappingListAPI, name='mappingListAPI'),
    path('api/addmapping', v.addMapping, name='addMapping'),
    path('api/updatemapping', v.updateMapping, name='updateMapping'),
    path('api/getmapping', v.getMapping, name='getMapping'),
    path('api/basegetMapping', v.basegetMapping, name='basegetMapping'),
    path('api/getMappingForUpdate', v.getMappingForUpdate,
         name='getMappingForUpdate'),
    path('api/ManagerUserListAPI', v.ManagerUserListAPI, name='ManagerUserListAPI'), 
    path('api/deleteMapping', v.deleteMappingForManager,
         name='deleteMappingForManager'),
    path('api/mappingJoinQuery', v.mappingJoinQuery, name='mappingJoinQuery'),


    # Permission
    path('api/permissionlist', v.PermissionListAPI, name='PermissionListAPI'),
    path('api/addpermission', v.addPermissions, name='addPermissions'),
    path('api/deletepermission', v.deletePermission, name='deletePermission'),
    path('api/getPermission', v.getPermission, name='getPermission'),

    path('api/menuitem', v.MenuitemListAPI, name='MenuitemListAPI'),
    path('api/rolepermissionlist', v.rolepermissionlist, name='rolepermissionlist'),
    path('api/addduplicateroleapi', v.addduplicateroleapi, name='addduplicateroleapi'),
    

    # check if authenticated
    path('api/authenticate', v.chkLoggedIn, name='chkLoggedIn'),
# ----------------------------------------------------------------------------
    # dashboard details for employee
    path('api/dashboarddata', v.dashboarddata, name='dashboarddata'),
    # dashboard for admin
    path('api/admindashboarddata', v.Admindashboarddata, name='Admindashboarddata'),
    # dashboard for users
    path('api/usersdashboard', v.usersDashboard, name='usersDashboard'),

# attendance ------------------------------------------------------------------
    path('api/newfiledata', v.newfiledata, name="newfiledata"),
    path('api/appendfiledata', v.appendfiledata, name="appendfiledata"),
    path('api/monthlydata', v.monthlydata, name="monthlydata"),

    path('api/usercheckininfo', v.usercheckininfo, name="usercheckininfo"),
    path('api/punch_indata',v.punch_indata,name="punch_indata"),
    path('api/punch_outdata',v.punch_outdata,name="punch_outdata"),
    path('api/punch_getdata',v.punch_getdata,name="punch_getdata"),
    path('api/punchout_scheduler',v.punchout_scheduler,name="punchout_scheduler"),
    path('api/attendancerequestapi',v.attendancerequestapi,name="attendancerequestapi"),
    path('api/getatt_request',v.getatt_request,name="getatt_request"),
    path('api/manageratt_request',v.manageratt_request,name="manageratt_request"),
    path('api/getemp_requestapi',v.getemp_requestapi,name="getemp_requestapi"),
    path('api/updateattendancerequestreason',v.updateattendancerequestreason,name="updateattendancerequestreason"),
    path('api/cancelattendancerequest',v.cancelattendancerequest,name="cancelattendancerequest"),
    path('api/Attendance_mangreminder',v.Attendance_mangreminder,name="Attendance_mangreminder"),


    path('api/addSecondaryInfo',v.addSecondaryInfo,name="addSecondaryInfo"),
    path('api/geteducatiopnalqualificationsbyemail',v.geteducatiopnalqualificationsbyemail,name="geteducatiopnalqualificationsbyemail"),
    path('api/getSecondaryInfo',v.getSecondaryInfo,name="getSecondaryInfo"),
    path('api/getSecondaryInfofordocumentverification',v.getSecondaryInfofordocumentverification,name="getSecondaryInfofordocumentverification"),
    path('api/geteducatiopnalqualifications',v.geteducatiopnalqualifications,name="geteducatiopnalqualifications"),
    path('api/getpreviouscompany',v.getpreviouscompany,name="getpreviouscompany"),
    path('api/update-personal-details-secondary-info',v.updatePersonalDetailsSecondaryInfo,name="update-personal-details-secondary-info"),
    path('api/update-employe-details-secondary-info',v.updateEmployeDetailsSecondaryInfo,name="update-employe-details-secondary-info"),
    path('api/updatecompanydetailssecondaryInfo',v.updatecompanydetailssecondaryInfo,name="updatecompanydetailssecondaryInfo"),
    path('api/add_educational_details',v.add_educational_details,name="add_educational_details"),
    path('api/add_user_previous_company',v.add_user_previous_company,name="add_user_previous_company"),
    path('api/get_user_previous_company',v.get_user_previous_company,name="get_user_previous_company"),
    path('api/edit_user_previous_company',v.edit_user_previous_company,name="edit_user_previous_company"),
    path('api/delete_user_previous_company',v.delete_user_previous_company,name="delete_user_previous_company"),



    path('api/update-details-and-document',v.updateDetailsAndDocument,name="update-details-and-document"),
    path('api/secondary-info-link',v.secondaryInfoLinkApi,name="secondary-info-link"),
    path('add-attendance',v.addAttendance,name="add-attendance"),
    path('api/uploadattendance',v.uploadattendance,name="uploadattendance"),


    path('api/employee_calendar', v.employee_calendar, name='employee_calendar'),
    path('api/yearlist', v.yearlist, name='yearlist'),
    path('api/monthlist', v.monthlist, name='monthlist'),
    
# leave ------------------------------------------------------------------

    path('api/checkAttendanceData', v.checkAttendanceData, name='checkAttendanceData'),
    path('api/weeklypercentdata', v.weeklypercentdata, name='weeklypercentdata'),
    path('api/teamtrackerdataapi', v.teamtrackerdataapi, name='teamtrackerdataapi'),
    path('api/team_tracker_by_department_api', v.team_tracker_by_department_api, name='team_tracker_by_department_api'),
    
    path('api/attstatisticsapi', v.attstatisticsapi, name='attstatisticsapi'),
    path('api/rankcardapi', v.rankcardapi, name='rankcardapi'),


    # check if forgot password token has expired
    path('api/checkIfForgotPasswordToken', v.checkIfForgotPasswordToken,
         name='checkIfForgotPasswordToken'),

    # employyee filter added
    path('api/employee_filter', v.employee_filter, name='employee_filter'),
    # employee list by secondary info
    path('api/employee_master_emp_list', v.employee_master_emp_list, name='employee_master_emp_list'),
    path('api/user_emp_list', v.user_emp_list, name='user_emp_list'),
    # apply leave mapping




    #admin dashboard
    path('api/locationcountdata', v.locationcountdata, name='locationcountdata'),
    path('api/allempbdaydata', v.allempbdaydata, name='allempbdaydata'),
    path('api/adminmnholidayapi', v.adminmnholidayapi, name='adminmnholidayapi'),
    path('api/adminmonthlyscoreapi', v.adminmonthlyscoreapi, name='adminmonthlyscoreapi'),
    path('api/admin_attoverview_api', v.admin_attoverview_api, name='admin_attoverview_api'),
    path('api/admin_employee_weekatt_api', v.admin_employee_weekatt_api, name='admin_employee_weekatt_api'),
    path('api/admin_attlist', v.admin_attlist, name='admin_attlist'),
    path('api/admin_attmodaldata', v.admin_attmodaldata, name='admin_attmodaldata'),
    path('api/admintodaysstatus_api', v.admintodaysstatus_api, name='admintodaysstatus_api'),
    path('api/sch_attendancelistapi', v.sch_attendancelistapi, name='sch_attendancelistapi'),
    path('api/admin_getattlist', v.admin_getattlist, name='admin_getattlist'),

    #holidays master
    path('api/add_holidays', v.add_holidays, name="add_holidays"),
    path('api/update_holidays', v.update_holidays, name="update_holidays"),
    path('api/get_holidaydata', v.get_holidaydata, name="get_holidaydata"),
    path('api/get_holidaylistdata', v.get_holidaylistdata, name="get_holidaylistdata"),
    path('api/get_holidaybyid', v.get_holidaybyid, name="get_holidaybyid"),
    path('api/delete_holidays', v.delete_holidays, name="delete_holidays"),

    #notifications 
    path('api/notfapproveactionapi', v.notfapproveactionapi, name='notfapproveactionapi'),
    path('api/notfrejectactionapi', v.notfrejectactionapi, name='notfrejectactionapi'),
    path('api/notffilterlistapi', v.notffilterlistapi, name='notffilterlistapi'),
    # path('api/notffiltergetlistapi', v.notffiltergetlistapi, name='notffiltergetlistapi'),
    path('api/notfdatecheckcronejob', v.notfdatecheckcronejob, name='notfdatecheckcronejob'),
    path('api/notftypelist', v.notftypelist, name='notftypelist'),
    path('api/accept-document', v.acceptDocument, name='accept-document'),
    path('api/rejected-document', v.rejectedDocument, name='rejected-document'),
    path('api/admin_Attendancelist',v.attendance_data.as_view(), name='post'),
    path('api/m_notfcount',v.m_notfcount, name='m_notfcount'),
  
    
    path('api/EmployeeList', v.EmployeeList, name='EmployeeList'),
    path('api/search_by_name_employee', v.search_by_name_employee, name='search_by_name_employee'),
    path('api/search_emp_by_id', v.search_emp_by_id, name='search_emp_by_id'),


    path('api/onboardinglist', v.onboardinglist, name='onboardinglist'),
    path('api/onboard_login_password', v.onboard_login_password, name='onboard_login_password'),


    path('api/late_empscheduler', v.late_empscheduler, name='late_empscheduler'),
    path('api/late_manager_scheduler', v.late_manager_scheduler, name='late_manager_scheduler'),

    path('api/taskmanagercheck', v.taskmanagercheck, name='taskmanagercheck'),
    path('api/getcitiesbystateid',v.getcitiesbystateid,name="getcitiesbystateid"),
    path('api/getstatesbycountryid',v.getstatesbycountryid,name="getstatesbycountryid"),
    path('api/getecountries',v.getecountries,name="getecountries"),
    path('api/getcountrystatebycityid',v.getcountrystatebycityid,name="getcountrystatebycityid"),
    path('api/searchcity',v.searchcity,name="searchcity"),
    path('api/addcountry',v.addcountry,name="addcountry"),

    path('api/updateprofile_otpmail',v.updateprofile_otpmail,name="updateprofile_otpmail"),
    path('api/updatemyprofile',v.updatemyprofile,name="updatemyprofile"),


    path('api/Employee_allinfo',v.Employee_allinfo,name="Employee_allinfo"),
    path('api/Employee_all_info_by_id',v.Employee_all_info_by_id,name="Employee_all_info_by_id"),
    path('api/sendonboardinglink', v.sendonboardinglink, name='sendonboardinglink'),
    path('api/Employee_educational_qualification',v.Employee_educational_qualification,name="Employee_educational_qualification"),

    path('api/update_employee_first_step',v.update_employee_first_step,name="update_employee_first_step"),

    path('api/update_employee_second_step',v.update_employee_second_step,name="update_employee_second_step"),
    
    path('api/update_employee_fourth_step',v.update_employee_fourth_step,name="update_employee_fourth_step"),
    path('api/update_employee_fifth_step',v.update_employee_fifth_step,name="update_employee_fifth_step"),


    #userdashboard
    path('api/getusedashboardata', v.getusedashboardata, name='getusedashboardata'),

    #leavescheduler

    path('api/search_by_name_employee', v.search_by_name_employee, name='search_by_name_employee'),
    path('api/search_emp_by_id', v.search_emp_by_id, name='search_emp_by_id'),
    path('api/checksession', v.checksession, name='checksession'),

    
    path('api/add_device_change_request', v.add_device_change_request, name='add_device_change_request'),
    path('api/devicechangerequestslist', v.devicechangerequestslist, name='devicechangerequestslist'),
    path('api/approveddevicechangerequestslist', v.approveddevicechangerequestslist, name='approveddevicechangerequestslist'),
    path('api/pendingdevicechangerequestslist', v.pendingdevicechangerequestslist, name='pendingdevicechangerequestslist'),
    path('api/rejecteddevicechangerequestslist', v.rejecteddevicechangerequestslist, name='rejecteddevicechangerequestslist'),
    path('api/approvedevicechangerequest', v.approvedevicechangerequest, name='approvedevicechangerequest'),
    path('api/reject_devicechangerequest', v.reject_devicechangerequest, name='reject_devicechangerequest'),


    #shift master

    path('api/add_shift', v.add_shift, name='add_shift'),
    path('api/get_all_shifts', v.get_all_shifts, name='get_all_shifts'),
    path('api/update_shift', v.update_shift, name='update_shift'),
    path('api/delete_shift', v.delete_shift, name='delete_shift'),

    path('api/get_shift_details', v.get_shift_details, name="get_shift_details"),
    path('api/get_all_empshiftsdetails', v.get_all_empshiftsdetails, name='get_all_empshiftsdetails'),
    path('api/add_empshiftdetails', v.add_empshiftdetails, name='add_empshiftdetails'),
    path('api/delete_empshiftdetails', v.delete_empshiftdetails, name='delete_empshiftdetails'),
    path('api/add_empshiftallotment', v.add_empshiftallotment, name='add_empshiftallotment'),
    path('api/bulkuploadshiftallotment', v.bulkuploadshiftallotment, name='bulkuploadshiftallotment'),
    path('api/get_all_alloted_shifts', v.get_all_alloted_shifts, name='get_all_alloted_shifts'),

    path('api/delete_empshiftallotment', v.delete_empshiftallotment, name='delete_empshiftallotment'),
    path('api/get_all_shifts_employees', v.get_all_shifts_employees, name='get_all_shifts_employees'),
    path('api/alloted_shifts_by_date', v.alloted_shifts_by_date, name='alloted_shifts_by_date'),
    path('api/emp_monthly_shift_details', v.employee_monthly_shift_details, name='emp_monthly_shift_details'),
    path('api/employee_monthly_shift_details',v.employee_monthly_shift_details, name='employee_monthly_shift_details'),

    path('api/paginationshiftallotmentlist', v.paginationshiftallotmentlist.as_view(), name='paginationshiftallotmentlist'),
    path('api/insertattendance', v.insertattendance, name='insertattendance'),
    path('api/updateattendance', v.updateattendance, name='updateattendance'),
    path('api/deleteattendance', v.deleteattendance, name='deleteattendance'),
    # path('api/get_attendance_by_time_and_date', v.get_attendance_by_time_and_date, name='get_attendance_by_time_and_date'),
    path('api/dashboardcalender', v.dashboardcalender, name='dashboardcalender'),
    path('api/monthly_attendance_report_shedular', v.monthly_attendance_report_shedular, name='monthly_attendance_report_shedular'),

    path('api/add_employeetype', v.add_employeetype, name='add_employeetype'),
    path('api/get_all_employeetype', v.get_all_employeetype, name='get_all_employeetype'),
    path('api/update_employeetype', v.update_employeetype, name='update_employeetype'),
    path('api/delete_employeetype', v.delete_employeetype, name='delete_employeetype'),
    path('api/get_employeetype_data', v.get_employeetype_data, name='get_employeetype_data'),

    path('api/Addtyperules',v.Addtyperules, name='Addtyperules'),
    path('api/gettyperules',v.gettyperules, name='gettyperules'),
    path('api/Updatetyperules',v.Updatetyperules, name='Updatetyperules'),
    path('api/delete_employee_type_rules',v.delete_employee_type_rules, name='delete_employee_type_rules'),


    path('api/shiftexcelreport',v.shiftexcelreport, name='shiftexcelreport'),
    path('api/attendanceexcelreport',v.attendanceexcelreport, name='attendanceexcelreport'),
    
    path('api/getemployeeallotedshift',v.getemployeeallotedshift, name='getemployeeallotedshift'),
    path('api/swapshift',v.swapshift, name='swapshift'),
    path('api/testgetshiftevents',v.testgetshiftevents, name='testgetshiftevents'),
    path('api/getshiftevents',v.getshiftevents, name='getshiftevents'),

    #warning mail
    path('api/getmailsubjectdata',v.getmailsubjectdata, name='getmailsubjectdata'),
    path('api/getmailhistorydata',v.getmailhistorydata, name='getmailhistorydata'),
    path('api/sendwarningmail',v.sendwarningmail, name='sendwarningmail'),
    path('api/chatgptconversion',v.chatgptconversion, name='chatgptconversion'),

    path('api/get_the_user_device_location',v.get_the_user_device_location, name='get_the_user_device_location'),
    path('api/pindepartment',v.pindepartment, name='pindepartment'),
    path('api/get_current_shift',v.get_current_shift, name='get_current_shift'),


    path('api/compoff_shedular',v.compoff_shedular, name='compoff_shedular'),

    path('api/get_user_available_compoff',v.get_user_available_compoff, name='get_user_available_compoff'),
    path('api/get_user_pending_compoff',v.get_user_pending_compoff, name='get_user_pending_compoff'),
    path('api/get_user_approved_compoff',v.get_user_approved_compoff, name='get_user_approved_compoff'),
    path('api/get_user_rejected_compoff',v.get_user_rejected_compoff, name='get_user_rejected_compoff'),
    path('api/get_user_expired_compoff',v.get_user_expired_compoff, name='get_user_expired_compoff'),
    path('api/get_user_withdraw_compoff',v.get_user_withdraw_compoff, name='get_user_withdraw_compoff'),
    path('api/get_user_reschedule_compoff',v.get_user_reschedule_compoff, name='get_user_reschedule_compoff'),

    path('api/claim_compoff',v.claim_compoff, name='claim_compoff'),
    path('api/change_claim_compoff_date',v.change_claim_compoff_date, name='change_claim_compoff_date'),
    path('api/withdraw_compoff',v.withdraw_compoff, name='withdraw_compoff'),

    path('api/get_manager_pending_compoff_requests',v.get_manager_pending_compoff_requests, name='get_manager_pending_compoff_requests'),
    path('api/get_manager_approved_compoff_requests',v.get_manager_approved_compoff_requests, name='get_manager_approved_compoff_requests'),
    path('api/get_manager_rejected_compoff_requests',v.get_manager_rejected_compoff_requests, name='get_manager_rejected_compoff_requests'),
    path('api/get_manager_expired_compoff_requests',v.get_manager_expired_compoff_requests, name='get_manager_expired_compoff_requests'),
    path('api/get_manager_withdraw_compoff_requests',v.get_manager_withdraw_compoff_requests, name='get_manager_withdraw_compoff_requests'),
    path('api/get_manager_reschedule_compoff_requests',v.get_manager_reschedule_compoff_requests, name='get_manager_reschedule_compoff_requests'),

    path('api/approve_compoff_requests',v.approve_compoff_requests, name='approve_compoff_requests'),
    path('api/reject_compoff_requests',v.reject_compoff_requests, name='reject_compoff_requests'),
    path('api/reschedule_compoff_requests',v.reschedule_compoff_requests, name='reschedule_compoff_requests'),


]

