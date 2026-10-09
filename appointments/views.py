from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Doctor, Patient, Appointment, MedicalReport, DEPARTMENT_CHOICES
from .forms import AppointmentBookingForm, PatientSearchForm


DEPARTMENTS_DATA = {
    'Cardiology': {
        'name': 'Cardiology',
        'icon': 'bi-heart-pulse-fill',
        'badge': 'Heart & Vascular Care',
        'short_desc': 'Comprehensive cardiac care specializing in preventive cardiology, arrhythmia, and advanced interventional procedures.',
        'full_desc': 'Our Department of Cardiology offers round-the-clock cardiac emergency services, high-precision non-invasive diagnostics (ECHO, TMT, Holter), advanced catheterization labs, and compassionate post-operative cardiac rehabilitation.',
        'services': [
            '24/7 Primary Angioplasty (PAMI)',
            'Comprehensive Echo & Stress Testing',
            'Pacemaker & ICD Implantation',
            'Heart Failure Management Clinic',
            'Preventive Heart Screenings',
        ]
    },
    'Pediatrics': {
        'name': 'Pediatrics',
        'icon': 'bi-balloon-heart-fill',
        'badge': 'Child & Newborn Health',
        'short_desc': 'Compassionate healthcare for infants, children, and adolescents with specialized neonatal intensive care.',
        'full_desc': 'The Pediatrics Department delivers gentle, family-centered medical care for growing children. From routine developmental milestones and immunizations to pediatric intensive care and sub-specialty clinics, we nurture healthy futures.',
        'services': [
            'Level III Neonatal Intensive Care (NICU)',
            'Childhood Immunization & Growth Tracking',
            'Pediatric Allergy & Asthma Clinic',
            'Pediatric Infectious Disease Care',
            'Adolescent Health Counseling',
        ]
    },
    'Orthopedics': {
        'name': 'Orthopedics',
        'icon': 'bi-person-walking',
        'badge': 'Bones & Joint Care',
        'short_desc': 'Leading joint replacement, sports injury treatments, trauma surgery, and spine rehabilitation specialists.',
        'full_desc': 'Our Orthopedic center provides world-class surgical and non-surgical solutions for bone, joint, ligament, and spine disorders. Utilizing computer-assisted arthroscopy and robotic-assisted joint replacement, we restore painless mobility.',
        'services': [
            'Minimally Invasive Joint Replacement (Hip & Knee)',
            'Arthroscopic Sports Injury Surgery (ACL/Meniscus)',
            'Comprehensive Spine & Disc Care',
            'Complex Trauma & Fracture Reconstruction',
            'Physiotherapy & Rehabilitation Unit',
        ]
    },
    'Neurology': {
        'name': 'Neurology',
        'icon': 'bi-activity',
        'badge': 'Brain & Nervous System',
        'short_desc': 'Expert diagnosis and cutting-edge treatments for neurological, cerebrovascular, and spinal conditions.',
        'full_desc': 'The Department of Neurology combines expert neurological clinicians with state-of-the-art neuro-imaging (3T MRI, CT Angio, Digital EEG/EMG) to manage stroke, epilepsy, neuromuscular disorders, dementia, and chronic migraines.',
        'services': [
            'Hyper-acute Stroke Thrombolysis',
            'Epilepsy Monitoring & Seizure Care',
            'Headache & Migraine Management',
            'Parkinson’s & Movement Disorder Therapy',
            'Neuro-Electrophysiology (EEG / EMG / NCV)',
        ]
    }
}


def home(request):
    """Hospital landing page with hero, statistics, departments, and featured doctors."""
    featured_doctors = Doctor.objects.filter(is_available=True)[:4]
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    total_patients = Patient.objects.count()

    context = {
        'featured_doctors': featured_doctors,
        'departments': DEPARTMENTS_DATA,
        'stats': {
            'doctors_count': total_doctors or 12,
            'appointments_count': total_appointments or 1500,
            'patients_count': total_patients or 1200,
            'experience_years': 25,
            'emergency_hours': '24/7',
        }
    }
    return render(request, 'appointments/home.html', context)


def doctors_list(request):
    """Doctor directory with department filter, search, and booking links."""
    dept_filter = request.GET.get('dept', '').strip()
    query = request.GET.get('q', '').strip()

    doctors = Doctor.objects.all()

    if dept_filter and dept_filter != 'All':
        doctors = doctors.filter(department__iexact=dept_filter)

    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(qualification__icontains=query) |
            Q(department__icontains=query)
        )

    context = {
        'doctors': doctors,
        'departments': [d[0] for d in DEPARTMENT_CHOICES],
        'selected_dept': dept_filter or 'All',
        'search_query': query,
    }
    return render(request, 'appointments/doctors.html', context)


def doctor_detail(request, doctor_id):
    """Individual doctor profile page."""
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    same_dept_doctors = Doctor.objects.filter(department=doctor.department).exclude(pk=doctor.pk)[:3]

    context = {
        'doctor': doctor,
        'same_dept_doctors': same_dept_doctors,
        'dept_info': DEPARTMENTS_DATA.get(doctor.department, {}),
    }
    return render(request, 'appointments/doctor_detail.html', context)


