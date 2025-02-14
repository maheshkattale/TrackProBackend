"""
URL configuration for TrackProBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('Users.urls')),
    path('leave/', include('Leave.urls')),
    path('department/',include('Department.urls')),
    path('project/',include('Project.urls')),
    path('tasks/', include('Tasks.urls')),   
    path('checktrackpro/',include('CheckTrackPro.urls')),
    path('company/', include('CompanyMaster.urls')),
    path('rules/', include('Rules.urls')),
    path('Investment/', include('Investment.urls')),
    path('ClientMaster/', include('ClientMaster.urls')),
    path('Shift/', include('Shift.urls')),
    path('packet/', include('Packet.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

