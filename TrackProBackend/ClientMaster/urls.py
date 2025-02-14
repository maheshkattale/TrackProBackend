from django.contrib import admin
from django.urls import path, include
from . import views as v

urlpatterns = [
    # path('admin/', admin.site.urls),

    # API - Client Master 
    path('api/clientlist',v.clientlist, name = 'clientlist'),
    path('api/addclient', v.addclient, name = 'addclient'),
    path('api/deleteclient', v.deleteclient, name='deleteclient'),
    path('api/updateclient', v.updateclient, name='updateclient'),
    path('api/getclient', v.getclient, name='getclient'),

    # API - ClientsideManager Master 
    path('api/ClientsideManagerlist',v.ClientsideManagerlist, name = 'ClientsideManagerlist'),
    path('api/addClientsideManager', v.addClientsideManager, name = 'addClientsideManager'),
    path('api/deleteClientsideManager', v.deleteClientsideManager, name='deleteClientsideManager'),
    path('api/updateClientsideManager', v.updateClientsideManager, name='updateClientsideManager'),
    path('api/getClientsideManager', v.getClientsideManager, name='getClientsideManager'),

    #API - createclient master
    path('api/createClient', v.createClient, name = 'createClient'),
    path('api/createClientlist', v.createClientlist, name = 'createClientlist'),
    path('api/getCreateClient', v.getCreateClient, name = 'getCreateClient'),
    path('api/deleteCreateClient', v.deleteCreateClient, name = 'deleteCreateClient'),
    path('api/updateCreateClient', v.updateCreateClient, name = 'updateCreateClient'),

    #API - Event master
    path('api/AddEvent', v.AddEvent, name = 'AddEvent'),
    path('api/Eventlist', v.Eventlist, name = 'Eventlist'),
    path('api/getEvent', v.getEvent, name = 'getEvent'),
    path('api/updateEvent', v.updateEvent, name = 'updateEvent'),
    path('api/deleteEvent', v.deleteEvent, name = 'deleteEvent'),


     #API - client-projects master
    path('api/AddClient_project', v.AddClient_project, name = 'AddClient_project'),
    path('api/Client_Projectlist', v.Client_Projectlist, name = 'Client_Projectlist'),
    # path('api/GetClient_project', v.GetClient_project, name = 'GetClient_project'),
    path('api/updateClient_project', v.updateClient_project, name = 'updateClient_project'),
    # path('api/deleteClient_project', v.deleteClient_project, name = 'deleteClient_project'),
    path('api/deleteclientproject', v.deleteclientproject, name='deleteclientproject'),

]