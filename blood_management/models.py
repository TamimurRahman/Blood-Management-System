from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('donor', 'Donor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='donor')
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_donor(self):
        return self.role == 'donor'


class BloodGroup(models.Model):
    """Blood group model"""
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    name = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, unique=True)
    
    def __str__(self):
        return self.name


class Donor(models.Model):
    """Donor profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(
        max_length=3, 
        choices=BloodGroup.BLOOD_GROUP_CHOICES,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        bg = self.blood_group if self.blood_group else 'N/A'
        return f"{self.user.get_full_name() or self.user.username} - {bg}"


class BloodBank(models.Model):
    """Blood Bank model"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BloodInventory(models.Model):
    """Blood inventory for each blood bank"""
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='inventory')
    blood_group = models.CharField(max_length=3, choices=BloodGroup.BLOOD_GROUP_CHOICES)
    units_available = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['blood_bank', 'blood_group']
        ordering = ['blood_bank', 'blood_group']

    def __str__(self):
        return f"{self.blood_bank.name} - {self.blood_group}: {self.units_available} units"


class DonationRequest(models.Model):
    """Blood donation request model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donation_requests')
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, related_name='donation_requests')
    blood_group = models.CharField(max_length=3, choices=BloodGroup.BLOOD_GROUP_CHOICES)
    units_requested = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    request_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.donor.user.username} - {self.blood_group} - {self.status}"

