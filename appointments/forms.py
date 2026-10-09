from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Doctor, Patient, Appointment, MedicalReport,
    DEPARTMENT_CHOICES, GENDER_CHOICES, BLOOD_GROUP_CHOICES, TIME_SLOT_CHOICES
)


class AppointmentBookingForm(forms.Form):
    # Patient Information
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'id': 'id_first_name'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'id': 'id_last_name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'patient@example.com',
            'id': 'id_email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 019-2834',
            'id': 'id_phone'
        })
    )
    age = forms.IntegerField(
        min_value=0,
        max_value=120,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Age (optional)',
            'id': 'id_age'
        })
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_gender'
        })
    )
    blood_group = forms.ChoiceField(
        choices=[('', '-- Select Blood Group (Optional) --')] + BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_blood_group'
        })
    )

    # Appointment Details
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_available=True),
        empty_label="-- Select Specialist Doctor --",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_doctor'
        })
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_appointment_date'
        })
    )
    time_slot = forms.ChoiceField(
        choices=[('', '-- Choose Time Slot --')] + TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_time_slot'
        })
    )
    reason_for_visit = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe your symptoms, medical concerns, or reasons for this visit...',
            'id': 'id_reason'
        })
    )

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date:
            today = timezone.localdate()
            if date < today:
                raise ValidationError("Appointment date cannot be in the past. Please select today or a future date.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and appointment_date and time_slot:
            # Check for conflict
            clash = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                time_slot=time_slot
            ).exclude(status='Cancelled').exists()

            if clash:
                raise ValidationError(
                    f"Dr. {doctor.name} already has an active booking for {time_slot} on "
                    f"{appointment_date.strftime('%B %d, %Y')}. Please choose another time slot or date."
                )

        return cleaned_data

    def save(self):
        cd = self.cleaned_data
        phone = cd['phone'].strip()

        # Find or create patient by phone number
        patient, created = Patient.objects.get_or_create(
            phone=phone,
            defaults={
                'first_name': cd['first_name'].strip(),
                'last_name': cd['last_name'].strip(),
                'email': cd['email'].strip(),
                'age': cd.get('age'),
                'gender': cd['gender'],
                'blood_group': cd.get('blood_group', ''),
            }
        )
        if not created:
            # Update basic patient details if provided
            patient.first_name = cd['first_name'].strip()
            patient.last_name = cd['last_name'].strip()
            if cd.get('email'):
                patient.email = cd['email'].strip()
            if cd.get('age'):
                patient.age = cd.get('age')
            if cd.get('blood_group'):
                patient.blood_group = cd.get('blood_group')
            patient.save()

        # Create the appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=cd['doctor'],
            appointment_date=cd['appointment_date'],
            time_slot=cd['time_slot'],
            reason_for_visit=cd['reason_for_visit'],
            status='Pending'
        )
        return appointment


class PatientSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your registered phone number or Appointment ID (e.g., CP-2026-...)',
            'id': 'patient_search_query'
        })
    )


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = [
            'blood_pressure',
            'heart_rate',
            'temperature',
            'respiratory_rate',
            'diagnosis',
            'prescription',
            'doctor_notes',
            'follow_up_date',
        ]
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120/80 mmHg'}),
            'heart_rate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 72 bpm'}),
            'temperature': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 98.6 °F'}),
            'respiratory_rate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 16 bpm'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'doctor_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
