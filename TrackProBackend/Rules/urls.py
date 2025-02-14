from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [
    path('LeaveRules', v.LeaveRulesAPI, name='LeaveRules'),
    path('AttendanceRules', v.AttendanceRulesAPI, name='AttendanceRules'),
    path('TrackProRules', v.TrackProRulesAPI, name='trackproRules'),
    path('dataruleslist',v.dataruleslist,name='dataruleslist'),

    path('addannouncement',v.addannouncement,name='addannouncement'),
    path('updateannouncement',v.updateannouncement,name='updateannouncement'),
    path('announcementlist',v.announcementlist,name='announcementlist'),
    path('deleteannouncement',v.deleteannouncement,name='deleteannouncement'),

    path('addnews',v.addnews,name='addnews'),
    path('updatenews',v.updatenews,name='updatenews'),
    path('newslist',v.newslist,name='newslist'),
    path('deletenews',v.deletenews,name='deletenews'),
]