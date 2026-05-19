from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    ISSUE_TYPES = [
        ('pothole', 'Pothole'),
        ('garbage', 'Garbage'),
        ('water', 'Water Leakage'),
        ('streetlight', 'Street Light Issue'),
        ('other', 'Other'),
    ]

    DEPARTMENTS = [
        ('municipality', 'Municipality'),
        ('panchayat', 'Panchayat'),
        ('pwd', 'PWD'),
        ('kwa', 'KWA'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Escalated', 'Escalated'),
    ]

    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    subject = models.CharField(max_length=200)
    description = models.TextField()
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    location = models.CharField(max_length=200)
    department = models.CharField(max_length=50, choices=DEPARTMENTS, blank=True)
    image = models.ImageField(upload_to='complaint_images/', blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    google_maps_location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def save(self, *args, **kwargs):
        """
        Automatically assign the department based on issue_type if not set.
        """
        ISSUE_TO_DEPARTMENT = {
            'pothole': 'pwd',
            'water': 'kwa',
            'garbage': 'municipality',
            'streetlight': 'panchayat',
            'other': 'municipality',
        }

        if not self.department:
            self.department = ISSUE_TO_DEPARTMENT.get(self.issue_type, 'kwa')

        if self.latitude and self.longitude and not self.google_maps_location:
            self.google_maps_location = f"{self.latitude},{self.longitude}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} ({self.get_issue_type_display()})"


class Officer(models.Model):
    DEPARTMENTS = [
        ('municipality', 'Municipality'),
        ('panchayat', 'Panchayat'),
        ('pwd', 'PWD'),
        ('kwa', 'KWA'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="officer_profile")
    officer_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENTS)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # Admin approval required
    registration_code = models.CharField(max_length=50, blank=True, null=True)  # Pre-shared code used during registration
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Officer"
        verbose_name_plural = "Officers"

    def __str__(self):
        status = "Verified" if self.is_verified else "Pending Verification"
        return f"{self.user.username} ({self.get_department_display()}) - {status}"
