from functools import partial
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from  Investment.serializers import *
from Investment.models import *
from Users.models import *
import json
# Create your views here.

#---------------------------------------------------section---------------------------------------------------------
@api_view(['POST'])
def Addsection(request):
    data={}
    user = request.user.id
    data['Name']=request.data.get('Name')
    data['Description']=request.data.get('Description')
    data['Tentative_limit']=request.data.get('Tentative_limits')
    data['Is_Active'] = request.POST.get('Is_Active')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = sectionserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Section Added Successfully",
            "status": "success"
        }
    })
    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg": "Section Error Adding Section",
            "status": "failure"
        }
    })

@api_view(['GET'])
def getsectionlist(request):
    sections = Section.objects.filter().order_by('id')
    serializer = sectionserializer(sections,many=True)
    return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Section List Displayed Successfully",
            "status": "success"
        }
    })
   
@api_view(['GET'])
def sectionbyidAPI(request):
    id = request.data.get('id')
    sectiondata = Section.objects.filter(id=id).first()
    if sectiondata is not None: 
        serializer = sectionserializer(sectiondata)
        return Response({
        "data":serializer.data,
        "response": {
            "n": 1,
            "msg": "id found",
            "status": "success"
        }
        })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "id not found",
                "status": "failed"
            }
            })
  
@api_view(['POST'])
def sectionbyidupdateAPI(request):
    data={}
    id = request.data.get('id')
    sectiondata = Section.objects.filter(id=id).first()
    if sectiondata is not None:
        user = request.data.get('userid')
        data['Name']=request.data.get('Name')
        data['Description']=request.data.get('Description')
        data['Tentative_limit']=request.data.get('Tentative_limits')
        data['Is_Active']=request.data.get('Is_Active')
        if data['Is_Active'] == '1':
            data['Is_Active'] = True
        else:
            data['Is_Active'] = False
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = sectionserializer(sectiondata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Section Has Been Updated Successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Section Error Updating Section",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": {},
        "response": {
            "n": 0,
            "msg":"id not found",
            "status": "failure"
        }
    })

@api_view(['POST'])
def sectiondeleteAPI(request):
    data={}
    id = request.data.get('id')
    sectiondata = Section.objects.filter(Is_Active=True,id=id).first()
    if sectiondata is not None:
        data['Is_Active']=False
        serializer = sectionserializer(sectiondata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": '',
            "response": {
                "n": 1,
                "msg": "Section Deleted Successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error deleting section",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg":"id not found",
            "status": "failure"
        }
    })

#------------------------------------------------Investment Type-------------------------------------------------------

@api_view(['POST'])
def AddInvestmentType(request):
    # requestdata=request.data
    data={}
    user = request.user.id
    data['sectionId']=request.data.get('sectionId')
    data['Name']=request.data.get('Name')
    data['Description']=request.data.get('Description')
    data['Max_limit']=request.data.get('Max_limit')
    data['ProofRequired']=request.data.get('ProofRequired')
    data['Exemption_Limit']=request.data.get('Exemption_Limit')
    data['DocRequired']=request.data.get('DocRequired')
    data['InvestmentSingleBatch']=request.data.get('InvestmentSingleBatch')
    data['SortOrder']=request.data.get('SortOrder')
    data['Invest_TypeCode']=request.data.get('Invest_TypeCode')
    data['ExemptSection']=request.data.get('ExemptSection')
    data['No_Projection']=request.data.get('No_Projection')
    data['Section']=request.data.get('Section')
    data['HideOnDeclaration']=request.data.get('HideOnDeclaration')
    data['NewTaxRegimeApp']=request.data.get('NewTaxRegimeApp')
    data['LTA_slabApplicable']=request.data.get('LTA_slabApplicable')
    data['Is_Active'] = request.POST.get('Is_Active')
    # if 'ProofRequired' in requestdata.keys():
    #     data['ProofRequired']

    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = investmentTypeserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Investment Type Added successfully",
            "status": "success"
        }
    })
    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg": "Error adding InvType",
            "status": "failure"
        }
    })

@api_view(['GET'])
def listInvestmentType(request):
    invtypes = InvestmentType.objects.all().order_by('id')
    serializer = listinvestmentTypeserializer(invtypes,many=True)
    return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Investment Type List Displayed Successfully",
            "status": "success"
        }
    })

@api_view(['GET'])
def listInvestmentTypeById(request):
    invtypes = InvestmentType.objects.all().order_by('id')
    serializer = investmentTypeserializer(invtypes,many=True)
    return Response({
        "data": serializer.data,
        "response": {
            "n": 1,
            "msg": "Investment Type List Displayed Successfully",
            "status": "success"
        }
    })
   
@api_view(['GET'])
def typelistbyidAPI(request):
    id = request.data.get('id')
    invdata = InvestmentType.objects.filter(id=id).first()
    if invdata is not None: 
        serializer = listinvestmentTypeserializer(invdata)
        return Response({
        "data":serializer.data,
        "response": {
            "n": 1,
            "msg": "Id Found",
            "status": "success"
        }
        })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "Id Not Found",
                "status": "failed"
            }
            })
  
