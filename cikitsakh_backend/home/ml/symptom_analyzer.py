from typing import List, Dict, Tuple
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os


class SymptomAnalyzer:
    """
    Fast ML-based symptom analysis using TF-IDF and cosine similarity
    """
    
    def __init__(self):
        self.vectorizer = None
        self.specialty_vectors = None
        self.specialty_names = []
        self.initialize_ml_model()
    
    # Training data for specialties
    HUMAN_SPECIALTY_TRAINING = {
        'cardiology': [
            'chest pain heart palpitation irregular heartbeat shortness breath angina hypertension',
            'heart attack coronary artery disease cardiac arrest blood pressure high',
            'chest tightness racing heart dizzy breathless fatigue weakness',
            'heart murmur valve disease arrhythmia tachycardia bradycardia',
            'swelling legs ankles fluid retention edema cardiovascular'
        ],
        'dermatology': [
            'skin rash acne eczema psoriasis itching hives allergic reaction',
            'moles warts fungal infection dry skin oily skin pigmentation',
            'hair loss nail problems skin lesion dermatitis contact allergy',
            'sunburn skin cancer melanoma basal cell carcinoma',
            'wrinkles aging skin acne scars blemishes pimples blackheads'
        ],
        'orthopedics': [
            'bone fracture joint pain arthritis back pain knee pain shoulder',
            'sprain ligament tear tendon injury muscle pain sports injury',
            'hip pain ankle pain neck pain spine disc herniation',
            'osteoporosis bone density cartilage damage meniscus tear',
            'joint stiffness swelling inflammation mobility limited range motion'
        ],
        'pediatrics': [
            'child infant baby vaccination immunization growth development',
            'newborn toddler pediatric fever cold cough flu',
            'child illness ear infection throat infection tonsillitis',
            'developmental delay milestone speech delay autism screening',
            'childhood diseases measles mumps rubella chickenpox'
        ],
        'neurology': [
            'headache migraine severe head pain cluster headache tension',
            'seizure epilepsy convulsion tremor shaking paralysis weakness',
            'stroke numbness tingling nerve pain sciatica neuropathy',
            'memory loss confusion dementia alzheimer parkinson disease',
            'dizziness vertigo balance problems coordination difficulty'
        ],
        'gastroenterology': [
            'chest pain stomach pain abdominal pain digestion nausea vomiting diarrhea',
            'constipation bloating gas indigestion acid reflux heartburn',
            'ulcer gastritis inflammatory bowel disease crohn colitis',
            'liver disease hepatitis cirrhosis gallstones pancreatitis',
            'food poisoning stomach flu gastroenteritis intestinal problems'
        ],
        'ophthalmology': [
            'eye pain vision blurry double vision blind spots floaters',
            'red eyes watery eyes dry eyes eye strain eye infection',
            'cataract glaucoma macular degeneration retinal detachment',
            'conjunctivitis pink eye stye chalazion eye discharge',
            'vision loss night blindness color blindness eye injury'
        ],
        'ent': [
            'ear pain hearing loss tinnitus ringing ears ear infection',
            'sore throat throat pain swallowing difficulty voice hoarse',
            'nasal congestion sinus infection sinusitis runny nose',
            'tonsillitis adenoids enlarged throat infection strep throat',
            'vertigo balance ear wax blockage eardrum perforation'
        ],
        'pulmonology': [
            'breathing difficulty shortness breath wheezing cough persistent',
            'asthma bronchitis pneumonia lung infection respiratory',
            'chest congestion phlegm mucus chronic cough smoker cough',
            'copd emphysema lung disease tuberculosis tb',
            'sleep apnea snoring breathing stops oxygen low'
        ],
        'endocrinology': [
            'diabetes high blood sugar glucose insulin thyroid',
            'weight gain weight loss unexplained fatigue tired exhausted',
            'excessive thirst frequent urination hunger increased',
            'thyroid nodule goiter hyperthyroid hypothyroid metabolism',
            'hormone imbalance menstrual irregular growth hormone'
        ],
        'general': [
            'fever cold flu body ache chills general weakness',
            'fatigue tired exhausted malaise unwell sick',
            'routine checkup health screening physical examination',
            'preventive care wellness check annual exam',
            'general illness common cold viral infection'
        ]
    }
    
    VET_SPECIALTY_TRAINING = {
        'veterinary_general': [
            'lethargy tired weak appetite loss not eating vomiting',
            'diarrhea loose stool dehydration fever sick unwell',
            'general illness common pet disease viral infection',
            'weight loss poor appetite drinking excessive thirst',
            'behavioral change lethargic depressed inactive'
        ],
        'veterinary_surgery': [
            'injury wound cut laceration bleeding trauma accident',
            'fracture broken bone limping leg injury paw injury',
            'tumor lump mass growth abnormal swelling',
            'surgery needed operation required surgical intervention',
            'foreign body ingestion swallowed object obstruction'
        ],
        'veterinary_dermatology': [
            'skin problem rash itching scratching excessive licking',
            'fur loss hair loss bald patches alopecia',
            'parasites fleas ticks mites mange scabies',
            'hot spots skin infection dermatitis allergic reaction',
            'dry skin oily skin dandruff skin lesion'
        ],
        'veterinary_dental': [
            'teeth problem tooth decay gum disease gingivitis',
            'bad breath halitosis mouth odor oral smell',
            'bleeding gums red gums swollen gums painful mouth',
            'tartar buildup plaque dental calculus tooth loss',
            'difficulty eating chewing problems mouth pain'
        ],
        'veterinary_cardiology': [
            'breathing difficulty labored breathing rapid breathing',
            'coughing persistent cough heart cough exercise intolerance',
            'weakness fainting collapse syncope tired easily',
            'heart murmur irregular heartbeat arrhythmia',
            'fluid retention swelling abdomen ascites edema'
        ],
        'veterinary_ophthalmology': [
            'eye problem vision loss blind cloudy eyes',
            'eye discharge watery eyes red eyes conjunctivitis',
            'squinting eye pain photophobia light sensitivity',
            'eye injury corneal ulcer eye infection',
            'cataract glaucoma retinal disease eye cloudiness'
        ]
    }
    
    SEVERITY_INDICATORS = {
        'severe': ['severe', 'extreme', 'unbearable', 'emergency', 'critical', 'acute',
                  'intense', 'excruciating', 'life-threatening', 'urgent', 'sudden', 'sharp'],
        'moderate': ['moderate', 'persistent', 'recurring', 'chronic', 'ongoing',
                    'frequent', 'regular', 'continuous', 'constant', 'steady'],
        'mild': ['mild', 'slight', 'minor', 'occasional', 'intermittent', 'light', 'little']
    }
    
    def initialize_ml_model(self):
        """Initialize TF-IDF vectorizer and train on specialty data"""
        # Prepare training data
        all_texts = []
        specialty_labels = []
        
        # Use human specialties by default (will be overridden for pets)
        for specialty, texts in self.HUMAN_SPECIALTY_TRAINING.items():
            for text in texts:
                all_texts.append(text)
                specialty_labels.append(specialty)
        
        # Initialize and fit TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True,
            min_df=1
        )
        
        # Fit and transform training data
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate average vector for each specialty
        self.specialty_vectors = {}
        self.specialty_names = list(self.HUMAN_SPECIALTY_TRAINING.keys())
        
        for specialty in self.specialty_names:
            indices = [i for i, label in enumerate(specialty_labels) if label == specialty]
            specialty_matrix = tfidf_matrix[indices]
            # Convert to numpy array to avoid matrix issues
            avg_vector = np.asarray(specialty_matrix.mean(axis=0)).flatten()
            self.specialty_vectors[specialty] = avg_vector
    
    def analyze_symptoms(self, symptoms: str, patient_type: str = 'human') -> Dict:
        """
        Fast ML-based symptom analysis using TF-IDF and cosine similarity
        
        Args:
            symptoms: String of symptoms
            patient_type: 'human' or 'pet'
            
        Returns:
            Dict with specialties, confidence scores, and recommendations
        """
        # Reinitialize for pet if needed
        if patient_type == 'pet':
            self._initialize_vet_model()
        
        # Preprocess symptoms
        symptoms_clean = self._preprocess_text(symptoms)
        
        # Transform symptoms to TF-IDF vector
        symptom_vector = self.vectorizer.transform([symptoms_clean])
        # Convert to dense numpy array and ensure 2D shape
        symptom_array = symptom_vector.toarray()
        
        # Calculate cosine similarity with each specialty
        specialty_scores = {}
        for specialty, spec_vector in self.specialty_vectors.items():
            # Ensure spec_vector is 2D array for cosine_similarity
            spec_array = np.asarray(spec_vector).reshape(1, -1)
            similarity = cosine_similarity(symptom_array, spec_array)[0][0]
            if similarity > 0.05:  # Threshold to filter noise
                specialty_scores[specialty] = float(similarity)
        
        # Sort by similarity score
        sorted_specialties = sorted(
            specialty_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Normalize scores to 0-1 range
        if sorted_specialties:
            max_score = sorted_specialties[0][1]
            confidence_scores = {
                spec: round(score / max_score, 2) if max_score > 0 else 0
                for spec, score in sorted_specialties[:3]
            }
        else:
            confidence_scores = {}
        
        # Extract severity
        severity = self.extract_severity(symptoms)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sorted_specialties[:3],
            severity,
            patient_type
        )
        
        # Extract matched keywords (for transparency)
        matched_keywords = self._extract_matched_keywords(
            symptoms_clean,
            [s[0] for s in sorted_specialties[:3]],
            patient_type
        )
        
        return {
            'patient_type': patient_type,
            'symptoms': symptoms,
            'recommended_specialties': [s[0] for s in sorted_specialties[:3]],
            'confidence_scores': confidence_scores,
            'matched_keywords': matched_keywords,
            'severity': severity,
            'recommendations': recommendations,
            'urgency': self._determine_urgency(severity, sorted_specialties),
            'ml_method': 'tfidf_cosine_similarity'
        }
    
    def _initialize_vet_model(self):
        """Initialize model for veterinary specialties"""
        all_texts = []
        specialty_labels = []
        
        for specialty, texts in self.VET_SPECIALTY_TRAINING.items():
            for text in texts:
                all_texts.append(text)
                specialty_labels.append(specialty)
        
        # Refit vectorizer for vet data
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True,
            min_df=1
        )
        
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate average vectors
        self.specialty_vectors = {}
        self.specialty_names = list(self.VET_SPECIALTY_TRAINING.keys())
        
        for specialty in self.specialty_names:
            indices = [i for i, label in enumerate(specialty_labels) if label == specialty]
            specialty_matrix = tfidf_matrix[indices]
            # Convert to numpy array to avoid matrix issues
            avg_vector = np.asarray(specialty_matrix.mean(axis=0)).flatten()
            self.specialty_vectors[specialty] = avg_vector
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_matched_keywords(
        self,
        symptoms: str,
        specialties: List[str],
        patient_type: str
    ) -> Dict:
        """Extract keywords that matched for transparency"""
        training_data = (
            self.HUMAN_SPECIALTY_TRAINING if patient_type == 'human'
            else self.VET_SPECIALTY_TRAINING
        )
        
        matched = {}
        symptom_words = set(symptoms.lower().split())
        
        for specialty in specialties:
            if specialty in training_data:
                spec_text = ' '.join(training_data[specialty])
                spec_words = set(spec_text.lower().split())
                common = symptom_words.intersection(spec_words)
                if common:
                    matched[specialty] = list(common)[:5]  # Top 5 matches
        
        return matched
    
    def extract_severity(self, symptoms: str) -> str:
        """Extract severity level from symptom description"""
        symptoms_lower = symptoms.lower()
        
        for level, keywords in self.SEVERITY_INDICATORS.items():
            if any(keyword in symptoms_lower for keyword in keywords):
                return level
        
        return 'moderate'
    
    def _generate_recommendations(
        self,
        top_specialties: List[Tuple[str, float]],
        severity: str,
        patient_type: str
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not top_specialties:
            recommendations.append("Consider consulting a general practitioner for initial assessment")
            return recommendations
        
        # Severity-based recommendations
        if severity == 'severe':
            recommendations.append("⚠️ Seek immediate medical attention")
            recommendations.append("Consider visiting emergency services if symptoms worsen")
        elif severity == 'moderate':
            recommendations.append("Schedule an appointment with a specialist soon")
            recommendations.append("Monitor symptoms and seek immediate care if they worsen")
        else:
            recommendations.append("Schedule a routine consultation")
            recommendations.append("Keep track of symptom progression")
        
        # Specialty-specific advice
        specialty_advice = {
            'cardiology': "Avoid strenuous activities until consultation",
            'dermatology': "Avoid scratching affected areas",
            'gastroenterology': "Maintain a food diary to identify triggers",
            'orthopedics': "Rest the affected area and apply ice if swollen",
            'neurology': "Keep a symptom diary with dates and times",
            'pulmonology': "Avoid smoke and pollutants",
            'veterinary_general': "Monitor eating and drinking habits",
            'veterinary_surgery': "Keep the animal calm and restrict movement",
        }
        
        top_specialty = top_specialties[0][0]
        if top_specialty in specialty_advice:
            recommendations.append(specialty_advice[top_specialty])
        
        return recommendations
    
    def _determine_urgency(
        self,
        severity: str,
        specialties: List[Tuple[str, float]]
    ) -> str:
        """Determine urgency level"""
        if severity == 'severe':
            return 'immediate'
        elif severity == 'moderate':
            return 'within_week'
        else:
            return 'routine'
    
    def match_doctors_to_symptoms(
        self,
        symptoms: str,
        patient_type: str,
        available_doctors: List[Dict]
    ) -> List[Dict]:
        """
        Match and rank doctors using ML similarity scores
        """
        analysis = self.analyze_symptoms(symptoms, patient_type)
        recommended_specs = analysis['recommended_specialties']
        confidence_scores = analysis['confidence_scores']
        
        doctor_scores = []
        for doctor in available_doctors:
            doc_spec = doctor.get('specialization', '').lower()
            
            # Calculate match score using ML confidence
            match_score = 0
            for i, rec_spec in enumerate(recommended_specs):
                if rec_spec in doc_spec or doc_spec in rec_spec:
                    match_score = confidence_scores.get(rec_spec, 0) * (3 - i)
                    break
            
            if match_score > 0:
                doctor['match_score'] = round(match_score, 2)
                doctor['match_reason'] = f"Specializes in {doc_spec}"
                doctor_scores.append(doctor)
        
        # Sort by match score, rating, distance
        doctor_scores.sort(
            key=lambda x: (
                -x.get('match_score', 0),
                -x.get('rating', 0),
                x.get('distance', 999)
            )
        )
        
        return doctor_scores
