from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponseForbidden
from functools import wraps
from rest_framework.authtoken.models import Token

from .models import Donor, BloodBank, BloodInventory, DonationRequest, User


def is_admin(user):
    """Check if user is admin or superuser"""
    if not user.is_authenticated:
        return False
    return user.is_admin or user.is_superuser


def admin_required(view_func):
    """Decorator to require admin access with proper error message"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not is_admin(request.user):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def home(request):
    """Redirect to appropriate dashboard based on user role"""
    if request.user.is_admin:
        return redirect('admin_dashboard')
    else:
        return redirect('donor_dashboard')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        role = request.POST.get('role', 'donor')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'blood_management/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'blood_management/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'blood_management/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role
        )
        
        # Create donor profile if role is donor
        if role == 'donor':
            Donor.objects.create(user=user)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'blood_management/register.html')


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'blood_management/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def donor_dashboard(request):
    """Donor dashboard"""
    try:
        donor = request.user.donor_profile
    except Donor.DoesNotExist:
        donor = None
    
    donation_requests = DonationRequest.objects.filter(donor=donor).order_by('-created_at')[:10] if donor else []
    
    # Get available blood groups
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    available_blood = {}
    for bg in blood_groups:
        total = BloodInventory.objects.filter(blood_group=bg).aggregate(
            total=Sum('units_available')
        )['total'] or 0
        available_blood[bg] = total
    
    context = {
        'donor': donor,
        'donation_requests': donation_requests,
        'available_blood': available_blood,
    }
    return render(request, 'blood_management/donor_dashboard.html', context)


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard"""
    total_donors = Donor.objects.count()
    total_blood_banks = BloodBank.objects.count()
    total_pending_requests = DonationRequest.objects.filter(status='pending').count()
    total_approved_requests = DonationRequest.objects.filter(status='approved').count()
    total_rejected_requests = DonationRequest.objects.filter(status='rejected').count()
    
    # Recent requests
    recent_requests = DonationRequest.objects.all().order_by('-created_at')[:10]
    
    # Blood group statistics
    blood_group_stats = {}
    for bg in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
        donors_count = Donor.objects.filter(blood_group=bg).count()
        inventory_total = BloodInventory.objects.filter(blood_group=bg).aggregate(
            total=Sum('units_available')
        )['total'] or 0
        blood_group_stats[bg] = {
            'donors': donors_count,
            'available_units': inventory_total
        }
    
    context = {
        'total_donors': total_donors,
        'total_blood_banks': total_blood_banks,
        'total_pending_requests': total_pending_requests,
        'total_approved_requests': total_approved_requests,
        'total_rejected_requests': total_rejected_requests,
        'recent_requests': recent_requests,
        'blood_group_stats': blood_group_stats,
    }
    return render(request, 'blood_management/admin_dashboard.html', context)


@login_required
def donor_profile(request):
    """Donor profile view"""
    try:
        donor = request.user.donor_profile
    except Donor.DoesNotExist:
        donor = None
    
    if request.method == 'POST':
        if donor:
            blood_group = request.POST.get('blood_group') or None
            donor.blood_group = blood_group if blood_group else donor.blood_group
            donor.date_of_birth = request.POST.get('date_of_birth') or None
            donor.address = request.POST.get('address', '')
            donor.city = request.POST.get('city', '')
            donor.state = request.POST.get('state', '')
            donor.zip_code = request.POST.get('zip_code', '')
            donor.is_available = request.POST.get('is_available') == 'on'
            donor.last_donation_date = request.POST.get('last_donation_date') or None
            donor.save()
            
            # Update user info
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.phone_number = request.POST.get('phone_number', '')
            request.user.save()
            
            messages.success(request, 'Profile updated successfully!')
        else:
            # Create donor profile
            blood_group = request.POST.get('blood_group') or None
            donor = Donor.objects.create(
                user=request.user,
                blood_group=blood_group,
                date_of_birth=request.POST.get('date_of_birth') or None,
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                zip_code=request.POST.get('zip_code', ''),
                is_available=request.POST.get('is_available') == 'on',
                last_donation_date=request.POST.get('last_donation_date') or None,
            )
            messages.success(request, 'Donor profile created successfully!')
        
        return redirect('donor_profile')
    
    context = {
        'donor': donor,
    }
    return render(request, 'blood_management/donor_profile.html', context)


