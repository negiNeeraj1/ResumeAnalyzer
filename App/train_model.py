"""
ML Model Training Script for Resume Analyzer
Trains a job field classification model using resume text data
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Job field categories
JOB_FIELDS = ['Data Science', 'Web Development', 'Android Development', 
              'IOS Development', 'UI-UX Development', 'NA']

def create_sample_data():
    """
    Creates sample training data based on keyword patterns.
    In production, replace this with your actual resume dataset.
    """
    training_data = []
    
    # Data Science samples
    ds_samples = [
        "python machine learning deep learning tensorflow keras pytorch data science analytics",
        "statistical modeling predictive analysis clustering classification scikit-learn",
        "neural networks artificial intelligence computer vision natural language processing",
        "data mining big data hadoop spark sql pandas numpy matplotlib",
        "flask streamlit data visualization tableau power bi jupyter notebook"
    ]
    for text in ds_samples:
        training_data.append({'resume_text': text, 'job_field': 'Data Science'})
    
    # Web Development samples
    web_samples = [
        "react javascript html css node.js express django flask php laravel",
        "frontend backend full stack web development angular vue.js",
        "rest api graphql mongodb mysql postgresql firebase",
        "responsive design bootstrap tailwind css git github",
        "wordpress magento e-commerce shopify woocommerce"
    ]
    for text in web_samples:
        training_data.append({'resume_text': text, 'job_field': 'Web Development'})
    
    # Android Development samples
    android_samples = [
        "android development java kotlin xml android studio gradle",
        "mobile app development flutter dart firebase android sdk",
        "material design recyclerview retrofit room database",
        "mvp architecture rxjava coroutines jetpack components",
        "google play store app publishing apk deployment"
    ]
    for text in android_samples:
        training_data.append({'resume_text': text, 'job_field': 'Android Development'})
    
    # iOS Development samples
    ios_samples = [
        "ios development swift objective-c xcode cocoa touch",
        "ios app development uikit swiftui core data",
        "app store deployment testflight cocoapods spm",
        "autolayout storyboard programmatic ui mvvm architecture",
        "core animation avfoundation storekit in-app purchases"
    ]
    for text in ios_samples:
        training_data.append({'resume_text': text, 'job_field': 'IOS Development'})
    
    # UI-UX Development samples
    uiux_samples = [
        "ui ux design figma adobe xd prototyping wireframes",
        "user experience design user research usability testing",
        "adobe photoshop illustrator indesign after effects",
        "interaction design visual design design systems",
        "sketch zeplin balsamiq invision user interface design"
    ]
    for text in uiux_samples:
        training_data.append({'resume_text': text, 'job_field': 'UI-UX Development'})
    
    # NA samples (general/non-technical)
    na_samples = [
        "english communication writing microsoft office leadership",
        "customer service sales marketing business administration",
        "project management team collaboration presentation skills",
        "social media content writing digital marketing"
    ]
    for text in na_samples:
        training_data.append({'resume_text': text, 'job_field': 'NA'})
    
    return pd.DataFrame(training_data)

def load_training_data(csv_path=None):
    """
    Load training data from CSV file or create sample data.
    
    CSV format should have columns: 'resume_text' and 'job_field'
    """
    if csv_path and os.path.exists(csv_path):
        print(f"Loading training data from {csv_path}")
        df = pd.read_csv(csv_path)
        return df
    else:
        print("No CSV file found. Creating sample training data...")
        print("Tip: Create a CSV file with 'resume_text' and 'job_field' columns for better results")
        return create_sample_data()

def train_job_field_classifier(df, model_type='random_forest'):
    """
    Train a job field classification model.
    
    Parameters:
    - df: DataFrame with 'resume_text' and 'job_field' columns
    - model_type: 'random_forest', 'svm', or 'naive_bayes'
    
    Returns:
    - Trained model and vectorizer
    """
    print(f"\n{'='*60}")
    print(f"Training {model_type.upper()} Model for Job Field Classification")
    print(f"{'='*60}\n")
    
    # Prepare data
    X = df['resume_text'].values
    y = df['job_field'].values
    
    print(f"Total samples: {len(X)}")
    print(f"Job fields: {set(y)}")
    print(f"\nClass distribution:")
    # Convert to Series for value_counts
    y_series = pd.Series(y)
    print(y_series.value_counts())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Vectorize text
    print("\nVectorizing text data...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
        lowercase=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train model
    print(f"\nTraining {model_type} classifier...")
    
    if model_type == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'svm':
        model = SVC(kernel='linear', probability=True, random_state=42)
    elif model_type == 'naive_bayes':
        model = MultinomialNB(alpha=0.1)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.fit(X_train_vec, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return model, vectorizer

def save_model(model, vectorizer, model_dir='./models'):
    """Save trained model and vectorizer"""
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'job_field_classifier.pkl')
    vectorizer_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nModel saved to: {model_path}")
    
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"Vectorizer saved to: {vectorizer_path}")
    
    return model_path, vectorizer_path

def main():
    """Main training function"""
    print("Starting ML Model Training for Resume Analyzer\n")
    
    # Load or create training data
    # Option 1: Use your own CSV file
    # df = load_training_data('training_data.csv')
    
    # Option 2: Use sample data (for testing)
    df = load_training_data()
    
    # Train model (try different models)
    model_types = ['random_forest', 'svm', 'naive_bayes']
    best_model = None
    best_vectorizer = None
    best_accuracy = 0
    best_type = None
    
    for model_type in model_types:
        try:
            model, vectorizer = train_job_field_classifier(df, model_type)
            
            # Quick evaluation on full dataset
            X = df['resume_text'].values
            X_vec = vectorizer.transform(X)
            y_pred = model.predict(X_vec)
            accuracy = accuracy_score(df['job_field'].values, y_pred)
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = model
                best_vectorizer = vectorizer
                best_type = model_type
        except Exception as e:
            print(f"Error training {model_type}: {e}")
            continue
    
    if best_model is not None:
        print(f"\nBest model: {best_type} with {best_accuracy:.2%} accuracy")
        save_model(best_model, best_vectorizer)
        print("\nTraining completed successfully!")
        print("\nNext steps:")
        print("   1. Use the trained model in App.py")
        print("   2. Collect more resume data to improve accuracy")
        print("   3. Retrain periodically with new data")
    else:
        print("\nTraining failed!")

if __name__ == "__main__":
    main()
