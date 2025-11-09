from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API Router
router = DefaultRouter()
router.register(r'donors', api_views.DonorViewSet, basename='donor')
router.register(r'blood-banks', api_views.BloodBankViewSet, basename='bloodbank')
router.register(r'inventory', api_views.BloodInventoryViewSet, basename='inventory')
router.register(r'donation-requests', api_views.DonationRequestViewSet, basename='donationrequest')

# All URLs (both API and template)
urlpatterns = [
    # API URLs
    path('api/auth/register/', api_views.register, name='api_register'),
    path('api/auth/login/', api_views.login, name='api_login'),
    path('api/auth/logout/', api_views.logout, name='api_logout'),
    path('api/admin/stats/', api_views.admin_stats, name='api_admin_stats'),
    path('api/', include(router.urls)),
    
    # Template URLs
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # Donor URLs
    path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('donor/profile/', views.donor_profile, name='donor_profile'),
    path('donor/history/', views.donation_history, name='donation_history'),
    path('donor/request/', views.create_donation_request, name='create_donation_request'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/donors/', views.manage_donors, name='manage_donors'),
    path('admin/blood-banks/', views.manage_blood_banks, name='manage_blood_banks'),
    path('admin/requests/', views.manage_requests, name='manage_requests'),
    path('admin/requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('admin/requests/<int:request_id>/reject/', views.reject_request, name='reject_request'),
]

