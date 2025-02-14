from django.contrib import admin
from django.urls import path, include
from . import views as v
urlpatterns = [
    path('api/IntermediateTrackProResultList', v.IntermediateTrackProResultList,
         name="IntermediateTrackProResultList"),
    path('api/getIntermediateTrackProResult', v.getIntermediateTrackProResult, 
         name="getIntermediateTrackProResult"),
    path('api/addIntermediateTrackProResult', v.addIntermediateTrackProResult,
         name="addIntermediateTrackProResult"),
    path('api/deleteIntermediateTrackProResult', v.deleteIntermediateTrackProResult,
         name="deleteIntermediateTrackProResult"),
    path('api/updateIntermediateTrackProResult', v.updateIntermediateTrackProResult,
         name="updateIntermediateTrackProResult"),

    # get week ajax api
    path('api/trackproResultweekList', v.trackproResultweekList, name="trackproResultweekList"),
    # excludeuser
    path('api/excludeUserData', v.ExcludeUserData.as_view(), name="ExcludeUserData"),
    # rank
    path('api/rank', v.rank, name="rank"),
    # check if trackpro score/week number/emp id exists
    path('api/checktrackproscoreexists', v.CheckIfTrackProScoreExists,
         name="CheckIfTrackProScoreExists"),
    # dashboard last 5
    path('api/lastFive', v.lastFive, name='lastFive'),
    # Reccords
    path('api/getTask', v.getTask, name='getTask'),
    path('api/getParticualrEmployeeTask', v.getParticualrEmployeeTask, name='getParticualrEmployeeTask'),
    path('api/getlasttask', v.getlasttask, name='getlasttask'),
    path('api/getemployeelasttask', v.getemployeelasttask, name='getemployeelasttask'),
    path('api/getScore', v.getScore, name='getScore'),
    path('api/getTaskScore', v.getTaskScore, name='getTaskScore'),
    path('api/getTaskSubmit', v.getTaskSubmit, name='getTaskSubmit'),
    path('api/addParticualrIntermediateTrackProResult', v.addParticualrIntermediateTrackProResult, name='addParticualrIntermediateTrackProResult'),
    path('api/getYear', v.getYear, name='getYear'),
    path('api/report_by_project',v.report_by_project_name_three_tier, name='users_report'),
    path('api/Getemployeerankinfo',v.Getemployeerankinfo, name='Getemployeerankinfo'),

    path('api/trackprocheck_managerscheduler', v.trackprocheck_managerscheduler, name='trackprocheck_managerscheduler'),
    path('api/trackprocheck_employeescheduler', v.trackprocheck_employeescheduler, name='trackprocheck_employeescheduler'),
    path('api/trackprocheck_report', v.trackprocheck_report, name='trackprocheck_report'),
    path('api/testemail', v.testemail, name='testemail'),
    path('api/reportfinalsubmitapi', v.reportfinalsubmitapi, name='reportfinalsubmitapi'),
    path('api/gettaskassignbymodal', v.gettaskassignbymodal, name='gettaskassignbymodal'),
    path('api/updateassignby', v.updateassignby, name='updateassignby'),
#     path('api/get_trackpro_percentege_by_emp', v.get_trackpro_percentege_by_empid, name='get_trackpro_percentege_by_emp'),
    path('api/get_employee_working_history', v.get_employee_working_history, name='get_employee_working_history'),


]

