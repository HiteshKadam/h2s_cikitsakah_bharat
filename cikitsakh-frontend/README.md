# Cikitsakh Frontend

Angular 21 frontend application for the Cikitsakh medical appointment system with symptom matching AI and location-based doctor search.

## Features

- 🏥 Human and Pet healthcare selection
- 🎤 Voice-enabled symptom input
- 🤖 AI-powered symptom analysis
- 📍 Location-based doctor search
- 🔍 Advanced filtering (specialization, rating, distance)
- 📅 Appointment booking system
- 📱 Responsive design

## Tech Stack

- Angular 21 (Standalone Components)
- TypeScript
- RxJS
- Bootstrap 5
- SCSS

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API endpoint in `src/app/services/api.service.ts`:
```typescript
private baseUrl = 'http://localhost:8000/api';
```

3. Start development server:
```bash
ng serve
```

4. Open browser at `http://localhost:4200`

## Project Structure

```
src/app/
├── components/
│   ├── app-marquee/          # Marquee component
│   └── nearby-doctors/       # Nearby doctors list
├── models/
│   └── doctor.model.ts       # Doctor interfaces
├── pages/
│   ├── home/                 # Care type selection
│   ├── symptoms/             # Symptom input & analysis
│   ├── doctor-list/          # Doctor search results
│   └── appointment/          # Appointment booking
├── services/
│   ├── api.service.ts        # Backend API calls
│   ├── doctor.service.ts     # Doctor data management
│   ├── care-selection.ts     # Care type state
│   └── location.service.ts   # Geolocation handling
└── app.routes.ts             # Route configuration
```

## Key Components

### Home Component
- Care type selection (Human/Pet)
- Entry point for the application

### Symptoms Component
- Text and voice symptom input
- AI-powered symptom analysis
- Recommended doctors display
- Severity detection

### Nearby Doctors Component
- Location-based doctor search
- Advanced filtering options
- Sorting by distance, rating, experience
- Responsive card layout

### Doctor List Component
- Search doctors by specialty and range
- Filter by care type
- Navigate to appointment booking

### Appointment Component
- Book appointments with selected doctor
- Patient information form
- Date and time selection

## Services

### ApiService
Handles all HTTP requests to backend:
- `analyzeSymptoms()` - Symptom analysis
- `searchDoctorsBySymptoms()` - Combined search
- `getNearbyDoctors()` - Location-based search
- `getHumanDoctors()` - Human doctor list
- `getVetDoctors()` - Vet doctor list

### DoctorService
Manages doctor data and transformations:
- `searchHumanDoctors()` - Search human doctors
- `searchVetDoctors()` - Search vet doctors
- `getNearbyHumanDoctors()` - Nearby human doctors
- `getNearbyVetDoctors()` - Nearby vet doctors

### CareSelectionService
Manages care type state (human/pet) across components

### LocationService
Handles geolocation API for user location

## API Integration

The frontend connects to Django backend at `http://localhost:8000/api`:

- `POST /analyze-symptoms/` - Analyze symptoms
- `POST /search-doctors/` - Search by symptoms
- `GET /human-doctors/nearby/` - Nearby human doctors
- `GET /vet-doctors/nearby/` - Nearby vet doctors
- `GET /human-doctors/` - List human doctors
- `GET /vet-doctors/` - List vet doctors

## Design System

### Colors
- Primary: `#593196` (Purple)
- Secondary: `#883cf9` (Light Purple)
- Success: `#16a34a` (Green)
- Danger: `#ef4444` (Red)

### Typography
- Font Family: Inter, system fonts
- Weights: 300, 400, 500, 600, 700

### Components
- Cards with hover effects
- Rounded corners (8px-20px)
- Soft shadows
- Smooth transitions

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Features to Implement

- [ ] User authentication
- [ ] Appointment history
- [ ] Doctor reviews and ratings
- [ ] Payment integration
- [ ] Real-time notifications
- [ ] Chat with doctors
- [ ] Medical records upload
- [ ] Prescription management

## Development

Run tests:
```bash
ng test
```

Build for production:
```bash
ng build --configuration production
```

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request
