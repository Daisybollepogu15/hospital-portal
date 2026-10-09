from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from appointments.models import Doctor, Patient, Appointment, MedicalReport
from appointments.forms import AppointmentBookingForm


class HospitalPortalTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.doctor = Doctor.objects.create(
            name='Dr. Test Cardiologist, MD',
            department='Cardiology',
            specialization='Interventional Cardiology',
            qualification='MBBS, MD',
            experience_years=10,
            consultation_fee=100.00,
            room_number='Room 101',
            is_available=True
        )
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Tester',
            email='john@example.com',
            phone='+15551234567',
            age=35,
            gender='Male'
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CarePlus')
        self.assertContains(response, 'Cardiology')

    def test_doctors_list_page(self):
        response = self.client.get(reverse('doctors_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Test Cardiologist')

        # Test filter by department
        response_filtered = self.client.get(reverse('doctors_list') + '?dept=Cardiology')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertContains(response_filtered, 'Dr. Test Cardiologist')

    def test_doctor_detail_page(self):
        response = self.client.get(reverse('doctor_detail', args=[self.doctor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Test Cardiologist')

    def test_departments_pages(self):
        response = self.client.get(reverse('departments_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cardiology')
        self.assertContains(response, 'Pediatrics')

        response_dept = self.client.get(reverse('department_detail', args=['Cardiology']))
        self.assertEqual(response_dept.status_code, 200)
        self.assertContains(response_dept, 'Department of Cardiology')

    def test_booking_appointment_success(self):
        booking_date = timezone.localdate() + timedelta(days=2)
        post_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '+15559876543',
            'email': 'jane.doe@example.com',
            'age': 28,
            'gender': 'Female',
            'blood_group': 'B+',
            'doctor': self.doctor.id,
            'appointment_date': booking_date.strftime('%Y-%m-%d'),
            'time_slot': '10:00 AM',
            'reason_for_visit': 'Annual heart health checkup',
        }
        response = self.client.post(reverse('book_appointment'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirects to confirmation

        # Verify created appointment
        appt = Appointment.objects.get(patient__phone='+15559876543')
        self.assertEqual(appt.doctor, self.doctor)
        self.assertEqual(appt.time_slot, '10:00 AM')
        self.assertEqual(appt.status, 'Pending')

    def test_duplicate_booking_prevention(self):
        booking_date = timezone.localdate() + timedelta(days=3)
        # Create initial appointment
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot='11:00 AM',
            reason_for_visit='Initial consultation',
            status='Confirmed'
        )

        # Attempt to book exact same doctor, date, and slot
        conflict_data = {
            'first_name': 'Second',
            'last_name': 'Patient',
            'phone': '+15550001111',
            'email': 'second@example.com',
            'gender': 'Male',
            'doctor': self.doctor.id,
            'appointment_date': booking_date.strftime('%Y-%m-%d'),
            'time_slot': '11:00 AM',
            'reason_for_visit': 'Second visit clash attempt',
        }
        form = AppointmentBookingForm(data=conflict_data)
        self.assertFalse(form.is_valid())
        self.assertIn("already has an active booking", str(form.errors))

    def test_past_date_booking_prevention(self):
        past_date = timezone.localdate() - timedelta(days=1)
        data = {
            'first_name': 'Late',
            'last_name': 'Patient',
            'phone': '+15552223333',
            'email': 'late@example.com',
            'gender': 'Male',
            'doctor': self.doctor.id,
            'appointment_date': past_date.strftime('%Y-%m-%d'),
            'time_slot': '09:00 AM',
            'reason_for_visit': 'Late attempt',
        }
        form = AppointmentBookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Appointment date cannot be in the past", str(form.errors))

    def test_patient_dashboard_lookup(self):
        booking_date = timezone.localdate() + timedelta(days=4)
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot='02:30 PM',
            reason_for_visit='Checkup',
            status='Pending'
        )

        # Search by phone number
        response = self.client.get(reverse('patient_dashboard'), {'query': self.patient.phone})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.full_name)
        self.assertContains(response, appt.appointment_id)

    def test_appointment_cancellation(self):
        booking_date = timezone.localdate() + timedelta(days=5)
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot='03:00 PM',
            reason_for_visit='Need cancellation',
            status='Pending'
        )

        response = self.client.post(reverse('cancel_appointment', args=[appt.appointment_id]))
        self.assertEqual(response.status_code, 302)

        appt.refresh_from_db()
        self.assertEqual(appt.status, 'Cancelled')

    def test_api_booked_slots(self):
        booking_date = timezone.localdate() + timedelta(days=6)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=booking_date,
            time_slot='09:30 AM',
            reason_for_visit='Testing API',
            status='Pending'
        )

        url = f"{reverse('api_booked_slots')}?doctor_id={self.doctor.id}&date={booking_date.strftime('%Y-%m-%d')}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('09:30 AM', data['booked_slots'])