@api_view(['POST'])
def InvtypebyidupdateAPI(request):
    data={}
    id = request.data.get('id')
    
    existdata = InvestmentType.objects.filter(id=id).first()
    if existdata is not None:
        user = request.user.id
        data['sectionId']=request.data.get('sectionId')
        data['Name']=request.data.get('Name')
        data['Description']=request.data.get('Description')
        data['Max_limit']=request.data.get('Max_limit')
        data['ProofRequired']=request.data.get('ProofRequired')
        data['Exemption_Limit']=request.data.get('Exemption_Limit')
        data['DocRequired']=request.data.get('DocRequired')
        data['InvestmentSingleBatch']=request.data.get('InvestmentSingleBatch')
        data['SortOrder']=request.data.get('SortOrder')
        data['Invest_TypeCode']=request.data.get('Invest_TypeCode')
        data['ExemptSection']=request.data.get('ExemptSection')
        data['No_Projection']=request.data.get('No_Projection')
        data['Section']=request.data.get('Section')
        data['HideOnDeclaration']=request.data.get('HideOnDeclaration')
        data['NewTaxRegimeApp']=request.data.get('NewTaxRegimeApp')
        data['LTA_slabApplicable']=request.data.get('LTA_slabApplicable')
        data['Is_Active']=request.data.get('Is_Active')
        
        data['CreatedBy']=user
        data['UpdatedBy']=user
        # usercode = Users.objects.filter(id=user).first()
        data['company_code']=request.user.company_code
        serializer = investmentTypeserializer(existdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Investment Type Has Been Updated Successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error updating type",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": '',
        "response": {
            "n": 0,
            "msg":"id not found",
            "status": "failure"
        }
    })

@api_view(['POST'])
def InvtypedeleteAPI(request):
    data={}
    id = request.data.get('id')
    invdata = InvestmentType.objects.filter(Is_Active=True,id=id).first()
    if invdata is not None:
        data['Is_Active']=False
        serializer = investmentTypeserializer(invdata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": '',
            "response": {
                "n": 1,
                "msg": "Investment Type Deleted Successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error deleting type",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": serializer.errors,
        "response": {
            "n": 0,
            "msg":"id not found",
            "status": "failure"
        }
    })

#----------------------------------------------Investment Disease----------------------------------------------

@api_view(['POST'])
def AddInvDisease(request):
    data={}
    user = request.user.id
    data['DiseaseName']=request.data.get('DiseaseName')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvDiseaseserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Disease Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Disease ","status": "Failure"}})



@api_view(['GET'])
def InvDiseaselist(request):
    disease = InvestmentDisease.objects.filter(Is_Active=True).order_by('id')
    serializer = InvDiseaseserializer(disease,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Disease list shown successfully","status": "success"}})


@api_view(['GET'])
def getdiseasebyid(request):
    Id = request.data.get('id')
    diseaseobj = InvestmentDisease.objects.filter(Is_Active=True,id=Id).first()
    if diseaseobj is not None:
        serializer = InvDiseaseserializer(diseaseobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Disease id found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updatedisease(request):
    data={}
    Id=request.data.get('id')
    diseaseobj = InvestmentDisease.objects.filter(Is_Active=True,id=Id).first()
    if diseaseobj is not None:
        user = request.user.id
        data['DiseaseName']=request.data.get('DiseaseName')
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvDiseaseserializer(diseaseobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Disease updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Disease id not found ","status": "Failure"}})

@api_view(['POST'])
def deletedisease(request):
    data={}
    Id=request.data.get('id')
    diseaseoj = InvestmentDisease.objects.filter(Is_Active=True,id=Id).first()
    if diseaseoj is not None:
        data['Is_Active']=False
        serializer = investmentTypeserializer(diseaseoj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Disease deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Disease id not found ","status": "Failure"}})


#InvestType Options------------------------------------------------------------------------------------------------------------------

@api_view(['POST'])
def AddInvTypeoptions(request):
    data={}
    data['InvestmentTypeId']=request.data.get('InvestmentTypeId')
    data['optionNo']=request.data.get('optionNo')
    data['optionText']=request.data.get('optionText')
    data['optionValue']=request.data.get('optionValue')
    data['company_code']=request.user.company_code
    serializer = InvTypeOptionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Option Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Option ","status": "Failure"}})

@api_view(['POST'])
def invtypeoptbyidupdateAPI(request):
    data={}
    id = request.data.get('id')
    invtypoptiondata = InvestmentTypeOptions.objects.filter(id=id).first()
    if invtypoptiondata is not None:
        # user = request.data.get('userid')
        data['InvestmentTypeId']=request.data.get('InvestmentTypeId')
        data['optionNo']=request.data.get('optionNo')
        data['optionText']=request.data.get('optionText')
        data['optionValue']=request.data.get('optionValue')
        data['company_code']=request.user.company_code
        serializer = InvTypeOptionSerializer(invtypoptiondata,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Option has been updated successfully",
                "status": "success"
            }
        })
        else:
            return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": "Error updating Option",
                "status": "failure"
            }
        })
    else:
        return Response({
        "data": {},
        "response": {
            "n": 0,
            "msg":"id not found",
            "status": "failure"
        }
    })


@api_view(['GET'])
def invtypeoptbyidAPI(request):
    id = request.data.get('id')
    invdata = InvestmentTypeOptions.objects.filter(id=id).first()
    if invdata is not None: 
        serializer = InvTypeOptionSerializer(invdata)
        return Response({
        "data":serializer.data,
        "response": {
            "n": 1,
            "msg": "id found",
            "status": "success"
        }
        })
    else:
        return Response({
            "data": '',
            "response": {
                "n": 0,
                "msg": "id not found",
                "status": "failed"
            }
            })

#Financial year--------------------------------------------------------------------------------------------

@api_view(['POST'])
def AddInvFinancialYear(request):
    data={}
    user = request.user.id
    data['FinancialYear']=request.data.get('FinancialYear')
    data['FinancialShort']=request.data.get('FinancialShort')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvFinancialYearserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Fin year Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding  ","status": "Failure"}})

