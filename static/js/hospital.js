// ==========================================================================
// CarePlus Hospital Portal - Frontend JavaScript Logic
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {
    initDatePickerMin();
    initBookingSlotChecker();
    initDepartmentDoctorFilter();
});

/**
 * Ensure appointment date picker cannot select past dates
 */
function initDatePickerMin() {
    const dateInput = document.getElementById('id_appointment_date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        if (!dateInput.value) {
            dateInput.value = today;
        }
    }
}

/**
 * Live Slot Checker: Queries Django API for booked slots
 * Disables slots that are already booked for the selected doctor & date
 */
function initBookingSlotChecker() {
    const doctorSelect = document.getElementById('id_doctor');
    const dateInput = document.getElementById('id_appointment_date');
    const slotSelect = document.getElementById('id_time_slot');
    const slotGrid = document.getElementById('slotGridContainer');

    if (!doctorSelect || !dateInput) return;

    function checkSlots() {
        const docId = doctorSelect.value;
        const dateVal = dateInput.value;

        if (!docId || !dateVal) return;

        // Visual feedback indicator
        if (slotGrid) {
            const statusIndicator = document.getElementById('slotLoadingIndicator');
            if (statusIndicator) statusIndicator.style.display = 'inline-block';
        }

        fetch(`/api/booked-slots/?doctor_id=${encodeURIComponent(docId)}&date=${encodeURIComponent(dateVal)}`)
            .then(res => res.json())
            .then(data => {
                const booked = data.booked_slots || [];
                const statusIndicator = document.getElementById('slotLoadingIndicator');
                if (statusIndicator) statusIndicator.style.display = 'none';

                // Update standard select options
                if (slotSelect) {
                    Array.from(slotSelect.options).forEach(opt => {
                        if (!opt.value) return;
                        if (booked.includes(opt.value)) {
                            opt.disabled = true;
                            opt.text = `${opt.value} (Already Booked)`;
                            if (slotSelect.value === opt.value) {
                                slotSelect.value = '';
                            }
                        } else {
                            opt.disabled = false;
                            opt.text = opt.value;
                        }
                    });
                }

                // Update visual interactive grid if rendered
                if (slotGrid) {
                    const buttons = slotGrid.querySelectorAll('.slot-btn');
                    buttons.forEach(btn => {
                        const slot = btn.getAttribute('data-slot');
                        if (booked.includes(slot)) {
                            btn.classList.add('booked', 'disabled');
                            btn.innerHTML = `<i class="bi bi-x-circle"></i> ${slot}`;
                            btn.title = 'This slot is already reserved';
                            if (btn.classList.contains('selected')) {
                                btn.classList.remove('selected');
                                if (slotSelect) slotSelect.value = '';
                            }
                        } else {
                            btn.classList.remove('booked', 'disabled');
                            btn.innerHTML = `<i class="bi bi-clock"></i> ${slot}`;
                            btn.title = 'Click to select this slot';
                        }
                    });
                }
            })
            .catch(err => {
                console.error("Error fetching booked slots:", err);
            });
    }

    doctorSelect.addEventListener('change', checkSlots);
    dateInput.addEventListener('change', checkSlots);

    // Initial check on page load if doctor and date are pre-selected
    if (doctorSelect.value && dateInput.value) {
        checkSlots();
    }
}

/**
 * Department filter for Doctors dropdown in the booking form
 */
function initDepartmentDoctorFilter() {
    const deptSelect = document.getElementById('id_department_filter');
    const doctorSelect = document.getElementById('id_doctor');

    if (!deptSelect || !doctorSelect) return;

    // Cache original options
    const originalOptions = Array.from(doctorSelect.options).map(opt => ({
        value: opt.value,
        text: opt.text,
        dept: opt.getAttribute('data-department') || ''
    }));

    deptSelect.addEventListener('change', function () {
        const selectedDept = this.value;
        const currentSelectedDoc = doctorSelect.value;

        doctorSelect.innerHTML = '';
        originalOptions.forEach(opt => {
            if (!opt.value || !selectedDept || opt.dept.toLowerCase() === selectedDept.toLowerCase()) {
                const newOpt = document.createElement('option');
                newOpt.value = opt.value;
                newOpt.text = opt.text;
                if (opt.dept) newOpt.setAttribute('data-department', opt.dept);
                doctorSelect.appendChild(newOpt);
            }
        });

        // Trigger slot recheck
        const changeEvent = new Event('change');
        doctorSelect.dispatchEvent(changeEvent);
    });
}

/**
 * Handle Slot Grid Button Click
 */
function selectTimeSlot(slotValue, buttonElement) {
    const slotSelect = document.getElementById('id_time_slot');
    if (slotSelect) {
        slotSelect.value = slotValue;
    }

    const grid = document.getElementById('slotGridContainer');
    if (grid) {
        grid.querySelectorAll('.slot-btn').forEach(btn => btn.classList.remove('selected'));
        if (buttonElement && !buttonElement.classList.contains('booked')) {
            buttonElement.classList.add('selected');
        }
    }
}
