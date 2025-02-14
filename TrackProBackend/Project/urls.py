
from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [
    # path('admin/', admin.site.urls),

    # API - Project
    path('api/projectLists', v.projectListAPI, name='Projectlistapis'),
    path('api/paginationprojectlist', v.paginationprojectlist.as_view(), name='paginationprojectlist'),
    # API - ProjectTasks
    path('api/projectTaskListAPI', v.projectTaskListAPI, name='projectTaskListAPI'),

    # Combined Project List
    path('api/projectlist', v.combinedProjectListApi, name='projectlistapi'),

    # CRUD
    path('api/addproject', v.addProject, name='addProject'),
    path('api/deleteproject', v.projectDelete, name='projectDelete'),
    path('api/updateproject', v.projectUpdate, name='projectUpdate'),

    # Search by id
    path('api/getproject', v.getProject, name='getProject'),

    # Project tasks Crud
    path('api/addprojecttask', v.addProjectTask, name='addProjectTask'),
    path('api/allProjectList', v.allProjectList, name='allProjectList'),
    # path('api/updateprojectask',v.updateProjectTask, name='updateProjectTask'),
    # path('api/holdProjectTask',v.holdProjectTask, name='holdProjectTask'),

    path('api/projectreport', v.projectreport.as_view(), name='projectreport'),
    path('api/projectreporttotaltasktime', v.projectreporttotaltasktime.as_view(), name='projectreporttotaltasktime'),

    path('api/excelprojectreport', v.excelprojectreport.as_view(), name='excelprojectreport'),
    path('api/searchproject', v.searchproject, name='searchproject'),

    #query 
    path('api/queryprojectlist', v.queryprojectlist, name='queryprojectlist'),
    path('api/querylocationlist', v.querylocationlist, name='querylocationlist'),
    path('api/querydepartmentlist', v.querydepartmentlist, name='querydepartmentlist'),
    path('api/queryuserdashboardlist', v.queryuserdashboardlist, name='queryuserdashboardlist'),
]
