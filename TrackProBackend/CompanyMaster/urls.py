from os import name
from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *


urlpatterns = [

    path('api/addcompanyAPI', v.addcompanyAPI, name='addcompanyAPI'),
    path('api/companylist', v.companylistAPI, name='companylist'),
    path('api/companybyid', v.companybyidAPI, name='companybyidAPI'),
    path('api/companybyidupdate', v.companybyidupdateAPI, name='companybyidupdateAPI'),
    path('api/deletecompanyAPI', v.deletecompanyAPI, name='deletecompanyAPI'),
    path('api/uploadpayslip', v.uploadpayslip, name='uploadpayslip'),
    path('api/getpaymentslip', v.getpaymentslip, name='getpaymentslip'),
    path('api/designationfileapi', v.designationfileapi, name='designationfileapi'),
    path('api/departmentfileapi', v.departmentfileapi, name='departmentfileapi'),
    path('api/excel-employee', v.addEmployeeExcel, name='addEmployeeExcel'),

    path('api/locationfileapi', v.locationfileapi, name='locationfileapi'),
    path('api/addBillingPeriod', v.AddBillingPeriod, name='AddBillingPeriod'),    
    path('api/updateplanperiod', v.updatePlanPeriod, name='updatePlanPeriod'),    
    path('api/billingPeriodlist', v.BillingPeriodlist, name='BillingPeriodlist'),    
    path('api/billingPeriodbyid', v.BillingPeriodbyid, name='BillingPeriodbyid'),    
    path('api/billingPerioddetails', v.billingPerioddetails, name='billingPerioddetails'),    
    path('api/addCompanytype', v.AddCompanytype, name='AddCompanytype'),    
    path('api/updateCompanyType', v.updateCompanyType, name='updateCompanyType'),    
    path('api/companytypelist', v.Companytypelist, name='Companytypelist'),    
    path('api/companyleadlist', v.Companyleadlist, name='Companyleadlist'),  
    path('api/delete_company_type', v.delete_company_type, name='delete_company_type'),

 
    path('api/addcompanypayment', v.addcompanypayment, name='addcompanypayment'),    
    path('api/companypaymentloglist', v.Companypaymentloglist, name='Companypaymentloglist'),    
    path('api/particualrcompanypaymentlog', v.particualrcompanypaymentlog, name='particualrcompanypaymentlog'),
    path('api/remindercompanylist', v.remindercompanylist, name='remindercompanylist'), 
    path('api/sendremindermail', v.sendremindermail, name='sendremindermail'), 
    path('api/sendactivereminder', v.sendActiveReminder, name='sendActiveReminder'), 

    path('api/companycountdashboard', v.companycountdashboard, name='companycountdashboard'),
    path('api/companypackages', v.companypackages, name='companypackages'),
    path('api/companyyearlyincome', v.CompanyYearlyIncome, name='CompanyYearlyIncome'),
    path('api/companyleadsgraph', v.CompanyLeadsGraph, name='CompanyLeadsGraph'),
    
]