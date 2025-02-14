from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [
    # path('admin/', admin.site.urls),
    # API - Department 
    path('api/departmentlist',v.departmentListAPI, name = 'departmentlistapi'),
    path('api/addepartment', v.addDepartment, name = 'addDepartment'),
    path('api/deletedepartment', v.departmentDelete, name='departmentDelete'),
    path('api/updatedepartment', v.departmentUpdate, name='departmentUpdate'),
    path('api/getdepartment', v.getDepartment, name='getDepartment'),
]
