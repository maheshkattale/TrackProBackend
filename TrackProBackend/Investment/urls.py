from django.contrib import admin
from django.urls import path, include
from . import views as v
from .views import *
urlpatterns = [

    # Section
    path('api/section', v.Addsection, name='Addsection'),
    path('api/sectionlist', v.getsectionlist, name='getsectionlist'),
    path('api/sectionbyid', v.sectionbyidAPI, name='sectionbyidAPI'),
    path('api/sectionupdate', v.sectionbyidupdateAPI, name='sectionbyidupdateAPI'),
    path('api/sectiondelete', v.sectiondeleteAPI, name='sectiondeleteAPI'),

    #Investment type
    path('api/InvestmentType', v.AddInvestmentType, name='AddInvestmentType'),
    path('api/typelist', v.listInvestmentType, name='listInvestmentType'),
    path('api/invtypelist', v.listInvestmentTypeById, name='listInvestmentTypeById'),
    path('api/typebyid', v.typelistbyidAPI, name='typelistbyidAPI'),
    path('api/typeupdate', v.InvtypebyidupdateAPI, name='InvtypebyidupdateAPI'),
    path('api/typedelete', v.InvtypedeleteAPI, name='InvtypedeleteAPI'),


    #Investment Disease
    path('api/AddDisease', v.AddInvDisease, name='AddInvDisease'),
    path('api/Diseaselist', v.InvDiseaselist, name='InvDiseaselist'),
    path('api/Diseasebyid', v.getdiseasebyid, name='getdiseasebyid'),
    path('api/UpdateDisease', v.updatedisease, name='updatedisease'),
    path('api/DeleteDisease', v.deletedisease, name='deletedisease'),

    #Investment Financial year
    path('api/AddFinYear', v.AddInvFinancialYear, name='AddInvFinancialYear'),
    path('api/FinYearlist', v.InvFinancialYearlist, name='InvFinancialYearlist'),
    path('api/FinYearbyid', v.getfinyearbyid, name='getfinyearbyid'),
    path('api/UpdateFinYear', v.updateFinYear, name='updateFinYear'),
    path('api/DeleteFinYear', v.deleteFinYear, name='deleteFinYear'),

    # Invetment Reasons
    path('api/AddReason', v.AddInvReasons, name='AddInvReasons'),
    path('api/Reasonlist', v.InvReasonslist, name='InvReasonslist'),
    path('api/Reasonbyid', v.getInvReasonsbyid, name='getfinyearbyid'),
    path('api/UpdateReason', v.updateReason, name='updateFinYear'),
    path('api/DeleteReason', v.deleteReason, name='deleteReason'),
    
    #Investment Files
    path('api/AddInvFiles', v.AddInvFiles, name='AddInvFiles'),
    path('api/InvFileslist', v.InvFileslist, name='InvFileslist'),
    path('api/InvFilesbyid', v.InvFilesbyid, name='InvFilesbyid'),
    path('api/UpdateInvFile', v.UpdateInvFiles, name='UpdateInvFiles'),
    path('api/deleteInvFiles', v.deleteInvFiles, name='deleteInvFiles'),


    #Investment file Details
    path('api/AddInvFileDetails', v.AddInvFile_Details, name='AddInvFile_Details'),
    path('api/InvFileDetailslist', v.InvFile_Detailslist, name='InvFileDetailslist'),
    path('api/InvFileDetailsbyid', v.InvFile_Detailsbyid, name='InvFileDetailsbyid'),
    path('api/UpdateInvFileDetails', v.UpdateInvFile_Details, name='UpdateInvFileDetails'),
    path('api/deleteInvFileDetails', v.deleteInvFile_Details, name='deleteInvFileDetails'),

   
    # Investment status master
    path('api/Addstatus', v.AddInvStatus, name='Addstatus'),
    path('api/statuslist', v.InvStatuslist, name='statuslist'),
    path('api/statusbyid', v.InvStatusbyid, name='statusbyid'),
    path('api/updatestatus', v.UpdateInvStatus, name='updatestatus'),
    path('api/deletestatus', v.deleteInvStatus, name='deletestatus'),

    # Investment proof status history
    path('api/Addstatushistory', v.AddproofStatus, name='Addstatushistory'),
    path('api/statushistorylist', v.InvProofstatushistorylist, name='statushistorylist'),
    path('api/statushistorybyid', v.InvProofStatusbyid, name='statushistorybyid'),
    path('api/statushistoryupdate', v.UpdateInvproofstatus, name='statushistoryupdate'),
    path('api/statushistorydelete', v.deleteInvproofstatus, name='statushistorydelete'),

    #claim deduction question
    path('api/Addclaimques', v.AddClaimDdeduction, name='Addclaimques'),
    path('api/claimquelist', v.ClaimDdeductionlist, name='claimquelist'),
    path('api/claimbyid', v.ClaimDdeductionbyid, name='claimbyid'),
    path('api/updateclaimque', v.UpdateClaimDdeduction, name='updateclaimque'),
    path('api/deleteclaimque', v.deleteInvproofstatus, name='deleteclaimque'),


    #Financial year slab
    path('api/Addslab', v.AddFinYearSlab, name='Addslab'),
    path('api/slablist', v.FinYearSlablist, name='slablist'),
    path('api/slabbyid', v.FinYearSlabbyid, name='slabbyid'),
    path('api/updateslab', v.UpdateFinYearSlab, name='updateslab'),
    path('api/deleteslab', v.deleteFinYearSlab, name='deleteslab'),


    #Investment OnOff
    path('api/AddOnOff', v.AddInvOnOFF, name='AddOnOff'),
    path('api/OnOfflist', v.InvOnOFFlist, name='OnOfflist'),
    path('api/OnOffbyid', v.OnOFFlistbyid, name='OnOffbyid'),
    path('api/updateOnOff', v.UpdateOnOFFlist, name='updateOnOff'),
    path('api/deleteOnOff', v.deleteOnOFFlist, name='deleteOnOff'),

    #Investment payroll configuration-
    path('api/Addpayrollconf', v.Addpayrollconfig, name='Addpayrollconf'),
    path('api/payrollconflist', v.payrollconfiglist, name='payrollconflist'),
    path('api/payrollconfbyid', v.payrollconfigbyid, name='payrollconfbyid'),
    path('api/updatepayrollconf', v.updatepayrollconfig, name='updatepayrollconf'),
    path('api/deletepayrollconf', v.deletepayrollconfig, name='deletepayrollconf'),

    #Investment payrollconfig employee
    path('api/Addpayrollemp', v.Addpayrollconfig_emp, name='Addpayrollemp'),
    path('api/payrollemplist', v.payrollconfig_emplist, name='payrollemplist'),
    path('api/payrollempbyid', v.payrollconfig_empbyid, name='payrollempbyid'),
    path('api/updatepayrollemp', v.updatepayrollconfig_emp, name='updatepayrollemp'),
    path('api/deletepayrollemp', v.deletepayrollconfig_emp, name='deletepayrollemp'),


    #Inv members
    path('api/Addmember', v.AddInvMembers, name='Addmember'),
    path('api/memberlist', v.InvMemberslist, name='memberlist'),
    path('api/memberbyid', v.InvMemberbyid, name='memberbyid'),
    path('api/updatemember', v.updateInvMember, name='updatemember'),
    path('api/deletemember', v.deleteInvMember, name='deletemember'),


    #Investment Members Audit
    path('api/Addmemberaudit', v.AddMembersAudit, name='Addmemberaudit'),
    path('api/MembersAuditlist', v.MembersAuditlist, name='MembersAuditlist'),
    path('api/MembersAuditbyid', v.MembersAuditbyid, name='MembersAuditbyid'),
    path('api/updateMembersAudit', v.updateMembersAudit, name='updateMembersAudit'),
    path('api/deleteMembersAudit', v.deleteMembersAudit, name='deleteMembersAudit'),

    #Investment  Member Tasks
    path('api/AddMembersTask', v.AddMembersTask, name='AddMembersTask'),
    path('api/MembersTasklist', v.MembersTasklist, name='MembersTasklist'),
    path('api/MembersTaskbyid', v.MembersTaskbyid, name='MembersTaskbyid'),
    path('api/updateMembersTask', v.updateMembersTask, name='updateMembersTask'),
    path('api/deleteMembersTask', v.deleteMembersTask, name='deleteMembersTask'),


    # Investment Proof Entry
    path('api/AddProofEntry', v.AddProofEntry, name=''),
    path('api/ProofEntrylist', v.ProofEntrylist, name=''),
    path('api/ProofEntrybyid', v.ProofEntrybyid, name=''),
    path('api/updateProofEntry', v.updateProofEntry, name=''),
    path('api/deleteProofEntry', v.deleteProofEntry, name=''),


    # Investment proof entry audit
    path('api/Addproofaudit', v.AddProofEntryAudit, name=''),
    path('api/Proofauditlist', v.ProofEntryAuditlist, name=''),
    path('api/ProofAuditbyid', v.ProofEntryAuditbyid, name=''),
    path('api/UpdateProofAudit', v.updateProofEntryAudit, name=''),
    path('api/DeleteProofAudit', v.deleteProofEntryAudit, name=''),

    #Rent Details
    path('api/AddRent', v.AddRentDetails, name=''),
    path('api/Rentlist', v.RentDetailslist, name=''),
    path('api/Rentbyid', v.RentDetailsbyid, name=''),
    path('api/Rentupdate', v.updateRentDetails, name=''),
    path('api/Rentdelete', v.deleteRentDetails, name=''),

    path('api/addInvLandlord', v.AddInvLandlord, name='AddInvLandlord'),
    path('api/Invlandlordlist', v.Invlandlordlist, name='Invlandlordlist'),
    path('api/getInvlandlordbyid', v.getInvlandlordbyid, name='getInvlandlordbyid'),
    path('api/updateInvLandlord', v.updateInvLandlord, name='updateInvLandlord'),

    path('api/addInvLender', v.AddInvLender, name='AddInvLender'),
    path('api/InvLenderlist', v.InvLenderlist, name='InvLenderlist'),
    path('api/getInvLenderbyid', v.getInvLenderbyid, name='getInvLenderbyid'),
    path('api/updateInvLender', v.updateInvLender, name='updateInvLender'),

    path('api/addProofBatch', v.AddProofBatch, name='AddProofBatch'),
    path('api/InvProofBatchlist', v.InvProofBatchlist, name='InvProofBatchlist'),
    path('api/getInvProofBatchbyid', v.getInvProofBatchbyid, name='getInvProofBatchbyid'),
    path('api/updateInvProofBatch', v.updateInvProofBatch, name='updateInvProofBatch'),

    #Configuration
    path('api/addConfiguration', v.addConfiguration, name='addConfiguration'),
    path('api/fieldTypeList', v.fieldTypeList, name='fieldTypeList'),
]