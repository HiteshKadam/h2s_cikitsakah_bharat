# Appointment Booking Implementation

## Overview
Complete appointment booking functionality with slot validation for both human and animal patients.

## Features Implemented

### Backend (Django)

1. **Slot Validation**
   - Checks for existing appointments before booking
   - Returns HTTP 409 (Conflict) if slot is already booked
   - Prevents double-booking on the same date/time

2. **Human Appointments** (`/api/appointments/human/create/`)
   - Validates time slot availability
   - Creates or retrieves patient record
   - Books appointment with status 'scheduled'
   - Returns detailed booking confirmation

3. **Animal Appointments** (`/api/appointments/animal/create/`)
   - Validates date availability (currently date-based, not time-based)
   - Creates or retrieves owner and animal records
   - Books appointment with status 'scheduled'
   - Returns detailed booking confirmation

4. **Available Slots Endpoint** (`/api/doctors/{doctor_id}/slots/`)
   - Generates 30-minute time slots based on doctor's working hours
   - Marks slots as available/booked based on existing appointments
   - Returns formatted time slots (e.g., "09:00 AM")

### Frontend (Angular)

1. **Appointment Component**
   - Dynamic form based on care type (human/pet)
   - Real-time slot availability checking
   - Date change triggers slot reload
   - Visual indicators for booked slots
   - Detailed success/error messages

2. **Error Handling**
   - HTTP 409: Shows slot conflict message and reloads slots
   - HTTP 404: Doctor not found
   - HTTP 400: Validation errors
   - HTTP 500: Server errors

3. **User Experience**
   - Shows available slot count
   - Disables booked slots in dropdown
   - Loading states for slot fetching
   - Detailed confirmation messages with appointment details

## API Endpoints

### Get Available Slots
```
GET /api/doctors/{doctor_id}/slots/?date=YYYY-MM-DD&type=human|pet
```

Response:
```json
{
  "success": true,
  "date": "2026-03-10",
  "doctor_id": 1,
  "slots": [
    {
      "time": "09:00",
      "display": "09:00 AM",
      "available": true
    },
    {
      "time": "09:30",
      "display": "09:30 AM",
      "available": false
    }
  ]
}
```

### Create Human Appointment
```
POST /api/appointments/human/create/
```

Request:
```json
{
  "doctor_id": 1,
  "patient_first_name": "John",
  "patient_last_name": "Doe",
  "contact_number": "1234567890",
  "email_id": "john@example.com",
  "scheduling_date": "2026-03-10",
  "scheduling_time": "09:00",
  "reason": "Regular checkup",
  "age": 30
}
```

Success Response (201):
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "appointment_id": 123,
  "booking_details": {
    "doctor_name": "Dr. Jane Smith",
    "patient_name": "John Doe",
    "date": "2026-03-10",
    "time": "09:00"
  }
}
```

Conflict Response (409):
```json
{
  "error": "Slot not available",
  "message": "This time slot is already booked. Please select another time.",
  "booked_slot": {
    "date": "2026-03-10",
    "time": "09:00"
  }
}
```

### Create Animal Appointment
```
POST /api/appointments/animal/create/
```

Request:
```json
{
  "doctor_id": 1,
  "owner_name": "Jane Doe",
  "owner_phone": "1234567890",
  "animal_name": "Max",
  "species": "Dog",
  "breed": "Golden Retriever",
  "age": 3,
  "gender": "Male",
  "weight": 30.5,
  "appointment_date": "2026-03-10",
  "reason": "Vaccination"
}
```

## Database Tables

### Human Appointments (`appointment` table)
- `appointment_id` (PK)
- `patient_id` (FK)
- `doctor_id` (FK)
- `scheduling_date`
- `scheduling_time`
- `status` ('scheduled', 'confirmed', 'completed', 'cancelled')
- `age`

### Animal Appointments (`appointment` table)
- `appointment_id` (PK)
- `doctor_id` (FK)
- `animal_id` (FK)
- `appointment_date`
- `status`

## Important Notes

### Animal Appointment Limitation
Currently, animal appointments only validate by DATE, not by specific TIME. This is because the `appointment` table for animals doesn't have a time field. 

**Recommendation**: Add time fields to animal appointments table for better slot management:
```sql
ALTER TABLE appointment ADD COLUMN appointment_time TIME;
```

Then update the validation logic to check both date AND time for animal appointments.

### Slot Generation
- Default working hours: 9:00 AM - 5:00 PM
- Slot interval: 30 minutes
- Uses doctor's `open_time_1` and `close_time_1` if available

### Status Values
- `scheduled`: Initial booking status
- `confirmed`: Doctor confirmed the appointment
- `completed`: Appointment finished
- `cancelled`: Appointment cancelled

## Testing

1. **Test Slot Availability**
   - Select a date
   - Verify slots are loaded
   - Check that booked slots are disabled

2. **Test Successful Booking**
   - Fill all required fields
   - Select an available slot
   - Submit and verify success message

3. **Test Slot Conflict**
   - Try to book an already booked slot
   - Verify error message appears
   - Verify slots are reloaded

4. **Test Validation**
   - Try submitting with missing fields
   - Verify validation messages

## Future Enhancements

1. Add time field to animal appointments
2. Add appointment cancellation functionality
3. Add appointment rescheduling
4. Send email/SMS confirmations
5. Add appointment reminders
6. Show doctor's schedule/calendar view
7. Add recurring appointments
8. Add waiting list for fully booked dates
