# 🤖 Model Usage Documentation

## Overview

This document explains **what models are used** in the Resume Analyzer project and **where they are used** in the application workflow.

---

## 📊 Models Used in This Project

### 1. **SVM (Support Vector Machine) Classifier** ⭐ PRIMARY MODEL
- **Type**: Supervised Machine Learning - Classification Model
- **Algorithm**: Support Vector Machine with Linear Kernel
- **Purpose**: Job Field Prediction (Multi-class Classification)
- **Location**: `./models/job_field_classifier.pkl`
- **Training Script**: `train_model.py`
- **Status**: ✅ Currently Active (89.66% accuracy on training data)

**Model Details:**
- **Input**: Resume text + Skills (combined text)
- **Output**: Predicted Job Field + Confidence Score
- **Classes**: 6 job fields
  - Data Science
  - Web Development
  - Android Development
  - IOS Development
  - UI-UX Development
  - NA (General/Other)

### 2. **TF-IDF Vectorizer** 📝 TEXT PROCESSING
- **Type**: Feature Extraction (Text Vectorization)
- **Purpose**: Converts resume text into numerical features
- **Location**: `./models/tfidf_vectorizer.pkl`
- **Parameters**:
  - Max Features: 5000
  - N-gram Range: (1, 2) - Single words and 2-word phrases
  - Stop Words: English (removed)
  - Lowercase: True

### 3. **Pre-trained NLP Models** (via pyresparser)
- **spaCy's `en_core_web_sm`**: Pre-trained English language model
  - Used for: Named Entity Recognition (NER), Part-of-Speech tagging
  - Purpose: Extract name, email, skills, degree from resume
- **Custom spaCy Model**: Custom entity extraction model
  - Used for: Resume-specific entity extraction

### 4. **Fallback: Keyword-Based System** (Rule-Based)
- **Type**: Rule-based pattern matching
- **Purpose**: Backup prediction when ML model unavailable
- **Method**: Simple keyword matching against predefined lists

---

## 🔄 Where Models Are Used in the Project

### **Use Case Flow Diagram**

```
User Uploads Resume PDF
         ↓
[PDF Parsing] - pdfminer3, pyresparser
         ↓
[Text Extraction] - Extract full resume text
         ↓
[Basic Info Extraction] - spaCy NLP models
    - Name, Email, Phone
    - Skills, Degree
         ↓
[Job Field Prediction] ⭐ ML MODEL USED HERE
    ├─→ ML Model Available? 
    │   ├─ YES → Use SVM Classifier
    │   │   ├─ TF-IDF Vectorization
    │   │   ├─ SVM Prediction
    │   │   ├─ Confidence Score
    │   │   └─ Top 3 Probabilities
    │   │
    │   └─ NO → Use Keyword Matching (Fallback)
    │
    └─→ Output: Predicted Job Field
         ↓
[Skill Recommendations] - Based on predicted field
         ↓
[Course Recommendations] - Based on predicted field
         ↓
[Resume Scoring] - Rule-based scoring system
         ↓
[Store Results] - MySQL Database
```

---

## 📍 Specific Code Locations

### 1. **Model Loading** (App.py lines 36-43)

```python
# ML Model for job field prediction
try:
    from ml_model import JobFieldPredictor
    ml_predictor = JobFieldPredictor()  # Loads model here
    ML_MODEL_AVAILABLE = ml_predictor.is_loaded
except Exception as e:
    print(f"ML Model not available: {e}")
    ML_MODEL_AVAILABLE = False
    ml_predictor = None
```

**What happens:**
- Attempts to load SVM classifier from `./models/job_field_classifier.pkl`
- Attempts to load TF-IDF vectorizer from `./models/tfidf_vectorizer.pkl`
- Sets `ML_MODEL_AVAILABLE` flag based on success

### 2. **Model Prediction** (App.py lines 397-450)

```python
# Try ML Model Prediction First (if available)
if ML_MODEL_AVAILABLE and ml_predictor:
    try:
        # ⭐ ML MODEL PREDICTION HAPPENS HERE
        reco_field, prediction_confidence, probabilities = ml_predictor.predict_job_field(
            resume_text, resume_data['skills']
        )
        
        if reco_field:
            # Get recommended skills
            recommended_skills = ml_predictor.get_recommended_skills(reco_field)
            
            # Display prediction with confidence
            confidence_percent = prediction_confidence * 100
            st.success(f"ML Model Prediction: {display_name} (Confidence: {confidence_percent:.1f}%)")
            
            # Show top probabilities
            if probabilities and len(probabilities) > 1:
                sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
                prob_text = ", ".join([f"{field}: {prob*100:.1f}%" for field, prob in sorted_probs])
                st.info(f"Top Predictions: {prob_text}")
```

**What happens:**
1. **Input**: Full resume text + extracted skills list
2. **Text Processing**: Combined into single text string
3. **Vectorization**: TF-IDF vectorizer converts text to numerical features
4. **Prediction**: SVM classifier predicts job field
5. **Output**: 
   - Predicted field (e.g., "Data Science")
   - Confidence score (0-100%)
   - Probability distribution for all fields

