from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [
    path('api/applyshiftrequest', v.applyshiftrequest, name='applyshiftrequest'),
    path('api/getempshifts', v.getempshifts, name='getempshifts'),

    path('api/addshiftmanagers', v.addshiftmanagers, name='addshiftmanagers'),
    path('api/shiftreqlist', v.shiftreqlist, name='shiftreqlist'),
    path('api/empshiftlist', v.empshiftlist, name='empshiftlist'),
    path('api/shiftaction', v.shiftaction, name='shiftaction'),

    path('api/get_manager_pending_shift_swap_applications', v.get_manager_pending_shift_swap_applications, name='get_manager_pending_shift_swap_applications'),
    path('api/get_manager_approved_shift_swap_applications', v.get_manager_approved_shift_swap_applications, name='get_manager_approved_shift_swap_applications'),
    path('api/get_manager_rejected_shift_swap_applications', v.get_manager_rejected_shift_swap_applications, name='get_manager_rejected_shift_swap_applications'),

    path('api/approve_shift_swap_applications', v.approve_shift_swap_applications, name='approve_shift_swap_applications'),
    path('api/reject_shift_swap_applications', v.reject_shift_swap_applications, name='reject_shift_swap_applications'),
    
]
