import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from appointments.models import Doctor, Patient, Appointment, MedicalReport
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Seed database with initial doctors, sample patients, appointments, and medical reports."

    def handle(self, *args, **options):
        self.stdout.write("Seeding CarePlus Hospital data...")

        # 1. Create or verify Admin superuser for the user
        User = get_user_model()
        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@careplus.health')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(admin_username, admin_email, admin_password)
            self.stdout.write(self.style.SUCCESS(f"Created admin superuser: username='{admin_username}', password='{admin_password}'"))
        else:
            self.stdout.write("Admin superuser already exists.")

        # 2. Seed Doctors across Cardiology, Pediatrics, Orthopedics, Neurology
        doctors_data = [
            # Cardiology
            {
                'name': 'Dr. Sarah Jenkins, MD',
                'department': 'Cardiology',
                'specialization': 'Senior Interventional Cardiologist',
                'qualification': 'MBBS, MD (Cardiology), FACC',
                'experience_years': 15,
                'consultation_fee': 85.00,
                'room_number': 'Suite 201, Heart Center',
                'phone': '+1 (800) 432-201',
                'email': 's.jenkins@careplus.health',
                'bio': 'Dr. Jenkins has performed over 2,500 coronary interventions and specializes in primary angioplasty, transcatheter aortic valve replacement (TAVR), and preventive heart clinics.',
                'avatar_url': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },
            {
                'name': 'Dr. Michael Chang, MD',
                'department': 'Cardiology',
                'specialization': 'Consultant Electrophysiologist',
                'qualification': 'MBBS, MD (Medicine), FESC',
                'experience_years': 11,
                'consultation_fee': 75.00,
                'room_number': 'Suite 204, Heart Center',
                'phone': '+1 (800) 432-204',
                'email': 'm.chang@careplus.health',
                'bio': 'Specialist in cardiac arrhythmias, radiofrequency catheter ablation, and permanent pacemaker/ICD implantations with 11+ years of academic and clinical excellence.',
                'avatar_url': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },

            # Pediatrics
            {
                'name': 'Dr. Emily Rodriguez, MD',
                'department': 'Pediatrics',
                'specialization': 'Chief Neonatologist & Pediatrician',
                'qualification': 'MBBS, MD (Pediatrics), FAAP',
                'experience_years': 16,
                'consultation_fee': 65.00,
                'room_number': 'Cabin 102, Children Wing',
                'phone': '+1 (800) 432-102',
                'email': 'e.rodriguez@careplus.health',
                'bio': 'Compassionate pediatric specialist caring for newborns, infants, and adolescents. Head of the Level III Neonatal Intensive Care Unit (NICU).',
                'avatar_url': 'https://images.unsplash.com/photo-1594824813524-8b6b0c169c9b?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },
            {
                'name': 'Dr. David Patel, MD',
                'department': 'Pediatrics',
                'specialization': 'Pediatric Allergy & Immunology',
                'qualification': 'MBBS, DCH, MD (Pediatrics)',
                'experience_years': 9,
                'consultation_fee': 60.00,
                'room_number': 'Cabin 106, Children Wing',
                'phone': '+1 (800) 432-106',
                'email': 'd.patel@careplus.health',
                'bio': 'Specialized in childhood asthma, food allergies, eczema, growth milestone evaluations, and immunization schedules.',
                'avatar_url': 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },

            # Orthopedics
            {
                'name': 'Dr. James Wilson, MS',
                'department': 'Orthopedics',
                'specialization': 'Robotic Joint Replacement Surgeon',
                'qualification': 'MBBS, MS (Ortho), MCh (Joints)',
                'experience_years': 18,
                'consultation_fee': 90.00,
                'room_number': 'OPD Suite 301, Bone Center',
                'phone': '+1 (800) 432-301',
                'email': 'j.wilson@careplus.health',
                'bio': 'Pioneer in robotic-assisted total knee and hip arthroplasty, complex trauma fracture reconstruction, and degenerative arthritis treatments.',
                'avatar_url': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },
            {
                'name': 'Dr. Rachel Adams, MS',
                'department': 'Orthopedics',
                'specialization': 'Sports Medicine & Arthroscopy',
                'qualification': 'MBBS, MS (Orthopedics), DNB',
                'experience_years': 10,
                'consultation_fee': 75.00,
                'room_number': 'OPD Suite 305, Bone Center',
                'phone': '+1 (800) 432-305',
                'email': 'r.adams@careplus.health',
                'bio': 'Expert in arthroscopic reconstruction of ACL, meniscus, rotator cuff repairs, and advanced musculoskeletal rehabilitation for athletes.',
                'avatar_url': 'https://images.unsplash.com/photo-1559839734-b258ff09395d?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },

            # Neurology
            {
                'name': 'Dr. Robert Henderson, DM',
                'department': 'Neurology',
                'specialization': 'Senior Neurologist & Stroke Care',
                'qualification': 'MBBS, MD, DM (Neurology), FAAN',
                'experience_years': 20,
                'consultation_fee': 95.00,
                'room_number': 'Suite 401, Neuro Wing',
                'phone': '+1 (800) 432-401',
                'email': 'r.henderson@careplus.health',
                'bio': 'Director of Stroke & Neurovascular Center. Expertise in stroke thrombolysis, epilepsy syndromes, Parkinson’s disease, and memory disorders.',
                'avatar_url': 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },
            {
                'name': 'Dr. Priya Sharma, DM',
                'department': 'Neurology',
                'specialization': 'Neuro-Physiologist & Headache Specialist',
                'qualification': 'MBBS, MD (Medicine), DM (Neuro)',
                'experience_years': 12,
                'consultation_fee': 80.00,
                'room_number': 'Suite 404, Neuro Wing',
                'phone': '+1 (800) 432-404',
                'email': 'p.sharma@careplus.health',
                'bio': 'Expertise in chronic migraine management, neuro-electrophysiology (EEG/EMG/NCV), neuromuscular junction disorders, and neuropathies.',
                'avatar_url': 'https://images.unsplash.com/photo-1594824813524-8b6b0c169c9b?auto=format&fit=crop&q=80&w=400',
                'is_available': True,
            },
        ]

        created_doctors = []
        for doc_info in doctors_data:
            doc, created = Doctor.objects.get_or_create(
                name=doc_info['name'],
                defaults=doc_info
            )
            created_doctors.append(doc)

        self.stdout.write(self.style.SUCCESS(f"Verified/Created {len(created_doctors)} specialist doctors."))

        # 3. Seed Sample Patient
        patient1, _ = Patient.objects.get_or_create(
            phone='+1 (555) 987-6543',
            defaults={
                'first_name': 'Eleanor',
                'last_name': 'Vance',
                'email': 'eleanor.vance@example.com',
                'age': 38,
                'gender': 'Female',
                'blood_group': 'O+',
                'address': '452 Elmwood Avenue, Apartment 4B',
                'emergency_contact': '+1 (555) 321-7654',
            }
        )

        patient2, _ = Patient.objects.get_or_create(
            phone='+1 (555) 456-7890',
            defaults={
                'first_name': 'Alexander',
                'last_name': 'Hayes',
                'email': 'alex.hayes@example.com',
                'age': 45,
                'gender': 'Male',
                'blood_group': 'A+',
                'address': '890 Crestview Road, Suite 12',
                'emergency_contact': '+1 (555) 654-9870',
            }
        )
        self.stdout.write(self.style.SUCCESS("Verified/Created sample patients."))

        # 4. Seed Appointments
        today = timezone.localdate()
        doc_cardio = created_doctors[0]  # Dr. Sarah Jenkins
        doc_ortho = created_doctors[4]   # Dr. James Wilson
        doc_neuro = created_doctors[6]   # Dr. Robert Henderson

        # Upcoming Confirmed Appointment
        appt1, created1 = Appointment.objects.get_or_create(
            patient=patient1,
            doctor=doc_cardio,
            appointment_date=today + timedelta(days=2),
            time_slot='10:00 AM',
            defaults={
                'reason_for_visit': 'Routine cardiovascular checkup, mild palpitations after exertion.',
                'status': 'Confirmed',
                'notes': 'Patient requested morning review.',
            }
        )

        # Upcoming Pending Appointment
        appt2, created2 = Appointment.objects.get_or_create(
            patient=patient2,
            doctor=doc_ortho,
            appointment_date=today + timedelta(days=3),
            time_slot='02:30 PM',
            defaults={
                'reason_for_visit': 'Right knee pain aggravated when climbing stairs, previous runner injury.',
                'status': 'Pending',
                'notes': 'First visit to Orthopedics.',
            }
        )

        # Completed Appointment with Medical Report
        appt3, created3 = Appointment.objects.get_or_create(
            patient=patient1,
            doctor=doc_neuro,
            appointment_date=today - timedelta(days=5),
            time_slot='11:00 AM',
            defaults={
                'reason_for_visit': 'Episodes of throbbing unilateral headaches and visual aura.',
                'status': 'Completed',
                'notes': 'Completed review. Medication prescribed.',
            }
        )

        # Create Medical Report for appt3 if not exists
        if not hasattr(appt3, 'medical_report'):
            MedicalReport.objects.create(
                appointment=appt3,
                patient=patient1,
                doctor=doc_neuro,
                report_date=today - timedelta(days=5),
                blood_pressure='118/76 mmHg',
                heart_rate='68 bpm',
                temperature='98.4 °F',
                respiratory_rate='15 bpm',
                diagnosis='Episode of Migraine with Typical Aura (ICD-10 G43.1). No focal neurological deficit detected on physical examination.',
                prescription="1. Tab. Zolmitriptan 2.5mg (At the onset of headache aura, max 2 tabs/24h)\n2. Tab. Propranolol 40mg once daily at bedtime (Prophylaxis)\n3. Tab. Naproxen 500mg as needed for acute pain\n4. Maintain strict hydration (>2.5L water/day)",
                doctor_notes='Patient advised to maintain a headache diary tracking potential triggers (caffeine, sleep deprivation, bright screens). Avoid skipping meals.',
                follow_up_date=today + timedelta(days=25)
            )
            self.stdout.write(self.style.SUCCESS("Created sample MedicalReport for completed visit."))

        self.stdout.write(self.style.SUCCESS("Successfully seeded CarePlus Hospital portal with doctors, patients, appointments, and medical report!"))