@login_required
def donation_history(request):
    """Donor donation history"""
    try:
        donor = request.user.donor_profile
        donation_requests = DonationRequest.objects.filter(donor=donor).order_by('-created_at')
    except Donor.DoesNotExist:
        donation_requests = []
    
    context = {
        'donation_requests': donation_requests,
    }
    return render(request, 'blood_management/donation_history.html', context)


@login_required
def create_donation_request(request):
    """Create a new donation request"""
    if request.method == 'POST':
        try:
            donor = request.user.donor_profile
            blood_bank_id = request.POST.get('blood_bank')
            blood_group = request.POST.get('blood_group')
            units_requested = int(request.POST.get('units_requested', 1))
            request_date = request.POST.get('request_date')
            
            blood_bank = BloodBank.objects.get(id=blood_bank_id)
            
            donation_request = DonationRequest.objects.create(
                donor=donor,
                blood_bank=blood_bank,
                blood_group=blood_group,
                units_requested=units_requested,
                request_date=request_date,
            )
            
            messages.success(request, 'Donation request submitted successfully!')
            return redirect('donation_history')
        except Donor.DoesNotExist:
            messages.error(request, 'Please create a donor profile first.')
            return redirect('donor_profile')
        except Exception as e:
            messages.error(request, f'Error creating request: {str(e)}')
    
    blood_banks = BloodBank.objects.all()
    context = {
        'blood_banks': blood_banks,
    }
    return render(request, 'blood_management/create_donation_request.html', context)


@login_required
@admin_required
def manage_donors(request):
    """Admin view to manage donors"""
    donors = Donor.objects.all()
    
    # Search and filter
    search = request.GET.get('search', '')
    blood_group = request.GET.get('blood_group', '')
    city = request.GET.get('city', '')
    is_available = request.GET.get('is_available', '')
    
    if search:
        donors = donors.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(city__icontains=search)
        )
    
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    
    if city:
        donors = donors.filter(city__icontains=city)
    
    if is_available:
        donors = donors.filter(is_available=is_available == 'true')
    
    context = {
        'donors': donors,
        'search': search,
        'blood_group': blood_group,
        'city': city,
        'is_available': is_available,
    }
    return render(request, 'blood_management/manage_donors.html', context)


@login_required
@admin_required
def manage_blood_banks(request):
    """Admin view to manage blood banks"""
    blood_banks = BloodBank.objects.all()
    
    # Search and filter
    search = request.GET.get('search', '')
    city = request.GET.get('city', '')
    state = request.GET.get('state', '')
    
    if search:
        blood_banks = blood_banks.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search) |
            Q(state__icontains=search)
        )
    
    if city:
        blood_banks = blood_banks.filter(city__icontains=city)
    
    if state:
        blood_banks = blood_banks.filter(state__icontains=state)
    
    context = {
        'blood_banks': blood_banks,
        'search': search,
        'city': city,
        'state': state,
    }
    return render(request, 'blood_management/manage_blood_banks.html', context)


@login_required
@admin_required
def manage_requests(request):
    """Admin view to manage donation requests"""
    requests = DonationRequest.objects.all()
    
    # Filter
    status_filter = request.GET.get('status', '')
    blood_group = request.GET.get('blood_group', '')
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    if blood_group:
        requests = requests.filter(blood_group=blood_group)
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
        'blood_group': blood_group,
    }
    return render(request, 'blood_management/manage_requests.html', context)


@login_required
@admin_required
def approve_request(request, request_id):
    """Approve a donation request"""
    donation_request = DonationRequest.objects.get(id=request_id)
    donation_request.status = 'approved'
    donation_request.approved_by = request.user
    donation_request.admin_notes = request.POST.get('admin_notes', '')
    donation_request.save()
    
    # Update blood inventory
    inventory, created = BloodInventory.objects.get_or_create(
        blood_bank=donation_request.blood_bank,
        blood_group=donation_request.blood_group,
        defaults={'units_available': 0}
    )
    inventory.units_available += donation_request.units_requested
    inventory.save()
    
    messages.success(request, 'Request approved successfully!')
    return redirect('manage_requests')


@login_required
@admin_required
def reject_request(request, request_id):
    """Reject a donation request"""
    donation_request = DonationRequest.objects.get(id=request_id)
    donation_request.status = 'rejected'
    donation_request.approved_by = request.user
    donation_request.admin_notes = request.POST.get('admin_notes', '')
    donation_request.save()
    
    messages.success(request, 'Request rejected.')
    return redirect('manage_requests')

