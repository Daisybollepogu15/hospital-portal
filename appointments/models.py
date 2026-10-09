import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


DEPARTMENT_CHOICES = [
    ('Cardiology', 'Cardiology'),
    ('Pediatrics', 'Pediatrics'),
    ('Orthopedics', 'Orthopedics'),
    ('Neurology', 'Neurology'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

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

TIME_SLOT_CHOICES = [
    ('09:00 AM', '09:00 AM - 09:30 AM'),
    ('09:30 AM', '09:30 AM - 10:00 AM'),
    ('10:00 AM', '10:00 AM - 10:30 AM'),
    ('10:30 AM', '10:30 AM - 11:00 AM'),
    ('11:00 AM', '11:00 AM - 11:30 AM'),
    ('11:30 AM', '11:30 AM - 12:00 PM'),
    ('02:00 PM', '02:00 PM - 02:30 PM'),
    ('02:30 PM', '02:30 PM - 03:00 PM'),
    ('03:00 PM', '03:00 PM - 03:30 PM'),
    ('03:30 PM', '03:30 PM - 04:00 PM'),
    ('04:00 PM', '04:00 PM - 04:30 PM'),
    ('04:30 PM', '04:30 PM - 05:00 PM'),
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
]


class Doctor(models.Model):
    name = models.CharField(max_length=150, help_text="e.g. Dr. Sarah Jenkins, MD")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(max_length=150, help_text="e.g. Interventional Cardiology")
    qualification = models.CharField(max_length=150, help_text="e.g. MBBS, MD, FACC")
    experience_years = models.PositiveIntegerField(default=5, help_text="Years of clinical practice")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    room_number = models.CharField(max_length=50, default="Room 101, OPD")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True, help_text="Image URL for doctor profile")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['department', 'name']

    def __str__(self):
        return f"{self.name} ({self.department})"

    @property
    def experience_display(self):
        return f"{self.experience_years}+ years"


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, db_index=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    appointment_id = models.CharField(max_length=30, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
    reason_for_visit = models.TextField(help_text="Symptoms, health concerns, or consultation reason")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, help_text="Internal clinical or admin notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', 'time_slot']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'time_slot'],
                condition=~models.Q(status='Cancelled'),
                name='unique_active_doctor_slot'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            # Generate reference ID e.g. CP-2026-A1B2C
            token = uuid.uuid4().hex[:6].upper()
            year = timezone.now().year
            self.appointment_id = f"CP-{year}-{token}"
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Duplicate booking check: prevent booking same doctor + date + time_slot if status is not Cancelled
        if self.doctor_id and self.appointment_date and self.time_slot:
            clash = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                time_slot=self.time_slot
            ).exclude(status='Cancelled')

            if self.pk:
                clash = clash.exclude(pk=self.pk)

            if clash.exists():
                raise ValidationError(
                    f"Dr. {self.doctor.name} already has an active appointment on "
                    f"{self.appointment_date} at {self.time_slot}. Please select a different time slot or date."
                )

    def __str__(self):
        return f"[{self.appointment_id}] {self.patient.full_name} with {self.doctor.name} on {self.appointment_date} ({self.time_slot})"

    @property
    def status_badge_class(self):
        badge_map = {
            'Pending': 'warning',
            'Confirmed': 'primary',
            'Completed': 'success',
            'Cancelled': 'danger',
        }
        return badge_map.get(self.status, 'secondary')


class MedicalReport(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_report')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_reports')
    report_date = models.DateField(default=timezone.now)
    blood_pressure = models.CharField(max_length=30, blank=True, help_text="e.g. 120/80 mmHg")
    heart_rate = models.CharField(max_length=30, blank=True, help_text="e.g. 72 bpm")
    temperature = models.CharField(max_length=30, blank=True, help_text="e.g. 98.6 °F")
    respiratory_rate = models.CharField(max_length=30, blank=True, help_text="e.g. 16 breaths/min")
    diagnosis = models.TextField(help_text="Clinical findings and diagnosis")
    prescription = models.TextField(help_text="Prescribed medications, dosage, and duration")
    doctor_notes = models.TextField(blank=True, help_text="Lifestyle advice, precautions, or lab test requests")
    follow_up_date = models.DateField(null=True, blank=True, help_text="Next review visit date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date', '-created_at']

    def __str__(self):
        return f"Report for {self.patient.full_name} by Dr. {self.doctor.name} ({self.report_date})"
