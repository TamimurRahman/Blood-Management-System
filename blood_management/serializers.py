from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Donor, BloodBank, BloodInventory, DonationRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number']
        read_only_fields = ['id', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone_number', 'role']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        return attrs


class DonorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Donor
        fields = ['id', 'user', 'user_id', 'blood_group', 'date_of_birth', 'address', 
                  'city', 'state', 'zip_code', 'is_available', 'last_donation_date', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DonorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ['blood_group', 'date_of_birth', 'address', 'city', 'state', 
                  'zip_code', 'is_available', 'last_donation_date']


class BloodBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodBank
        fields = ['id', 'name', 'address', 'city', 'state', 'zip_code', 
                  'phone_number', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BloodInventorySerializer(serializers.ModelSerializer):
    blood_bank_name = serializers.CharField(source='blood_bank.name', read_only=True)
    
    class Meta:
        model = BloodInventory
        fields = ['id', 'blood_bank', 'blood_bank_name', 'blood_group', 
                  'units_available', 'last_updated']
        read_only_fields = ['id', 'last_updated']


class DonationRequestSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.user.get_full_name', read_only=True)
    donor_username = serializers.CharField(source='donor.user.username', read_only=True)
    blood_bank_name = serializers.CharField(source='blood_bank.name', read_only=True)
    
    class Meta:
        model = DonationRequest
        fields = ['id', 'donor', 'donor_name', 'donor_username', 'blood_bank', 
                  'blood_bank_name', 'blood_group', 'units_requested', 
                  'request_date', 'status', 'admin_notes', 'created_at', 
                  'updated_at', 'approved_by']
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_by']


class DonationRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRequest
        fields = ['blood_bank', 'blood_group', 'units_requested', 'request_date']


class AdminStatsSerializer(serializers.Serializer):
    total_donors = serializers.IntegerField()
    total_blood_banks = serializers.IntegerField()
    total_pending_requests = serializers.IntegerField()
    total_approved_requests = serializers.IntegerField()
    total_rejected_requests = serializers.IntegerField()
    blood_group_stats = serializers.DictField()

