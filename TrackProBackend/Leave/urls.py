from os import name
from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [

    path('api/leaveapi', v.leaveapi, name='leaveapi'),
    path('api/apply_leave_api', v.apply_leave_api, name='apply_leave_api'),
    path('api/get_employee_leave_balance_api', v.get_employee_leave_balance_api, name='get_employee_leave_balance_api'),
    path('api/calculate_total_leave_days_api', v.calculate_total_leave_days_api, name='calculate_total_leave_days_api'),

    path('api/leaveListAPI', v.todays_applications_list, name='leaveListAPI'),
    path('api/UserleaveListAPI', v.UserleaveListAPI, name='UserleaveListAPI'),
    path('api/FilterleaveListAPI', v.FilterleaveListAPI, name='FilterleaveListAPI'),
    path('api/withdraw_application', v.withdraw_application, name='withdraw_application'),
    path('api/deleteleaveAPI', v.deleteleaveAPI, name='deleteleaveAPI'),
    path('api/getbyidleaveAPI/<int:id>', v.getbyidleaveAPI, name='getbyidleaveAPI'),
    path('api/updatebyidleaveAPI/<int:id>', v.updatebyidleaveAPI, name='updatebyidleaveAPI'),
    
    path('api/update_leave_api', v.update_leave_api, name='update_leave_api'),
    path('api/updatedrafyleaveAPI/<int:id>', v.updatedrafyleaveAPI, name='updatedrafyleaveAPI'),
    path('api/leave_mapping_emp_filter', v.leave_mapping_emp_filter, name='leave_mapping_emp_filter'),
    path('api/leave_history', v.leave_history, name='leave_history'),
    path('api/statusleaveAPI', v.statusleaveAPI, name='statusleaveAPI'),
    path('api/leavemappingAPI', v.leavemappingAPI, name='leavemappingAPI'),
    path('api/leavemappingJoinQuery', v.leavemappingJoinQuery, name='leavemappingJoinQuery'),
    path('api/leavemappinglistAPI', v.leavemappinglistAPI, name='leavemappinglistAPI'),
    path('api/mapped_managers', v.mapped_managers, name='mapped_managers'),
    path('api/leave_calculation', v.leave_calculation, name='leave_calculation'),
    path('api/leaverequestAPI', v.leaverequestAPI, name='leaverequestAPI'),
    path('api/leaveactionAPI', v.leaveactionAPI, name='leaveactionAPI'),
    path('api/reject_approved_application', v.reject_approved_application, name='reject_approved_application'),
    
    path('api/approve_rejected_application', v.approve_rejected_application, name='approve_rejected_application'),
    path('api/admin-leave-approved', v.AdminLeaveApprovedPostApi, name='leaveactionAPI'),
    path('api/get_filter_leaves', v.get_filter_applications, name='get_filter_leaves'),
    path('api/leave_user_emp_list', v.leave_user_emp_list, name='leave_user_emp_list'),
    path('api/Apply_Leave_Mapping', v.Apply_Leave_Mapping, name='Apply_Leave_Mapping'),
    path('api/employee_yearly_total_days', v.employee_yearly_total_days, name='employee_yearly_total_days'),
    path('api/dashboard_leave_card', v.dashboard_leave_card, name='dashboard_leave_card'),
    path('api/getattendancecount', v.getattendancecount, name='getattendancecount'),
    path('api/get_daily_attendance_by_month', v.get_daily_attendance_by_month, name='get_daily_attendance_by_month'),
    
    path('api/get_per_date_leaves_count', v.get_per_date_leaves_count, name='get_per_date_leaves_count'),
    path('api/getattendancebydate', v.getattendancebydate, name='getattendancebydate'),
    path('api/get_late_mark_attendance', v.get_late_mark_attendance, name='get_late_mark_attendance'),
    path('api/get_past_application', v.get_past_application, name='get_past_application'),
    path('api/employee_application_details', v.employee_application_details, name='employee_application_details'),
    path('api/get_late_count_per_month',v.get_late_count_per_month,name="get_late_count_per_month"),
    path('api/get_leaves_and_latemarks_by_date', v.get_leaves_and_latemarks_by_date, name='get_leaves_and_latemarks_by_date'),


    path('api/get_manager_pending_applications_requests',v.get_manager_pending_applications_requests, name='get_manager_pending_applications_requests'),
    path('api/get_manager_approved_applications_requests',v.get_manager_approved_applications_requests, name='get_manager_approved_applications_requests'),
    path('api/get_manager_rejected_applications_requests',v.get_manager_rejected_applications_requests, name='get_manager_rejected_applications_requests'),
    path('api/get_manager_expired_applications_requests',v.get_manager_expired_applications_requests, name='get_manager_expired_applications_requests'),
    path('api/get_manager_withdraw_applications_requests',v.get_manager_withdraw_applications_requests, name='get_manager_withdraw_applications_requests'),
    path('api/get_manager_all_applications_requests',v.get_manager_all_applications_requests, name='get_manager_all_applications_requests'),



    # unused
    path('api/get_filter_applications', v.get_filter_applications, name='get_filter_applications'),
    path('api/attendance_scheduler', v.attendance_scheduler, name='attendance_scheduler'),
    path('api/get_existing_applcation_dates', v.get_existing_applcation_dates, name='get_existing_applcation_dates'),
    
    path('api/leavemodulecronejob830Am', v.leavemodulecronejob830Am, name='leavemodulecronejob830Am'),
    path('api/leavemodulecronejob930Am', v.leavemodulecronejob930Am, name='leavemodulecronejob930Am'),
    path('api/previousdayleaves', v.previousdayleaves, name='previousdayleaves'),

    path('api/team_attendance_scheduler', v.team_attendance_scheduler, name='team_attendance_scheduler'),
    path('api/team_attendance_scheduler_for_month_year', v.team_attendance_scheduler_for_month_year, name='team_attendance_scheduler_for_month_year'),
    path('api/team_attendance_scheduler_by_date', v.team_attendance_scheduler_by_date, name='team_attendance_scheduler_by_date'),

    path('api/get_all_emp_attendance_by_date', v.get_all_emp_attendance_by_date, name='get_all_emp_attendance_by_date'),
    path('api/get_sift_emp_attendance_by_date', v.get_sift_emp_attendance_by_date, name='get_sift_emp_attendance_by_date'),
    path('api/get_sift_emp_attendance_and_task_by_date', v.get_sift_emp_attendance_and_task_by_date, name='get_sift_emp_attendance_and_task_by_date'),
    
    path('api/get_alloted_shift_header_details', v.get_alloted_shift_header_details, name='get_alloted_shift_header_details'),
    path('api/warning_shedular_9hr_after_checkin', v.warning_shedular_9hr_after_checkin, name='warning_shedular_9hr_after_checkin'),
    path('api/change_working_status', v.change_working_status, name='change_working_status'),
    path('api/mark_forced_system_checkout', v.mark_forced_system_checkout, name='mark_forced_system_checkout'),
    path('api/send_mail', v.send_mail, name='send_mail'),
    path('api/granted_compoff_list', v.granted_compoff_list, name='granted_compoff_list'),
    path('api/pagination_get_late_mark_attendance', v.pagination_get_late_mark_attendance.as_view(), name='pagination_get_late_mark_attendance'),
    path('api/latemarkexcelreport', v.latemarkexcelreport, name='latemarkexcelreport'),
    
    path('api/add_leave_type', v.add_leave_type, name='add_leave_type'),
    path('api/update_leave_type', v.update_leave_type, name='update_leave_type'),
    path('api/delete_leave_type', v.delete_leave_type, name='delete_leave_type'),
    path('api/get_leave_type_by_id', v.get_leave_type_by_id, name='get_leave_type_by_id'),
    path('api/get_leave_type_list', v.get_leave_type_list, name='get_leave_type_list'),
    





]
