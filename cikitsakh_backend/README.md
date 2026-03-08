# Cikitsakh Backend API

Django REST API for the Cikitsakh medical appointment system with symptom matching AI and location-based doctor search.

## Features

- Symptom analysis with AI-based specialty matching
- Location-based doctor search using Haversine distance calculation
- Human and animal (pet) doctor filtering
- REST API endpoints for frontend integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `cikitsakh_backend/settings.py`

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## API Endpoints

### Doctor Search
- `GET /api/doctors/` - List all doctors with filters
  - Query params: `patient_type`, `specialization`, `city`, `min_rating`

- `GET /api/doctors/nearby/` - Find nearby doctors
  - Query params: `latitude`, `longitude`, `radius`, `patient_type`, `specialization`

### Symptom Analysis
- `POST /api/analyze-symptoms/` - Analyze symptoms
  - Body: `{ "symptoms": "...", "patient_type": "human|pet" }`

- `POST /api/search-doctors/` - Combined symptom analysis + doctor search
  - Body: `{ "symptoms": "...", "patient_type": "human|pet", "latitude": float, "longitude": float, "radius": float }`

## Database Models

### Doctor Model
- `name`: Doctor's name
- `specialization`: Medical specialty
- `patient_type`: 'human' or 'pet'
- `city`: City location
- `latitude`, `longitude`: GPS coordinates
- `rating`: Doctor rating (0-5)
