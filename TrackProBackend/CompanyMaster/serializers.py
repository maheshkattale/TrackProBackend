from django.db.models import fields
from rest_framework import serializers
from CompanyMaster.models import companyinfo,paymentslip,BillingPeriod,CompanyType,companypaymentlog


class companyserializer(serializers.ModelSerializer):

    class Meta:
        model = companyinfo
        fields = '__all__'

class paymentslipserializer(serializers.ModelSerializer):

    class Meta:
        model = paymentslip
        fields = '__all__'

class BillingPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillingPeriod
        fields = '__all__'

class CompanytypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyType
        fields = '__all__'

class CompanypaymentlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = companypaymentlog
        fields = '__all__'