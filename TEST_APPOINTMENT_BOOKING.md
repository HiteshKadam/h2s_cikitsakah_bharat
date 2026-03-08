# Test Appointment Booking - Step by Step

## 🚀 Prerequisites

1. Backend server running: `python manage.py runserver`
2. Frontend server running: `npm start` or `ng serve`
3. Database has at least one doctor record

## 🧪 Test Steps

### Step 1: Test Doctor Details API
```bash
curl "http://localhost:8000/api/doctors/8/?type=human"
```

**Expected**: JSON response with doctor details including `address_details` object

**If it fails**: Check that doctor ID 8 exists in your database

### Step 2: Test Available Slots API
```bash
curl "http://localhost:8000/api/doctors/8/slots/?date=2026-03-15&type=human"
```

**Expected**: JSON response with array of time slots

### Step 3: Test Frontend Flow

#### 3.1 Navigate to Home
- Open browser: `http://localhost:4200`
- Should see care type selection

#### 3.2 Select Care Type
- Click "Human Healthcare" or "Pet Healthcare"
- Should navigate to symptoms page

#### 3.3 Enter Symptoms
- Type: "chest pain and difficulty breathing"
- Click "Analyze & Find Doctors"
- Allow location permission when prompted

#### 3.4 View Doctor Results
- Should see doctor cards with:
  - Doctor name
  - Specialization
  - Match score
  - Distance
  - "Book Appointment" button

#### 3.5 Book Appointment
- Click "Book Appointment" on any doctor
- Should navigate to `/appointment/:doctorId`
- Should see:
  - Doctor details loaded (name, specialization, location)
  - Patient/Owner information form
  - Date picker (minimum date = today)
  - Time slot dropdown

#### 3.6 Fill Form (Human)
- First Name: "John"
- Last Name: "Doe"
- Contact Number: "9876543210"
- Email: "john@example.com" (optional)
- Date: Select tomorrow
- Time: Select any available slot
- Reason: "Chest pain checkup"

#### 3.7 Fill Form (Pet)
- Owner Name: "Jane Smith"
- Owner Phone: "9876543210"
- Owner Email: "jane@example.com" (optional)
- Pet Name: "Max"
- Species: "Dog"
- Breed: "Golden Retriever" (optional)
- Date: Select tomorrow
- Reason: "Vaccination"

#### 3.8 Submit
- Click "Confirm Booking"
- Should see loading spinner
- Should see success alert with appointment ID
- Should navigate back to symptoms page

### Step 4: Test Backend Appointment Creation

#### Human Appointment
```bash
curl -X POST http://localhost:8000/api/appointments/human/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 8,
    "patient_first_name": "Test",
    "patient_last_name": "Patient",
    "contact_number": "9876543210",
    "email_id": "test@example.com",
    "scheduling_date": "2026-03-15",
    "scheduling_time": "10:00",
    "reason": "Checkup"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "appointment_id": 123,
  "patient_created": true,
  "appointment": {
    "appointment_id": 123,
    "scheduling_date": "2026-03-15",
    "scheduling_time": "10:00:00",
    "status": "scheduled",
    "patient_details": {...},
    "doctor_details": {...}
  }
}
```

#### Pet Appointment
```bash
curl -X POST http://localhost:8000/api/appointments/animal/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "owner_name": "Test Owner",
    "owner_phone": "9876543210",
    "animal_name": "Buddy",
    "species": "Dog",
    "appointment_date": "2026-03-15",
    "reason": "Vaccination"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "appointment_id": 456,
  "owner_created": true,
  "animal_created": true,
  "appointment": {
    "appointment_id": 456,
    "appointment_date": "2026-03-15",
    "status": "scheduled",
    "doctor_name": "Dr. Vet Name",
    "animal_name": "Buddy",
    "owner_name": "Test Owner"
  }
}
```

## ✅ Success Criteria

### Backend
- [ ] Doctor details API returns 200 with correct data structure
- [ ] Available slots API returns 200 with slot array
- [ ] Human appointment creation returns 201 with appointment ID
- [ ] Pet appointment creation returns 201 with appointment ID
- [ ] Patient/Owner records created in database
- [ ] Appointment records created in database

### Frontend
- [ ] Doctor details load without errors
- [ ] Address details display correctly (city, state)
- [ ] Available slots load and display
- [ ] Form validation works (submit disabled until valid)
- [ ] Date change triggers slot reload
- [ ] Form submission shows loading state
- [ ] Success message displays with appointment ID
- [ ] Navigation works after booking

## 🐛 Troubleshooting

### Error: "Doctor not found"
- Check doctor ID exists in database
- Verify doctor_id parameter is correct
- Check database connection

### Error: "address_details not in fields"
- **FIXED**: This was the serializer issue
- Restart Django server to reload code
- Clear browser cache

### Error: "Failed to load doctor details"
- Check browser console for errors
- Verify API endpoint URL is correct
- Check CORS settings in Django

### Slots Not Loading
- Check date format is YYYY-MM-DD
- Verify doctor has working hours set
- Check browser console for errors

### Form Not Submitting
- Check all required fields are filled
- Verify date is not in the past
- Check browser console for validation errors

## 📊 Database Verification

### Check Appointment Created
```sql
-- Human appointments
SELECT * FROM appointment 
WHERE appointment_id = <your_appointment_id>;

-- Animal appointments  
SELECT * FROM appointment 
WHERE appointment_id = <your_appointment_id>;
```

### Check Patient Created
```sql
SELECT * FROM patients 
WHERE contact_number = '9876543210';
```

### Check Owner/Animal Created
```sql
SELECT * FROM owner WHERE phone = '9876543210';
SELECT * FROM animal WHERE owner_id = <owner_id>;
```

## 🎯 Expected Behavior

1. **First Booking**: Creates new patient/owner/animal records
2. **Repeat Booking**: Reuses existing patient/owner/animal records
3. **Slot Availability**: Booked slots marked as unavailable
4. **Status**: All appointments created with status "scheduled"
5. **Validation**: Invalid data rejected with error messages

## 📝 Test Checklist

- [ ] Backend APIs tested with curl
- [ ] Frontend flow tested end-to-end
- [ ] Human appointment booking works
- [ ] Pet appointment booking works
- [ ] Form validation works
- [ ] Slot availability updates
- [ ] Database records created
- [ ] Error handling works
- [ ] Success messages display
- [ ] Navigation works

---

**Status**: Ready for Testing
**Last Updated**: March 8, 2026
