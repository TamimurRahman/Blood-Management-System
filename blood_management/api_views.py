from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from .models import User, Donor, BloodBank, BloodInventory, DonationRequest
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    DonorSerializer, DonorCreateSerializer,
    BloodBankSerializer, BloodInventorySerializer,
    DonationRequestSerializer, DonationRequestCreateSerializer,
    AdminStatsSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        # Create donor profile if role is donor
        if user.role == 'donor':
            Donor.objects.create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response({'message': 'Logout successful'})


class DonorViewSet(viewsets.ModelViewSet):
    """ViewSet for Donor management"""
    queryset = Donor.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DonorCreateSerializer
        return DonorSerializer

    def get_queryset(self):
        queryset = Donor.objects.all()
        
        # Filter by blood group
        blood_group = self.request.query_params.get('blood_group', None)
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by availability
        is_available = self.request.query_params.get('is_available', None)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        # Search by name or username
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(city__icontains=search)
            )
        
        # Non-admin users can only see their own profile
        if not self.request.user.is_admin:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset

    def perform_create(self, serializer):
        # Automatically set user to current user if not admin
        if not self.request.user.is_admin:
            serializer.save(user=self.request.user)
        else:
            user_id = self.request.data.get('user_id')
            if user_id:
                user = User.objects.get(id=user_id)
                serializer.save(user=user)
            else:
                serializer.save(user=self.request.user)


class BloodBankViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Bank management"""
    queryset = BloodBank.objects.all()
    serializer_class = BloodBankSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = BloodBank.objects.all()
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by state
        state = self.request.query_params.get('state', None)
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(state__icontains=search)
            )
        
        return queryset


class BloodInventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Blood Inventory management"""
    queryset = BloodInventory.objects.all()
    serializer_class = BloodInventorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = BloodInventory.objects.all()
        
        # Filter by blood bank
        blood_bank = self.request.query_params.get('blood_bank', None)
        if blood_bank:
            queryset = queryset.filter(blood_bank_id=blood_bank)
        
        # Filter by blood group
        blood_group = self.request.query_params.get('blood_group', None)
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        
        return queryset


class DonationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for Donation Request management"""
    queryset = DonationRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DonationRequestCreateSerializer
        return DonationRequestSerializer

    def get_queryset(self):
        queryset = DonationRequest.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by blood group
        blood_group = self.request.query_params.get('blood_group', None)
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        
        # Non-admin users can only see their own requests
        if not self.request.user.is_admin:
            try:
                donor = self.request.user.donor_profile
                queryset = queryset.filter(donor=donor)
            except Donor.DoesNotExist:
                queryset = queryset.none()
        
        return queryset

    def perform_create(self, serializer):
        # Automatically set donor to current user's donor profile
        if not self.request.user.is_admin:
            try:
                donor = self.request.user.donor_profile
                serializer.save(donor=donor)
            except Donor.DoesNotExist:
                raise serializers.ValidationError("Donor profile not found. Please create a donor profile first.")
        else:
            donor_id = self.request.data.get('donor')
            if donor_id:
                donor = Donor.objects.get(id=donor_id)
                serializer.save(donor=donor)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a donation request"""
        donation_request = self.get_object()
        donation_request.status = 'approved'
        donation_request.approved_by = request.user
        donation_request.admin_notes = request.data.get('admin_notes', '')
        donation_request.save()
        
        # Update blood inventory
        inventory, created = BloodInventory.objects.get_or_create(
            blood_bank=donation_request.blood_bank,
            blood_group=donation_request.blood_group,
            defaults={'units_available': 0}
        )
        inventory.units_available += donation_request.units_requested
        inventory.save()
        
        serializer = self.get_serializer(donation_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a donation request"""
        donation_request = self.get_object()
        donation_request.status = 'rejected'
        donation_request.approved_by = request.user
        donation_request.admin_notes = request.data.get('admin_notes', '')
        donation_request.save()
        
        serializer = self.get_serializer(donation_request)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats(request):
    """Get admin dashboard statistics"""
    total_donors = Donor.objects.count()
    total_blood_banks = BloodBank.objects.count()
    total_pending_requests = DonationRequest.objects.filter(status='pending').count()
    total_approved_requests = DonationRequest.objects.filter(status='approved').count()
    total_rejected_requests = DonationRequest.objects.filter(status='rejected').count()
    
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
    
    data = {
        'total_donors': total_donors,
        'total_blood_banks': total_blood_banks,
        'total_pending_requests': total_pending_requests,
        'total_approved_requests': total_approved_requests,
        'total_rejected_requests': total_rejected_requests,
        'blood_group_stats': blood_group_stats
    }
    
    serializer = AdminStatsSerializer(data)
    return Response(serializer.data)

