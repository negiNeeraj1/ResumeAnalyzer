# 🤖 ML Model Integration Guide

This guide explains how to train and use a Machine Learning model for job field prediction in the Resume Analyzer.

## 📋 Overview

The ML model replaces the keyword-based prediction system with a trained classifier that can:
- Predict job fields more accurately
- Handle variations in resume text
- Provide confidence scores
- Learn from new data

## 🚀 Quick Start

### Step 1: Install ML Dependencies

```bash
pip install scikit-learn
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Train the Model

Run the training script:

```bash
cd App
python train_model.py
```

This will:
- Create sample training data (or use your CSV file)
- Train multiple models (Random Forest, SVM, Naive Bayes)
- Select the best performing model
- Save the model to `./models/` directory

### Step 3: Use the Trained Model

The model is automatically loaded when you run `App.py`. The system will:
- Use ML model if available
- Fall back to keyword matching if model not found

```bash
streamlit run App.py
```

## 📊 Training Your Own Model

### Option 1: Use Sample Data (Quick Start)

The training script includes sample data for testing. Just run:

```bash
python train_model.py
```

### Option 2: Use Your Own Data (Recommended)

1. **Create a CSV file** with your resume data:

```csv
resume_text,job_field
"python machine learning tensorflow data science analytics",Data Science
"react javascript html css web development",Web Development
"android java kotlin mobile development",Android Development
...
```

2. **Update `train_model.py`**:

```python
# In train_model.py, change:
df = load_training_data('your_data.csv')
```

3. **Train the model**:

```bash
python train_model.py
```

### Option 3: Collect Data from Your Database

You can extract training data from your MySQL database:

```python
import pandas as pd
import pymysql

# Connect to database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    db='cv'
)

# Query user data
query = """
SELECT 
    CONCAT(convert(Actual_skills using utf8), ' ', convert(Predicted_Field using utf8)) as resume_text,
    convert(Predicted_Field using utf8) as job_field
FROM user_data
WHERE Predicted_Field IS NOT NULL
"""

df = pd.read_sql(query, connection)
df.to_csv('training_data.csv', index=False)
```

## 🎯 Model Types

The training script tests three model types:

1. **Random Forest** (Default)
   - Good for general classification
   - Handles non-linear relationships
   - Fast training and prediction

2. **SVM (Support Vector Machine)**
   - Good for text classification
   - Works well with TF-IDF features
   - Can be slower for large datasets

3. **Naive Bayes**
   - Fast and efficient
   - Good baseline model
   - Works well with text data

The script automatically selects the best performing model.

## 📁 File Structure

```
App/
├── train_model.py          # Training script
├── ml_model.py             # Model inference module
├── App.py                  # Main application (updated)
├── models/                 # Saved models (created after training)
│   ├── job_field_classifier.pkl
│   └── tfidf_vectorizer.pkl
└── ML_MODEL_GUIDE.md       # This file
```

## 🔧 Customization

### Adjust Model Parameters

Edit `train_model.py`:

```python
# Random Forest parameters
model = RandomForestClassifier(
    n_estimators=200,      # More trees = better accuracy (slower)
    max_depth=30,          # Deeper trees = more complex
    random_state=42
)

# TF-IDF parameters
vectorizer = TfidfVectorizer(
    max_features=10000,    # More features = better (slower)
    ngram_range=(1, 3),    # Include 1-3 word phrases
    stop_words='english'
)
```

### Add More Job Fields

1. Update `JOB_FIELDS` in `train_model.py`:

```python
JOB_FIELDS = [
    'Data Science', 
    'Web Development', 
    'Android Development',
    'IOS Development', 
    'UI-UX Development',
    'DevOps',              # Add new field
    'Cybersecurity',       # Add new field
    'NA'
]
```

2. Add training samples for new fields
3. Update `get_recommended_skills()` in `ml_model.py`

## 📈 Improving Model Accuracy

1. **More Training Data**: Collect more resume samples
2. **Better Data Quality**: Ensure accurate labels
3. **Feature Engineering**: Add more features (skills count, experience years, etc.)
4. **Hyperparameter Tuning**: Use GridSearchCV for optimal parameters
5. **Ensemble Methods**: Combine multiple models

## 🔄 Retraining

Retrain periodically with new data:

```bash
# 1. Collect new data from database
# 2. Add to training CSV
# 3. Retrain
python train_model.py
```

## 🐛 Troubleshooting

### Model Not Loading

- Check if `./models/` directory exists
- Verify model files are present
- Check file permissions

### Low Accuracy

- Add more training data
- Check data quality and labels
- Try different model types
- Adjust hyperparameters

### Memory Issues

- Reduce `max_features` in TF-IDF
- Use smaller `n_estimators` for Random Forest
- Process data in batches

## 📝 Notes

- The model uses TF-IDF vectorization for text features
- Models are saved as pickle files
- The system gracefully falls back to keyword matching if ML model fails
- ML predictions show confidence scores to users

## 🎓 Next Steps

1. Collect real resume data from your database
2. Label the data accurately
3. Train with your dataset
4. Evaluate and improve
5. Deploy and monitor performance

---

**Need Help?** Check the code comments in `train_model.py` and `ml_model.py` for detailed explanations.