@api_view(['GET'])
def InvFinancialYearlist(request):
    Finyear = InvestmentFinancialYear.objects.all().order_by('id')
    serializer = InvFinancialYearserializer(Finyear,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "FinYearlist shown successfully","status": "success"}})

@api_view(['GET'])
def getfinyearbyid(request):
    Id = request.data.get('id')
    finyearobj = InvestmentFinancialYear.objects.filter(Is_Active=True,id=Id).first()
    if finyearobj is not None:
        serializer = InvFinancialYearserializer(finyearobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Fin Year id found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updateFinYear(request):
    data={}
    Id=request.data.get('id')
    Finyearobj = InvestmentFinancialYear.objects.filter(Is_Active=True,id=Id).first()
    if Finyearobj is not None:
        user = request.user.id
        data['FinancialYear']=request.data.get('FinancialYear')
        data['FinancialShort']=request.data.get('FinancialShort')
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvFinancialYearserializer(Finyearobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Fin Year updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": " id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteFinYear(request):
    data={}
    Id=request.data.get('id')
    finyearobj = InvestmentFinancialYear.objects.filter(Is_Active=True,id=Id).first()
    if finyearobj is not None:
        data['Is_Active']=False
        serializer = InvFinancialYearserializer(finyearobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Fin Year deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Year id not found ","status": "Failure"}})

#-----------------------------------------Investment Reasons-----------------------------------------------------------
@api_view(['POST'])
def AddInvReasons(request):
    data={}
    user = request.user.id
    data['ReasonName']=request.data.get('ReasonName')
    data['ReasonDescription']=request.data.get('ReasonDescription')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvReasonsserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv Reasons Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Reasons ","status": "Failure"}})

@api_view(['GET'])
def InvReasonslist(request):
    reason = InvestmentReasons.objects.filter(Is_Active=True).order_by('id')
    serializer = InvReasonsserializer(reason,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv Reasons shown successfully","status": "success"}})

@api_view(['GET'])
def getInvReasonsbyid(request):
    Id = request.data.get('id')
    reasonobj = InvestmentReasons.objects.filter(Is_Active=True,id=Id).first()
    if reasonobj is not None:
        serializer = InvReasonsserializer(reasonobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv Reason found successfully","status": "success"}})
        serializer = InvFinancialYearserializer(finyearobj
        ,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Disease deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Disease id not found ","status": "Failure"}})


@api_view(['POST'])
def updateReason(request):
    data={}
    Id=request.data.get('id')
    reasonobj = InvestmentReasons.objects.filter(Is_Active=True,id=Id).first()
    if reasonobj is not None:
        user = request.user.id
        data['ReasonName']=request.data.get('ReasonName')
        data['ReasonDescription']=request.data.get('ReasonDescription')
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvReasonsserializer(reasonobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Reason updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": " id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteReason(request):
    data={}
    Id=request.data.get('id')
    reasonobj = InvestmentReasons.objects.filter(Is_Active=True,id=Id).first()
    if reasonobj is not None:
        data['Is_Active']=False
        serializer = InvReasonsserializer(reasonobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "reason deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "reason id not found ","status": "Failure"}})


#------------------------------------------ Investment_Files ------------------------------------------------------

@api_view(['POST'])
def AddInvFiles(request):
    data={}
    user = request.user.id
    data['UserId']=request.data.get('UserId')
    data['company_code']=request.user.company_code
    serializer = InvFilesSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv files Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Invfiles ","status": "Failure"}})

@api_view(['GET'])
def InvFileslist(request):
    filesobj = Investment_Files.objects.filter(Is_Active=True).order_by('id')
    serializer = InvFilesSerializer(filesobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Files shown successfully","status": "success"}})

@api_view(['GET'])
def InvFilesbyid(request):
    Id = request.data.get('id')
    filesobj = Investment_Files.objects.filter(Is_Active=True,id=Id).first()
    if filesobj is not None:
        serializer = InvFilesSerializer(filesobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv Reason found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def UpdateInvFiles(request):
    data={}
    Id = request.data.get('id')
    invfilesobj = Investment_Files.objects.filter(Is_Active=True,id=Id).first()
    if invfilesobj is not None:
        user = request.user.id
        data['UserId']=request.data.get('UserId')
        data['company_code']=request.user.company_code
        serializer = InvFilesSerializer(invfilesobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv files updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating Invfiles ","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def deleteInvFiles(request):
    data={}
    Id = request.data.get('id')
    invfilesobj = Investment_Files.objects.filter(Is_Active=True,id=Id).first()
    if invfilesobj is not None:
        data['Is_Active']=False
        serializer = InvFilesSerializer(invfilesobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Inv files deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Inv files id not found ","status": "Failure"}})


#---------------------------------------------Investment File Details----------------------------------------------------

@api_view(['POST'])
def AddInvFile_Details(request):
    data={}
    user = request.user.id
    data['UserId']=request.data.get('UserId')
    data['company_code']=request.user.company_code
    serializer = InvFile_DetailsSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv file details Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Inv file details ","status": "Failure"}})

@api_view(['GET'])
def InvFile_Detailslist(request):
    filesobj = Investment_FileDetails.objects.filter(Is_Active=True).order_by('id')
    serializer = InvFile_DetailsSerializer(filesobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment File details shown successfully","status": "success"}})

@api_view(['GET'])
def InvFile_Detailsbyid(request):
    Id = request.data.get('id')
    filesobj = Investment_FileDetails.objects.filter(Is_Active=True,id=Id).first()
    if filesobj is not None:
        serializer = InvFile_DetailsSerializer(filesobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv file details found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def UpdateInvFile_Details(request):
    data={}
    Id = request.data.get('id')
    invfilesobj = Investment_FileDetails.objects.filter(Is_Active=True,id=Id).first()
    if invfilesobj is not None:
        user = request.user.id
        data['UserId']=request.data.get('UserId')
        data['company_code']=request.user.company_code
        serializer = InvFile_DetailsSerializer(invfilesobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv file details updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating Inv file details ","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def deleteInvFile_Details(request):
    data={}
    Id = request.data.get('id')
    invfilesobj = Investment_FileDetails.objects.filter(Is_Active=True,id=Id).first()
    if invfilesobj is not None:
        data['Is_Active']=False
        serializer = InvFile_DetailsSerializer(invfilesobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Inv files deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Inv files id not found ","status": "Failure"}})


#-----------------------------------------------------Investment Status master---------------------------------------

@api_view(['POST'])
def AddInvStatus(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['CreatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvstatusSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv status Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Invstatus ","status": "Failure"}})

@api_view(['GET'])
def InvStatuslist(request):
    statusobj = InvestmentStatusMaster.objects.filter(Is_Active=True).order_by('id')
    serializer = InvstatusSerializer(statusobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment status shown successfully","status": "success"}})

@api_view(['GET'])
def InvStatusbyid(request):
    Id = request.data.get('id')
    statusobj = InvestmentStatusMaster.objects.filter(Is_Active=True,id=Id).first()
    if statusobj is not None:
        serializer = InvstatusSerializer(statusobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv status found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def UpdateInvStatus(request):
    data={}
    Id = request.data.get('id')
    invstatusobj = InvestmentStatusMaster.objects.filter(Is_Active=True,id=Id).first()
    if invstatusobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = InvstatusSerializer(invstatusobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv status updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating status ","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteInvStatus(request):
    data={}
    Id = request.data.get('id')
    invstatusobj = Investment_Files.objects.filter(Is_Active=True,id=Id).first()
    if invstatusobj is not None:
        data['Is_Active']=False
        serializer = InvFilesSerializer(invstatusobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Inv status deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Inv status id not found ","status": "Failure"}})

#----------------------------------------Investment Proofstatushistory-------------------------------------------

@api_view(['POST'])
def AddproofStatus(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['company_code']=request.user.company_code
    serializer = InvProofStatusHistorySerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv proofstatushistory Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Invstatus ","status": "Failure"}})


@api_view(['GET'])
def InvProofstatushistorylist(request):
    statusobj = ProofStatusHistory.objects.filter(Is_Active=True).order_by('id')
    serializer = InvProofStatusHistorySerializer(statusobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment proofstatushistory shown successfully","status": "success"}})


@api_view(['GET'])
def InvProofStatusbyid(request):
    Id = request.data.get('id')
    statusobj = ProofStatusHistory.objects.filter(Is_Active=True,id=Id).first()
    if statusobj is not None:
        serializer = InvProofStatusHistorySerializer(statusobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv status found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def UpdateInvproofstatus(request):
    data={}
    Id = request.data.get('id')
    invstatusobj = ProofStatusHistory.objects.filter(Is_Active=True,id=Id).first()
    if invstatusobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = InvProofStatusHistorySerializer(invstatusobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Inv status updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating status ","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def deleteInvproofstatus(request):
    data={}
    Id = request.data.get('id')
    invstatusobj = ProofStatusHistory.objects.filter(Is_Active=True,id=Id).first()
    if invstatusobj is not None:
        data['Is_Active']=False
        serializer = InvProofStatusHistorySerializer(invstatusobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Inv proofstatushistory deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Inv proofstatushistory id not found ","status": "Failure"}})



#----------------------------------Investment claim deduction questions------------------------------------------------------

@api_view(['POST'])
def AddClaimDdeduction(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = ClaimDeductionSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "claim questions Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding questions ","status": "Failure"}})

@api_view(['GET'])
def ClaimDdeductionlist(request):
    claimobj = ClaimDeductionQuestions.objects.filter(Is_Active=True).order_by('id')
    serializer = ClaimDeductionSerializer(claimobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "claim questions shown successfully","status": "success"}})

@api_view(['GET'])
def ClaimDdeductionbyid(request):
    Id = request.data.get('id')
    claimobj = ClaimDeductionQuestions.objects.filter(Is_Active=True,id=Id).first()
    if claimobj is not None:
        serializer = ClaimDeductionSerializer(claimobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "claim question found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def UpdateClaimDdeduction(request):
    data={}
    Id = request.data.get('id')
    claimobj = ClaimDeductionQuestions.objects.filter(Is_Active=True,id=Id).first()
    if claimobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = ClaimDeductionSerializer(claimobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "claim question updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating claim question ","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteInvproofstatus(request):
    data={}
    Id = request.data.get('id')
    claimobj = ClaimDeductionQuestions.objects.filter(Is_Active=True,id=Id).first()
    if claimobj is not None:
        data['Is_Active']=False
        serializer = ClaimDeductionSerializer(claimobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "claim question deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting claim question","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#--------------------------------------Investment_LTA Financial Year Slab---------------------------------------------

@api_view(['POST'])
def AddFinYearSlab(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['UpdatedBy']=user
    data['CreatedBy']=user
    data['company_code']=request.user.company_code
    serializer = FinYearSlabSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "finyear slab Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding slab ","status": "Failure"}})

@api_view(['GET'])
def FinYearSlablist(request):
    slabobj = Investment_LTAFinYearSlab.objects.filter(Is_Active=True).order_by('id')
    serializer = FinYearSlabSerializer(slabobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "finyear slab shown successfully","status": "success"}})

@api_view(['GET'])
def FinYearSlabbyid(request):
    Id = request.data.get('id')
    slabobj = Investment_LTAFinYearSlab.objects.filter(Is_Active=True,id=Id).first()
    if slabobj is not None:
        serializer = FinYearSlabSerializer(slabobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "finyear slab found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def UpdateFinYearSlab(request):
    data={}
    Id = request.data.get('id')
    slabobj = Investment_LTAFinYearSlab.objects.filter(Is_Active=True,id=Id).first()
    if slabobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        data['UpdatedBy']=user
        serializer = FinYearSlabSerializer(slabobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "finyear slab updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating finyear slab","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteFinYearSlab(request):
    data={}
    Id = request.data.get('id')
    slabobj = Investment_LTAFinYearSlab.objects.filter(Is_Active=True,id=Id).first()
    if slabobj is not None:
        data['Is_Active']=False
        serializer = FinYearSlabSerializer(slabobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "finyear slab deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting finyear slab","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#---------------------------------------------------Investment On Off ---------------------------------------------------------------------------------

@api_view(['POST'])
def AddInvOnOFF(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['UpdatedBy']=user
    data['CreatedBy']=user
    data['company_code']=request.user.company_code
    serializer = OnOffSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "invOnOff Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding invOnOff ","status": "Failure"}})

@api_view(['GET'])
def InvOnOFFlist(request):
    onoffobj = Investment_OnOff.objects.filter(Is_Active=True).order_by('id')
    serializer = OnOffSerializer(onoffobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "invOnOff shown successfully","status": "success"}})

@api_view(['GET'])
def OnOFFlistbyid(request):
    Id = request.data.get('id')
    onoffobj = Investment_OnOff.objects.filter(Is_Active=True,id=Id).first()
    if onoffobj is not None:
        serializer = OnOffSerializer(onoffobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "invOnOff found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def UpdateOnOFFlist(request):
    data={}
    Id = request.data.get('id')
    onoffobj = Investment_OnOff.objects.filter(Is_Active=True,id=Id).first()
    if onoffobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        data['UpdatedBy']=user
        serializer = OnOffSerializer(onoffobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "invOnOff updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating invOnOff","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteOnOFFlist(request):
    data={}
    Id = request.data.get('id')
    onoffobj = Investment_OnOff.objects.filter(Is_Active=True,id=Id).first()
    if onoffobj is not None:
        data['Is_Active']=False
        serializer = OnOffSerializer(onoffobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "invOnOff deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting invOnOff","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#-------------------------------------Investment payroll configuration--------------------------------------------------------------------------------------------

@api_view(['POST'])
def Addpayrollconfig(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['UpdatedBy']=user
    data['CreatedBy']=user
    data['company_code']=request.user.company_code
    serializer = PayrollConfigSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding payrollconfig ","status": "Failure"}})

@api_view(['GET'])
def payrollconfiglist(request):
    payrollobj = InvestmentPayrollConfig.objects.filter(Is_Active=True).order_by('id')
    serializer = PayrollConfigSerializer(payrollobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig list shown successfully","status": "success"}})

@api_view(['GET'])
def payrollconfigbyid(request):
    Id = request.data.get('id')
    payrollobj = InvestmentPayrollConfig.objects.filter(Is_Active=True,id=Id).first()
    if payrollobj is not None:
        serializer = PayrollConfigSerializer(payrollobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updatepayrollconfig(request):
    data={}
    Id = request.data.get('id')
    payrollobj = InvestmentPayrollConfig.objects.filter(Is_Active=True,id=Id).first()
    if payrollobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = PayrollConfigSerializer(payrollobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating invOnOff","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deletepayrollconfig(request):
    data={}
    Id = request.data.get('id')
    payrollobj = InvestmentPayrollConfig.objects.filter(Is_Active=True,id=Id).first()
    if payrollobj is not None:
        data['Is_Active']=False
        serializer = PayrollConfigSerializer(payrollobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "payrollconfig deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting payrollconfig","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


#-------------------------------Investment payrollconfig employee--------------------------------------------------------------------------------------

@api_view(['POST'])
def Addpayrollconfig_emp(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['CreatedBy']=user
    data['company_code']=request.user.company_code
    serializer = PayrollConfig_empSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig_emp Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding payrollconfig_emp ","status": "Failure"}})


@api_view(['GET'])
def payrollconfig_emplist(request):
    payrollobj = InvestmentPayrollConfig_Employee.objects.filter(Is_Active=True).order_by('id')
    serializer = PayrollConfig_empSerializer(payrollobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig_emp list shown successfully","status": "success"}})

@api_view(['GET'])
def payrollconfig_empbyid(request):
    Id = request.data.get('id')
    payrollobj = InvestmentPayrollConfig_Employee.objects.filter(Is_Active=True,id=Id).first()
    if payrollobj is not None:
        serializer = PayrollConfig_empSerializer(payrollobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig_emp found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def updatepayrollconfig_emp(request):
    data={}
    Id = request.data.get('id')
    payrollobj = InvestmentPayrollConfig_Employee.objects.filter(Is_Active=True,id=Id).first()
    if payrollobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = PayrollConfig_empSerializer(payrollobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "payrollconfig_emp updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating payrollconfig_emp","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deletepayrollconfig_emp(request):
    data={}
    Id = request.data.get('id')
    payrollobj = InvestmentPayrollConfig_Employee.objects.filter(Is_Active=True,id=Id).first()
    if payrollobj is not None:
        data['Is_Active']=False
        serializer = PayrollConfig_empSerializer(payrollobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "payrollconfig_emp deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting payrollconfig_emp","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})



#---------------------------------------------Investment Members--------------------------------------------------------------------------------------------
@api_view(['POST'])
def AddInvMembers(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvMembersSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Investment Member ","status": "Failure"}})


@api_view(['GET'])
def InvMemberslist(request):
    invobj = InvestmentMembers.objects.filter(Is_Active=True).order_by('id')
    serializer = InvMembersSerializer(invobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Members list shown successfully","status": "success"}})


@api_view(['GET'])
def InvMemberbyid(request):
    Id = request.data.get('id')
    invobj = InvestmentMembers.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        serializer = InvMembersSerializer(invobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updateInvMember(request):
    data={}
    Id = request.data.get('id')
    invobj = InvestmentMembers.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = InvMembersSerializer(invobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating Investment Member","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteInvMember(request):
    data={}
    Id = request.data.get('id')
    invobj = InvestmentMembers.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        data['Is_Active']=False
        serializer = InvMembersSerializer(invobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Investment Member deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting Investment Member","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#----------------------------------------------Investment Members Audit--------------------------------------------------------------------------------------

@api_view(['POST'])
def AddMembersAudit(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvMembersAuditSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Audit Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Investment Member Audit ","status": "Failure"}})


@api_view(['GET'])
def MembersAuditlist(request):
    invobj = InvestmentMembersAudit.objects.filter(Is_Active=True).order_by('id')
    serializer = InvMembersAuditSerializer(invobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Audit list shown successfully","status": "success"}})


@api_view(['GET'])
def MembersAuditbyid(request):
    Id = request.data.get('id')
    invobj = InvestmentMembersAudit.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        serializer = InvMembersAuditSerializer(invobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Audit found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updateMembersAudit(request):
    data={}
    Id = request.data.get('id')
    invobj = InvestmentMembersAudit.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvMembersAuditSerializer(invobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Audit updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating Investment Member Audit","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteMembersAudit(request):
    data={}
    Id = request.data.get('id')
    invobj = InvestmentMembersAudit.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        data['Is_Active']=False
        serializer = InvMembersAuditSerializer(invobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Investment Member Audit deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting Investment Member Audit","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#---------------------------------------Investment Member Tasks-----------------------------------------------------------------------------------------------------------


@api_view(['POST'])
def AddMembersTask(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['company_code']=request.user.company_code
    serializer = memberTasksSerializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Task Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Investment Member Task ","status": "Failure"}})

@api_view(['GET'])
def MembersTasklist(request):
    taskobj = Investment_MemberTasks.objects.filter(Is_Active=True).order_by('id')
    serializer = memberTasksSerializer(taskobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Task list shown successfully","status": "success"}})


@api_view(['GET'])
def MembersTaskbyid(request):
    Id = request.data.get('id')
    taskobj = Investment_MemberTasks.objects.filter(Is_Active=True,id=Id).first()
    if taskobj is not None:
        serializer = memberTasksSerializer(taskobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Task found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def updateMembersTask(request):
    data={}
    Id = request.data.get('id')
    invobj = Investment_MemberTasks.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = memberTasksSerializer(invobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Investment Member Task updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating Investment Member Task","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteMembersTask(request):
    data={}
    Id = request.data.get('id')
    invobj = Investment_MemberTasks.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        data['Is_Active']=False
        serializer = memberTasksSerializer(invobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Investment Member Task deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting Investment Member Task","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#------------------------------------Proof Entry---------------------------------------------------------------------------------------------------------

@api_view(['POST'])
def AddProofEntry(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['company_code']=request.user.company_code
    serializer = ProofEntryserializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding ProofEntry ","status": "Failure"}})

@api_view(['GET'])
def ProofEntrylist(request):
    taskobj = ProofEntry.objects.filter(Is_Active=True).order_by('id')
    serializer = ProofEntryserializer(taskobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry list shown successfully","status": "success"}})


@api_view(['GET'])
def ProofEntrybyid(request):
    Id = request.data.get('id')
    taskobj = ProofEntry.objects.filter(Is_Active=True,id=Id).first()
    if taskobj is not None:
        serializer = ProofEntryserializer(taskobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def updateProofEntry(request):
    data={}
    Id = request.data.get('id')
    invobj = ProofEntry.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = ProofEntryserializer(invobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating ProofEntry","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteProofEntry(request):
    data={}
    Id = request.data.get('id')
    invobj = ProofEntry.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        data['Is_Active']=False
        serializer = ProofEntryserializer(invobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "ProofEntry deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting ProofEntry","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


#--------------------------------------------------Rent Details----------------------------------------------------------------------------------


@api_view(['POST'])
def AddRentDetails(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['company_code']=request.user.company_code
    serializer = RentDetailsserializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Rent Details Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Rent Details ","status": "Failure"}})

@api_view(['GET'])
def RentDetailslist(request):
    rentobj = RentDetails.objects.filter(Is_Active=True).order_by('id')
    serializer = RentDetailsserializer(rentobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Rent Details list shown successfully","status": "success"}})

@api_view(['GET'])
def RentDetailsbyid(request):
    Id = request.data.get('id')
    rentobj = RentDetails.objects.filter(Is_Active=True,id=Id).first()
    if rentobj is not None:
        serializer = RentDetailsserializer(rentobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Rent Details found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updateRentDetails(request):
    data={}
    Id = request.data.get('id')
    rentobj = RentDetails.objects.filter(Is_Active=True,id=Id).first()
    if rentobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = RentDetailsserializer(rentobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Rent Details updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating Rent Details","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteRentDetails(request):
    data={}
    Id = request.data.get('id')
    rentobj = RentDetails.objects.filter(Is_Active=True,id=Id).first()
    if rentobj is not None:
        data['Is_Active']=False
        serializer = RentDetailsserializer(rentobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "Rent Details deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting Rent Details ","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#----------------------------------------Investment proofentry audit-----------------------------------------------------------


@api_view(['POST'])
def AddProofEntryAudit(request):
    data={}
    requestdata = request.data.copy()
    user = request.user.id
    data['company_code']=request.user.company_code
    serializer = ProofEntry_Auditserializer(data=requestdata)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry audit Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding ProofEntry ","status": "Failure"}})

@api_view(['GET'])
def ProofEntryAuditlist(request):
    taskobj = ProofEntryAudit.objects.filter(Is_Active=True).order_by('id')
    serializer = ProofEntry_Auditserializer(taskobj,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry audit list shown successfully","status": "success"}})


@api_view(['GET'])
def ProofEntryAuditbyid(request):
    Id = request.data.get('id')
    taskobj = ProofEntryAudit.objects.filter(Is_Active=True,id=Id).first()
    if taskobj is not None:
        serializer = ProofEntry_Auditserializer(taskobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry audit found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})


@api_view(['POST'])
def updateProofEntryAudit(request):
    data={}
    Id = request.data.get('id')
    invobj = ProofEntryAudit.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        user = request.user.id
        requestdata = request.data.copy()
        data['company_code']=request.user.company_code
        serializer = ProofEntry_Auditserializer(invobj,data=requestdata,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "ProofEntry audit updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error updating ProofEntryaudit","status": "Failure"}})
    else:
        return Response({"data":'',"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def deleteProofEntryAudit(request):
    data={}
    Id = request.data.get('id')
    invobj = ProofEntryAudit.objects.filter(Is_Active=True,id=Id).first()
    if invobj is not None:
        data['Is_Active']=False
        serializer = ProofEntry_Auditserializer(invobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":'',"response":{"n": 1,"msg": "ProofEntry audit deleted successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while deleting ProofEntry audit","status": "Failure"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

#----------------------------------landlord----------------------------------------------------------------------------
@api_view(['POST'])
def AddInvLandlord(request):
    data={}
    user = request.user.id
    data['EmployeeCode']=request.data.get('EmployeeCode')
    data['LandlordName']=request.data.get('LandlordName')
    data['LandlordAddress']=request.data.get('LandlordAddress')
    data['LandlordPAN']=request.data.get('LandlordPAN')
    data['File_Path']=request.data.get('File_Path')
    data['FinancialYearId']=request.data.get('FinancialYearId')
    data['BatchNo']=request.data.get('BatchNo')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvLandLordserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Land lord Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Land lord ","status": "Failure"}})

@api_view(['GET'])
def Invlandlordlist(request):
    Finyear = Investment_LandlordDetails.objects.all().order_by('id')
    serializer = InvLandLordserializer(Finyear,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Land lord shown successfully","status": "success"}})

@api_view(['GET'])
def getInvlandlordbyid(request):
    Id = request.data.get('id')
    finyearobj = Investment_LandlordDetails.objects.filter(id=Id).first()
    if finyearobj is not None:
        serializer = InvLandLordserializer(finyearobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Land lord found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})



def updateInvLandlord(request):
    data={}
    Id=request.data.get('id')
    landlordobj = Investment_LandlordDetails.objects.filter(id=Id).first()
    if landlordobj is not None:
        user = request.user.id
        data['LandlordName']=request.data.get('LandlordName')
        data['EmployeeCode']=request.data.get('EmployeeCode')
        data['LandlordAddress']=request.data.get('LandlordAddress')
        data['LandlordPAN']=request.data.get('LandlordPAN')
        data['File_Path']=request.data.get('File_Path')
        data['FinancialYearId']=request.data.get('FinancialYearId')
        data['BatchNo']=request.data.get('BatchNo')
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvLandLordserializer(landlordobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Land lord updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        return Response({"data":"","response":{"n": 0,"msg": " id not found ","status": "Failure"}})

#----------------------------------------------lender--------------------------------------------------------------------
@api_view(['POST'])
def AddInvLender(request):
    data={}
    user = request.user.id
    data['InvestTypeId']=request.data.get('InvestTypeId')
    data['EmployeeCode']=request.data.get('EmployeeCode')
    data['LenderName']=request.data.get('LenderName')
    data['LenderAddress']=request.data.get('LenderAddress')
    data['LenderType']=request.data.get('LenderType')
    data['LenderPAN']=request.data.get('LenderPAN')
    data['LAmount']=request.data.get('LAmount')
    data['FinancialYearId']=request.data.get('FinancialYearId')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvLenderserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Lender Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Lender","status": "Failure"}})

@api_view(['GET'])
def InvLenderlist(request):
    Finyear = Investment_LenderDetails.objects.all().order_by('id')
    serializer = InvLenderserializer(Finyear,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Lender shown successfully","status": "success"}})

@api_view(['GET'])
def getInvLenderbyid(request):
    Id = request.data.get('id')
    lenderobj = Investment_LenderDetails.objects.filter(id=Id).first()
    if lenderobj is not None:
        serializer = InvLenderserializer(lenderobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Lender found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updateInvLender(request):
    data={}
    Id=request.data.get('id')
    lenderobj = Investment_LenderDetails.objects.filter(id=Id).first()
    if lenderobj is not None:
        user = request.user.id
        data['InvestTypeId']=request.data.get('InvestTypeId')
        data['EmployeeCode']=request.data.get('EmployeeCode')
        data['LenderName']=request.data.get('LenderName')
        data['LenderAddress']=request.data.get('LenderAddress')
        data['LenderType']=request.data.get('LenderType')
        data['LenderPAN']=request.data.get('LenderPAN')
        data['LAmount']=request.data.get('LAmount')
        data['FinancialYearId']=request.data.get('FinancialYearId')
        data['BatchNo']=request.data.get('BatchNo')
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvLenderserializer(lenderobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Lender updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        return Response({"data":"","response":{"n": 0,"msg": " id not found ","status": "Failure"}})


#-----------------------------------------------proof batch-----------------------------------------------------------------
@api_view(['POST'])
def AddProofBatch(request):
    data={}
    user = request.user.id
    data['BatchNo']=request.data.get('BatchNo')
    data['NoOfProof']=request.data.get('NoOfProof')
    data['status']=request.data.get('status')
    data['FinancialYearId']=request.data.get('FinancialYearId')
    data['CreatedBy']=user
    data['UpdatedBy']=user
    data['company_code']=request.user.company_code
    serializer = InvProofBatchserializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Proof Batch Added successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error Adding Proof Batch","status": "Failure"}})

@api_view(['GET'])
def InvProofBatchlist(request):
    Finyear = Investment_ProofBatchMaster.objects.all().order_by('id')
    serializer = InvProofBatchserializer(Finyear,many=True)
    return Response({"data":serializer.data,"response":{"n": 1,"msg": "Proof Batch shown successfully","status": "success"}})

@api_view(['GET'])
def getInvProofBatchbyid(request):
    Id = request.data.get('id')
    proofobj = Investment_ProofBatchMaster.objects.filter(id=Id).first()
    if proofobj is not None:
        serializer = InvProofBatchserializer(proofobj)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Proof Batch found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "id not found ","status": "Failure"}})

@api_view(['POST'])
def updateInvProofBatch(request):
    data={}
    Id=request.data.get('id')
    proofobj = Investment_ProofBatchMaster.objects.filter(id=Id).first()
    if proofobj is not None:
        user = request.user.id
        data['BatchNo']=request.data.get('BatchNo')
        data['NoOfProof']=request.data.get('NoOfProof')
        data['status']=request.data.get('status')
        data['FinancialYearId']=request.data.get('FinancialYearId')
        data['CreatedBy']=user
        data['UpdatedBy']=user
        data['company_code']=request.user.company_code
        serializer = InvProofBatchserializer(proofobj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Proof Batch updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        return Response({"data":"","response":{"n": 0,"msg": " id not found ","status": "Failure"}})


@api_view(['POST'])
def addConfiguration(request):
    requestData = request.data.copy()
    confObject = Configuration.objects.filter(Is_Active = True,sectionId = requestData['sectionId'],invTypeId = requestData['invTypeId']).first()
    requestData['Is_Active'] = True
    if requestData['policyNocheck'] is not None and requestData['policyNocheck'] == "1":
        requestData['policyNocheck'] = True
    else:
        requestData['policyNocheck'] = False
    if requestData['receiptNocheck'] is not None and requestData['receiptNocheck'] == "1":
        requestData['receiptNocheck'] = True
    else:
        requestData['receiptNocheck'] = False
    if requestData['periodcheck'] is not None and requestData['periodcheck'] == "1":
        requestData['periodcheck'] = True
    else:
        requestData['periodcheck'] = False
    if requestData['possessiondatecheck'] is not None and requestData['possessiondatecheck'] == "1":
        requestData['possessiondatecheck'] = True
    else:
        requestData['possessiondatecheck'] = False
    if requestData['sharepercentagecheck'] is not None and requestData['sharepercentagecheck'] == "1":
        requestData['sharepercentagecheck'] = True
    else:
        requestData['sharepercentagecheck'] = False
    if requestData['metro_nonmetrocheck'] is not None and requestData['metro_nonmetrocheck'] == "1":
        requestData['metro_nonmetrocheck'] = True
    else:
        requestData['metro_nonmetrocheck'] = False
    if requestData['lenderform'] is not None and requestData['lenderform'] == "1":
        requestData['lenderform'] = True
    else:
        requestData['lenderform'] = False
    if requestData['IsPreviousYear'] is not None and requestData['IsPreviousYear'] == "1":
        requestData['IsPreviousYear'] = True
    else:
        requestData['IsPreviousYear'] = False
    if requestData['limitpancomp'] is not None and requestData['limitpancomp'] == "1":
        requestData['limitpancomp'] = True
    else:
        requestData['limitpancomp'] = False
    if requestData['block_maxlimit'] is not None and requestData['block_maxlimit'] == "1":
        requestData['block_maxlimit'] = True
    else:
        requestData['block_maxlimit'] = False
    if requestData['ltapayment'] is not None and requestData['ltapayment'] == "1":
        requestData['ltapayment'] = True
    else:
        requestData['ltapayment'] = False
    if confObject is not None:
        serializer = configurationserializer(confObject,data=requestData)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Configuration updated successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while updating","status": "Failure"}})
    else:
        serializer = configurationserializer(data=requestData)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response":{"n": 1,"msg": "Configuration added successfully","status": "success"}})
        else:
            return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error while adding","status": "Failure"}})

@api_view(['GET'])
def fieldTypeList(request):
    fieldObject = FieldType.objects.filter(Is_Active = True)
    if fieldObject is not None:
        serializer = FieldTypeserializer(fieldObject,many=True)
        return Response({"data":serializer.data,"response":{"n": 1,"msg": "Field type found successfully","status": "success"}})
    else:
        return Response({"data":serializer.errors,"response":{"n": 0,"msg": "Error fetching fieldtype","status": "Failure"}})
    
