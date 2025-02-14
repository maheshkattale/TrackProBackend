from os import name
from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [

    path('api/add_packet', v.add_packet, name='add_packet'),
    path('api/update_packet', v.update_packet, name='update_packet'),
    path('api/delete_packet', v.delete_packet, name='delete_packet'),
    path('api/get_packet_by_id', v.get_packet_by_id, name='get_packet_by_id'),
    path('api/get_packet_list', v.get_packet_list, name='get_packet_list'),
    path('api/get_packet_mapped_employees', v.get_packet_mapped_employees, name='get_packet_mapped_employees'),

    path('api/apply_employees_packet_mapping', v.apply_employees_packet_mapping, name='apply_employees_packet_mapping'),
    path('api/apply_packet_rules', v.apply_packet_rules, name='apply_packet_rules'),
    path('api/get_packet_leave_rules', v.get_packet_leave_rules, name='get_packet_leave_rules'),






]
