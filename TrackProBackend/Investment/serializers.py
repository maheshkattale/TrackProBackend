from Tasks.models import ProjectTasks
from Users.models import Users
from rest_framework import serializers
from .models import *



class sectionserializer(serializers.ModelSerializer):
  
    class Meta:
        model = Section
        fields ='__all__'


class investmentTypeserializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentType
        fields ='__all__'



class listinvestmentTypeserializer(serializers.ModelSerializer):
    sectionId = serializers.StringRelatedField()

    class Meta:
        model = InvestmentType
        fields ='__all__'

class InvDiseaseserializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentDisease
        fields ='__all__'

class InvFinancialYearserializer(serializers.ModelSerializer):

   class Meta:
        model = InvestmentFinancialYear
        fields ='__all__'

class InvReasonsserializer(serializers.ModelSerializer):
    
   class Meta:
        model = InvestmentReasons
        fields ='__all__'


class InvFilesSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = Investment_Files
        fields ='__all__'

class InvFile_DetailsSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = Investment_FileDetails
        fields ='__all__'

class InvstatusSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = InvestmentStatusMaster
        fields ='__all__'


class InvProofStatusHistorySerializer(serializers.ModelSerializer):
    
   class Meta:
        model = ProofStatusHistory
        fields ='__all__'


class ClaimDeductionSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = ClaimDeductionQuestions
        fields ='__all__'


class FinYearSlabSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = Investment_LTAFinYearSlab
        fields ='__all__'


class OnOffSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = Investment_OnOff
        fields ='__all__'


class PayrollConfigSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = InvestmentPayrollConfig
        fields ='__all__'


class PayrollConfig_empSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = InvestmentPayrollConfig_Employee
        fields ='__all__'


class InvMembersSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = InvestmentMembers
        fields ='__all__'


class InvMembersAuditSerializer(serializers.ModelSerializer):
    
   class Meta:
        model = InvestmentMembersAudit
        fields ='__all__'



class memberTasksSerializer(serializers.ModelSerializer):

        class Meta:
                model = Investment_MemberTasks
                fields ='__all__'


class ProofEntryserializer(serializers.ModelSerializer):

    class Meta:
        model = ProofEntry
        fields ='__all__'

class ProofEntry_Auditserializer(serializers.ModelSerializer):

    class Meta:
        model = ProofEntryAudit
        fields ='__all__'

class RentDetailsserializer(serializers.ModelSerializer):

    class Meta:
        model = RentDetails
        fields ='__all__'
class InvTypeOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentTypeOptions
        fields ='__all__'

class InvFinancialYearserializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentFinancialYear
        fields ='__all__'

class InvLandLordserializer(serializers.ModelSerializer):

    class Meta:
        model = Investment_LandlordDetails
        fields ='__all__'

class InvLenderserializer(serializers.ModelSerializer):

    class Meta:
        model = Investment_LenderDetails
        fields ='__all__'

class InvProofBatchserializer(serializers.ModelSerializer):

    class Meta:
        model = Investment_ProofBatchMaster
        fields ='__all__'

class configurationserializer(serializers.ModelSerializer):

    class Meta:
        model = Configuration
        fields ='__all__'

class FieldTypeserializer(serializers.ModelSerializer):

    class Meta:
        model = FieldType
        fields ='__all__'
