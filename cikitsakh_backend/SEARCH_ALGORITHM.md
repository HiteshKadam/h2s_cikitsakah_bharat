# Progressive Search Algorithm

## Overview
The doctor search system implements a progressive fallback mechanism to ensure patients always find relevant doctors, even in areas with limited availability.

## Search Strategy

### Phase 1: Initial Radius Search (10km)
- Search for doctors within the initial radius (default 10km)
- Filter by recommended specialties from AI analysis
- Calculate distances using Haversine formula

### Phase 2: Progressive Radius Expansion
If no doctors found in Phase 1, expand search radius:
1. **20km radius** - Nearby areas
2. **50km radius** - Extended local area
3. **100km radius** - Regional search

### Phase 3: City-Based Fallback
If still no doctors found after 100km:
1. Identify nearest cities with matching specialists
2. Calculate distance to each city
3. Select top 3 nearest cities
4. Return all matching doctors from those cities
5. Limit results to 20 doctors

## Algorithm Flow

```
User Location + Symptoms
        ↓
AI Symptom Analysis
        ↓
Search within 10km
        ↓
    Found? → YES → Rank & Return
        ↓ NO
Search within 20km
        ↓
    Found? → YES → Rank & Return
        ↓ NO
Search within 50km
        ↓
    Found? → YES → Rank & Return
        ↓ NO
Search within 100km
        ↓
    Found? → YES → Rank & Return
        ↓ NO
Find Nearest Cities
        ↓
Search in Top 3 Cities
        ↓
Rank & Return (up to 20)
```

## Response Structure

```json
{
  "analysis": {
    "recommended_specialties": ["cardiology", "general"],
    "confidence_scores": {"cardiology": 0.95},
    "severity": "moderate",
    "urgency": "within_week"
  },
  "doctors": [...],
  "total_found": 5,
  "search_radius": 50,
  "initial_radius": 10,
  "search_expanded": true,
  "city_based_search": false,
  "search_attempts": [
    {"radius": 10, "method": "location_based"},
    {"radius": 20, "method": "location_based"},
    {"radius": 50, "method": "location_based"}
  ]
}
```

## Benefits

1. **Always Find Doctors**: Progressive expansion ensures results
2. **Relevant Results**: AI ranking prioritizes best matches
3. **User Awareness**: Frontend shows search radius expansion
4. **Performance**: Stops searching once doctors are found
5. **Scalability**: Works in both dense and sparse areas

## Distance Calculation

Uses Haversine formula for accurate geographic distance:
```python
def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert to radians
    # Calculate using Earth's radius (6371 km)
    # Returns distance in kilometers
```

## Future Enhancements

1. Geocoding integration for accurate coordinates
2. Real-time traffic-based distance
3. Public transport accessibility
4. Doctor availability filtering
5. Multi-city parallel search
6. Caching for frequently searched locations
