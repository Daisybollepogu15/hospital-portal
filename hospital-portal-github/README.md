# CarePlus Hospital & Patient Appointment Management Portal

A modern, full-stack hospital web portal built with **Python 3.11**, **Django 5.2**, **Bootstrap 5**, and **SQLite**. Designed for college assignments, academic presentations, and real-world clinical appointment workflows.

---

## 🌟 Key Features

1. **Hospital Home & Clinical Showcase**:
   - Modern healthcare branding with a clean blue-and-white theme.
   - Hero banner with quick appointment booking CTA.
   - Center of Excellence highlights for **Cardiology**, **Pediatrics**, **Orthopedics**, and **Neurology**.
   - Live hospital statistics, OPD timings, and emergency contact banner.

2. **Physicians Directory & Filters**:
   - Specialist cards with degrees, experience, room/cabin numbers, and consultation fees.
   - Filterable tabs by department (All, Cardiology, Pediatrics, Orthopedics, Neurology).
   - Real-time search by doctor name, specialty, or qualifications.

3. **Smart Appointment Booking**:
   - Form for patient details (Name, Phone, Email, Age, Gender, Blood Group).
   - Real-time **duplicate booking prevention**: prevents clashing reservations for the same doctor, date, and time slot.
   - Prevents selecting past dates.
   - Interactive time-slot grid with live slot availability checks.
   - Automatic generation of unique tracking reference IDs (`CP-2026-XXXX`).

4. **Printable Appointment Pass**:
   - Clean appointment slip with reference code, doctor room location, fee, and patient instructions.
   - One-click print/PDF export.

5. **Patient Portal & Dashboard**:
   - Quick lookup via registered phone number or Appointment ID.
   - Separates **Upcoming Appointments** and **Previous / Completed Records**.
   - One-click cancellation for pending appointments (frees the slot immediately).
   - View and print digital **Medical Reports & Prescriptions**.

6. **Clinical Medical Reports**:
   - Complete diagnostic summaries with vital signs (BP, Heart Rate, Temperature, Respiratory Rate).
   - Digital prescription (Rx) with dosages and clinical guidelines.

7. **Custom Django Admin Portal**:
   - Custom header and branding (`CarePlus Hospital Administration`).
   - Doctor management with fee editing and availability toggles.
   - Appointment tracking with colored status badges (`Pending`, `Confirmed`, `Completed`, `Cancelled`).
   - Bulk status update actions.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11.4, Django 5.2.17
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Database**: SQLite3 (as required by college guidelines)
- **Deployment**: Gunicorn, WhiteNoise, Render (`render.yaml`)

---

## 🚀 How to Run Locally

### 1. Open Terminal in the Project Folder
Ensure you are in the `Hospital Portal` root directory:
```bash
cd "C:\Users\DAISY\OneDrive\Desktop\Hospital Portal"
```

### 2. Apply Migrations (Already configured)
```bash
python manage.py migrate
```

### 3. Seed Sample Hospital Data (Doctors, Patients, Reports)
```bash
python manage.py seed_hospital_data
```
*(This sets up 8 specialist doctors, sample appointments, and an admin account).*

### 4. Start the Django Development Server
```bash
python manage.py runserver
```

### 5. Open in Your Browser
- **Hospital Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Doctor Directory**: [http://127.0.0.1:8000/doctors/](http://127.0.0.1:8000/doctors/)
- **Book Appointment**: [http://127.0.0.1:8000/book/](http://127.0.0.1:8000/book/)
- **Patient Dashboard**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
  - *Test Phone Number*: `+1 (555) 987-6543` (pre-seeded with past and upcoming appointments & medical reports)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Username**: `admin`
  - **Password**: `admin123`

---

## 🧪 Running Automated Tests

To run the complete automated test suite (verifying models, views, duplicate booking detection, slot API, and cancellation):
```bash
python manage.py test
```

---

## ☁️ Deploying to GitHub & Render

### Step 1: Push to GitHub
1. Initialize git and commit:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Complete Hospital & Patient Appointment Management Portal"
   ```
2. Create a new GitHub repository and push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Render
1. Go to [Render.com](https://render.com) and log in.
2. Click **New +** &rarr; **Blueprint** (or **Web Service**).
3. Connect your GitHub repository.
4. Render will automatically detect `render.yaml` and configure:
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py seed_hospital_data && python manage.py collectstatic --no-input`
   - **Start Command**: `gunicorn hospital_config.wsgi:application --bind 0.0.0.0:$PORT`
5. Click **Apply** or **Deploy**. Your hospital portal will be live on a free Render URL!
