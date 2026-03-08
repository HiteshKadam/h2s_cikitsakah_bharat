# Testing Guide - Cikitsakh Application

## 🧪 Backend Testing

### 1. Start the Backend Server
```bash
cd cikitsakh_backend
python manage.py runserver
```

Expected output:
```
Django version 6.0.3, using settings 'cikitsakh_backend.settings'
Starting development server at http://127.0.0.1:8000/
```

### 2. Test ML Symptom Analyzer

#### Test Case 1: Heart-related symptoms
```bash
curl -X POST http://127.0.0.1:8000/api/search-doctors/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "severe chest pain, shortness of breath, palpitations",
    "patient_type": "human",
    "latitude": 19.2325,
    "longitude": 73.0848,
    "radius": 10
  }'
```

Expected response:
- `recommended_specialties`: ["cardiology", ...]
- `confidence_scores`: {"cardiology": 0.85+}
- `severity`: "severe"
- `urgency`: "immediate"

#### Test Case 2: Skin-related symptoms
```bash
curl -X POST http://127.0.0.1:8000/api/search-doctors/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "itchy rash on arms, red spots, dry skin",
    "patient_type": "human",
    "latitude": 19.2325,
    "longitude": 73.0848,
    "radius": 10
  }'
```

Expected response:
- `recommended_specialties`: ["dermatology", ...]
- `confidence_scores`: {"dermatology": 0.80+}

#### Test Case 3: Pet symptoms
```bash
curl -X POST http://127.0.0.1:8000/api/search-doctors/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "my dog is not eating, vomiting, very tired",
    "patient_type": "pet",
    "latitude": 19.2325,
    "longitude": 73.0848,
    "radius": 10
  }'
```

Expected response:
- `recommended_specialties`: ["veterinary_general", ...]
- `patient_type`: "pet"

### 3. Test Progressive Search

#### Test with remote location (should expand radius)
```bash
curl -X POST http://127.0.0.1:8000/api/search-doctors/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "headache and fever",
    "patient_type": "human",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "radius": 10
  }'
```

Expected response:
- `search_expanded`: true
- `search_radius`: 20, 50, or 100 (depending on results)
- `initial_radius`: 10
- `search_attempts`: Array showing expansion attempts

### 4. Test Nearby Doctors Endpoint
```bash
curl "http://127.0.0.1:8000/api/human-doctors/nearby/?latitude=19.2325&longitude=73.0848&radius=50"
```

Expected response:
- Array of doctors with distance calculations
- Sorted by distance

## 🌐 Frontend Testing

### 1. Start the Frontend
```bash
cd cikitsakh-frontend
npm start
# or
ng serve
```

Navigate to: `http://localhost:4200`

### 2. Test User Flow

#### Step 1: Select Care Type
- Click "Human Healthcare" or "Pet Healthcare"
- Should navigate to symptoms page

#### Step 2: Enter Symptoms
- Type symptoms in text area
- OR click microphone icon for voice input
- Examples:
  - "I have severe chest pain and difficulty breathing"
  - "My skin is itchy with red rashes"
  - "Persistent headache for 3 days"

#### Step 3: Analyze and Search
- Click "Analyze & Find Doctors"
- Browser should request location permission
- Loading indicator should appear

#### Step 4: View Results
- Analysis card should show:
  - Recommended specialties
  - Confidence scores
  - Severity level
  - Recommendations
- Doctor cards should show:
  - Doctor name and photo
  - Specialization
  - Match score (percentage)
  - Distance from user
  - Rating
  - Experience
  - Location

#### Step 5: Book Appointment
- Click "Book Appointment" on any doctor card
- Should navigate to appointment page

### 3. Test Edge Cases

#### No Location Permission
- Deny location permission
- Should show alert: "Please enable location services"

#### No Symptoms Entered
- Click "Analyze & Find Doctors" without entering symptoms
- Should show alert: "Please enter symptoms"

#### No Doctors Found
- Enter very specific symptoms in remote area
- Should show message about expanding search
- May show city-based results

## 🔍 Debugging

### Backend Logs
Watch the Django console for:
- Request logs: `[08/Mar/2026 19:23:45] "POST /api/search-doctors/ HTTP/1.1" 200`
- Error traces if any
- ML model initialization messages

### Frontend Console
Open browser DevTools (F12) and check:
- Network tab for API calls
- Console for JavaScript errors
- Response data from backend

### Common Issues

#### Issue: "np.matrix is not supported"
**Status**: ✅ FIXED
**Solution**: Already applied in `symptom_analyzer.py`

#### Issue: No doctors found
**Check**:
1. Database has doctors in the area
2. Specialization matches symptoms
3. Progressive search is working (check `search_expanded` flag)

#### Issue: CORS errors
**Check**:
1. Backend CORS settings in `settings.py`
2. Frontend is running on `http://localhost:4200`
3. Backend is running on `http://127.0.0.1:8000`

#### Issue: Location not working
**Check**:
1. Browser supports geolocation API
2. HTTPS or localhost (required for geolocation)
3. User granted location permission

## 📊 Performance Metrics

### Expected Performance
- ML Analysis: 30-50ms
- Database Query: 50-200ms
- Total API Response: < 500ms
- Frontend Render: < 100ms

### Monitoring
```python
# Add to views.py for timing
import time
start = time.time()
# ... your code ...
print(f"Execution time: {(time.time() - start) * 1000}ms")
```

## ✅ Success Criteria

### Backend
- [ ] Server starts without errors
- [ ] ML model initializes successfully
- [ ] API returns 200 status
- [ ] Symptom analysis returns correct specialties
- [ ] Progressive search expands radius when needed
- [ ] Doctors are ranked by match score

### Frontend
- [ ] App loads without errors
- [ ] Care type selection works
- [ ] Symptom input (text and voice) works
- [ ] Location permission requested
- [ ] Analysis results display correctly
- [ ] Doctor cards show all information
- [ ] Match scores are visible
- [ ] Appointment booking navigation works

## 🎯 Test Scenarios

### Scenario 1: Emergency Case
**Input**: "severe chest pain, can't breathe, sweating"
**Expected**:
- Specialty: Cardiology
- Severity: Severe
- Urgency: Immediate
- Recommendation: "⚠️ Seek immediate medical attention"

### Scenario 2: Routine Checkup
**Input**: "general health checkup, feeling fine"
**Expected**:
- Specialty: General
- Severity: Mild
- Urgency: Routine
- Recommendation: "Schedule a routine consultation"

### Scenario 3: Pet Emergency
**Input**: "my dog is vomiting blood, very weak"
**Expected**:
- Specialty: Veterinary General/Surgery
- Patient Type: Pet
- Severity: Severe
- Urgency: Immediate

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

Backend Tests:
[ ] Server starts successfully
[ ] ML analyzer works
[ ] Progressive search works
[ ] API responses correct

Frontend Tests:
[ ] Care selection works
[ ] Symptom input works
[ ] Location permission works
[ ] Results display correctly
[ ] Appointment booking works

Issues Found:
1. ___________
2. ___________

Notes:
___________
```