### 3. **Fallback System** (App.py lines 452-520)

```python
# Fallback to Keyword-Based Prediction if ML model not available or failed
if not reco_field:
    # Keyword matching logic...
    for i in resume_data['skills']:
        if i.lower() in ds_keyword:
            reco_field = 'Data Science'
            # ... etc
```

**What happens:**
- If ML model fails or not available
- Uses simple keyword matching
- Checks if skills match predefined keyword lists
- Less accurate but always works

---

## 🎯 Use Case Scenarios

### **Scenario 1: ML Model Available** ✅

**User Flow:**
1. User uploads resume PDF
2. System extracts text and skills using pyresparser + spaCy
3. **ML Model Prediction:**
   - Text → TF-IDF Vectorization
   - Vector → SVM Classifier
   - Output: "Data Science" with 85% confidence
4. System shows:
   - "🎯 ML Model Prediction: You are looking for Data Science Jobs (Confidence: 85.0%)"
   - "Top Predictions: Data Science: 85.0%, Web Development: 10.0%, Android Development: 5.0%"
5. Recommends Data Science skills and courses
6. Stores prediction in database

### **Scenario 2: ML Model Not Available** ⚠️

**User Flow:**
1. User uploads resume PDF
2. System extracts text and skills
3. **Keyword Matching (Fallback):**
   - Checks if "tensorflow" in skills → Yes
   - Matches to "Data Science" keyword list
   - Sets `reco_field = 'Data Science'`
4. System shows:
   - "🎯 Our analysis says you are looking for Data Science Jobs."
   - (No confidence score shown)
5. Recommends Data Science skills and courses
6. Stores prediction in database

---

## 🔧 Model Architecture

### **SVM Classifier Architecture**

```
Input: Resume Text + Skills
         ↓
[Text Preprocessing]
  - Lowercase
  - Remove stopwords
         ↓
[TF-IDF Vectorization]
  - Max 5000 features
  - 1-gram and 2-gram
  - Output: 5000-dimensional vector
         ↓
[SVM Classifier]
  - Kernel: Linear
  - Probability: True (for confidence scores)
  - Output: Class label + Probabilities
         ↓
Output: Job Field + Confidence + All Probabilities
```

### **Training Process** (train_model.py)

1. **Data Collection**: Sample training data (29 samples)
2. **Data Split**: 80% train, 20% test
3. **Feature Engineering**: TF-IDF vectorization
4. **Model Training**: 
   - Tests 3 models: Random Forest, SVM, Naive Bayes
   - Selects best performing (SVM won with 89.66% accuracy)
5. **Model Saving**: Pickle files saved to `./models/`

---

## 📊 Model Performance

### **Current Model Metrics**

- **Model Type**: SVM (Support Vector Machine)
- **Training Accuracy**: 89.66%
- **Test Accuracy**: 50% (on small test set of 6 samples)
- **Classes**: 6 job fields
- **Features**: 5000 TF-IDF features

### **Model Limitations**

1. **Small Training Data**: Only 29 samples (needs more for better accuracy)
2. **Test Set Too Small**: Only 6 samples for testing
3. **Limited Generalization**: May not work well on resumes with unusual formats
4. **No Retraining**: Model doesn't auto-retrain with new data

---

## 🚀 How to Improve Model Usage

### **1. Collect More Training Data**

```python
# Extract from your database
python extract_training_data.py

# This creates training_data.csv with real resume data
```

### **2. Retrain with More Data**

```python
# Update train_model.py to use your CSV
df = load_training_data('training_data.csv')

# Retrain
python train_model.py
```

### **3. Add More Job Fields**

Edit `train_model.py`:
```python
JOB_FIELDS = [
    'Data Science', 
    'Web Development',
    'DevOps',           # Add new field
    'Cybersecurity',    # Add new field
    # ... etc
]
```

---

## 📝 Summary

### **What Model is Used?**
- **Primary**: SVM (Support Vector Machine) Classifier
- **Supporting**: TF-IDF Vectorizer for text processing
- **NLP**: spaCy models for text extraction
- **Fallback**: Keyword-based rule system

### **Where is it Used?**
1. **Model Loading**: App startup (App.py lines 36-43)
2. **Prediction**: During resume analysis (App.py lines 397-450)
3. **Fallback**: If ML model unavailable (App.py lines 452-520)
4. **Storage**: Predictions saved to MySQL database

### **Use Case**
- **Primary Purpose**: Predict job field from resume text
- **Input**: Resume PDF → Extracted text + skills
- **Output**: Job field prediction + confidence score
- **Application**: Resume analysis, skill recommendations, course suggestions

---

**Last Updated**: After ML model integration
**Model Status**: ✅ Active and Working
**Model Location**: `./App/models/job_field_classifier.pkl`




