from django.contrib import admin
from django.utils.html import format_html
from .models import Doctor, Patient, Appointment, MedicalReport

admin.site.site_header = "CarePlus Hospital Administration"
admin.site.site_title = "CarePlus Admin Portal"
admin.site.index_title = "Hospital & Appointment Management"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'department',
        'specialization',
        'experience_years',
        'consultation_fee',
        'room_number',
        'is_available',
    )
    list_filter = ('department', 'is_available')
    search_fields = ('name', 'specialization', 'qualification', 'room_number')
    list_editable = ('is_available', 'consultation_fee')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'department', 'specialization', 'qualification', 'bio', 'avatar_url')
        }),
        ('Practice Details', {
            'fields': ('experience_years', 'consultation_fee', 'room_number', 'is_available')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'phone',
        'email',
        'gender',
        'age',
        'blood_group',
        'created_at',
    )
    list_filter = ('gender', 'blood_group')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('created_at',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'appointment_id',
        'patient_display',
        'doctor_display',
        'appointment_date',
        'time_slot',
        'status_badge',
        'created_at',
    )
    list_filter = ('status', 'appointment_date', 'doctor__department')
    search_fields = (
        'appointment_id',
        'patient__first_name',
        'patient__last_name',
        'patient__phone',
        'doctor__name',
    )
    date_hierarchy = 'appointment_date'
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    def patient_display(self, obj):
        return obj.patient.full_name
    patient_display.short_description = "Patient"

    def doctor_display(self, obj):
        return f"{obj.doctor.name} ({obj.doctor.department})"
    doctor_display.short_description = "Doctor"

    def status_badge(self, obj):
        colors = {
            'Pending': '#eab308',     # amber
            'Confirmed': '#2563eb',   # blue
            'Completed': '#16a34a',   # green
            'Cancelled': '#dc2626',   # red
        }
        bg = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.78rem;">{}</span>',
            bg,
            obj.status
        )
    status_badge.short_description = "Status"

    @admin.action(description="Mark selected appointments as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')

    @admin.action(description="Mark selected appointments as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')

    @admin.action(description="Mark selected appointments as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = (
        'report_reference',
        'patient_name',
        'doctor_name',
        'report_date',
        'diagnosis_summary',
        'follow_up_date',
    )
    list_filter = ('report_date', 'doctor__department')
    search_fields = (
        'patient__first_name',
        'patient__last_name',
        'doctor__name',
        'diagnosis',
        'prescription',
    )

    def report_reference(self, obj):
        return f"Report #{obj.id} ({obj.appointment.appointment_id})"
    report_reference.short_description = "Report Reference"

    def patient_name(self, obj):
        return obj.patient.full_name
    patient_name.short_description = "Patient"

    def doctor_name(self, obj):
        return obj.doctor.name
    doctor_name.short_description = "Doctor"

    def diagnosis_summary(self, obj):
        if len(obj.diagnosis) > 60:
            return obj.diagnosis[:60] + "..."
        return obj.diagnosis
    diagnosis_summary.short_description = "Diagnosis"
