from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Donor, BloodBank, BloodInventory, DonationRequest, BloodGroup


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'phone_number', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number')}),
    )


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'city', 'is_available', 'last_donation_date']
    list_filter = ['blood_group', 'is_available', 'city', 'state']
    search_fields = ['user__username', 'user__email', 'city', 'state']


@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'phone_number']
    list_filter = ['city', 'state']
    search_fields = ['name', 'city', 'state']


@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['blood_bank', 'blood_group', 'units_available', 'last_updated']
    list_filter = ['blood_bank', 'blood_group']
    search_fields = ['blood_bank__name']


@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_bank', 'blood_group', 'units_requested', 'status', 'request_date', 'created_at']
    list_filter = ['status', 'blood_group', 'request_date']
    search_fields = ['donor__user__username', 'blood_bank__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BloodGroup)
class BloodGroupAdmin(admin.ModelAdmin):
    list_display = ['name']