def departments_list(request):
    """Listing of all four primary hospital departments."""
    depts_with_counts = []
    for dept_key, info in DEPARTMENTS_DATA.items():
        doc_count = Doctor.objects.filter(department__iexact=dept_key).count()
        depts_with_counts.append({
            'key': dept_key,
            'info': info,
            'doctor_count': doc_count,
        })

    context = {
        'departments_list': depts_with_counts,
    }
    return render(request, 'appointments/departments.html', context)


def department_detail(request, department_name):
    """Individual department details with associated doctors."""
    # Find matching department case-insensitively
    matched_key = None
    for k in DEPARTMENTS_DATA:
        if k.lower() == department_name.lower():
            matched_key = k
            break

    if not matched_key:
        matched_key = 'Cardiology'

    dept_info = DEPARTMENTS_DATA[matched_key]
    doctors = Doctor.objects.filter(department__iexact=matched_key)

    context = {
        'dept_name': matched_key,
        'dept_info': dept_info,
        'doctors': doctors,
    }
    return render(request, 'appointments/department_detail.html', context)


def book_appointment(request, doctor_id=None):
    """Interactive appointment booking form."""
    initial_data = {}
    selected_doctor = None

    # Handle doctor passed via URL or query param
    requested_doc_id = doctor_id or request.GET.get('doctor')
    if requested_doc_id:
        try:
            selected_doctor = Doctor.objects.get(pk=requested_doc_id, is_available=True)
            initial_data['doctor'] = selected_doctor.id
        except Doctor.DoesNotExist:
            pass

    # Today's date as default min date
    today_str = timezone.localdate().isoformat()

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(
                request,
                f"Appointment booked successfully! Your reference code is #{appointment.appointment_id}."
            )
            # Store patient phone in session for immediate dashboard access
            request.session['patient_phone'] = appointment.patient.phone
            return redirect('appointment_confirmation', appointment_id=appointment.appointment_id)
        else:
            messages.error(
                request,
                "Please correct the errors in the booking form before submitting."
            )
    else:
        form = AppointmentBookingForm(initial=initial_data)

    context = {
        'form': form,
        'selected_doctor': selected_doctor,
        'doctors': Doctor.objects.filter(is_available=True),
        'today_str': today_str,
    }
    return render(request, 'appointments/book_appointment.html', context)


def appointment_confirmation(request, appointment_id):
    """Appointment confirmation receipt and pass."""
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor'),
        appointment_id=appointment_id
    )

    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_confirmation.html', context)


def patient_dashboard(request):
    """Patient dashboard showing upcoming and previous appointments."""
    query = request.GET.get('query', '').strip()
    session_phone = request.session.get('patient_phone', '')

    search_query = query or session_phone
    patient = None
    appointments = []
    upcoming_appointments = []
    previous_appointments = []

    if search_query:
        # Search by phone number (resilient to dashes, spaces, +) or appointment ID
        clean_digits = ''.join(filter(str.isdigit, search_query))
        query_filter = (
            Q(phone__iexact=search_query) |
            Q(phone__icontains=search_query) |
            Q(appointments__appointment_id__iexact=search_query)
        )
        if clean_digits and len(clean_digits) >= 6:
            query_filter |= Q(phone__icontains=clean_digits)

        patient = Patient.objects.filter(query_filter).distinct().first()

        if patient:
            # Store in session for seamless subsequent views
            request.session['patient_phone'] = patient.phone
            appointments = Appointment.objects.filter(patient=patient).select_related('doctor', 'medical_report').order_by('-appointment_date', '-created_at')
            today = timezone.localdate()

            for appt in appointments:
                if appt.status in ['Pending', 'Confirmed'] and appt.appointment_date >= today:
                    upcoming_appointments.append(appt)
                else:
                    previous_appointments.append(appt)
        else:
            if query:
                messages.warning(
                    request,
                    f"No records found for '{query}'. Please check your phone number or appointment ID."
                )

    search_form = PatientSearchForm(initial={'query': search_query} if search_query else None)

    context = {
        'search_form': search_form,
        'patient': patient,
        'search_query': search_query,
        'upcoming_appointments': upcoming_appointments,
        'previous_appointments': previous_appointments,
        'all_appointments': appointments,
    }
    return render(request, 'appointments/dashboard.html', context)


def cancel_appointment(request, appointment_id):
    """Cancel a pending appointment."""
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    if request.method == 'POST':
        if appointment.status == 'Pending':
            appointment.status = 'Cancelled'
            appointment.save()
            messages.success(
                request,
                f"Appointment #{appointment.appointment_id} has been cancelled successfully."
            )
        else:
            messages.warning(
                request,
                f"Cannot cancel appointment with status '{appointment.status}'. Please contact the hospital helpdesk."
            )

        return redirect('patient_dashboard')

    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/cancel_confirm.html', context)


def medical_report_detail(request, report_id):
    """View and print medical report and doctor prescription."""
    report = get_object_or_404(
        MedicalReport.objects.select_related('appointment', 'patient', 'doctor'),
        pk=report_id
    )

    context = {
        'report': report,
        'appointment': report.appointment,
        'patient': report.patient,
        'doctor': report.doctor,
    }
    return render(request, 'appointments/medical_report.html', context)


def api_booked_slots(request):
    """API endpoint to get booked slots for a given doctor and date."""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'booked_slots': []})

    try:
        booked = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date_str
        ).exclude(status='Cancelled').values_list('time_slot', flat=True)

        return JsonResponse({'booked_slots': list(booked)})
    except Exception as e:
        return JsonResponse({'error': str(e), 'booked_slots': []}, status=400)