"""
ML Model Inference Module for Resume Analyzer
Loads and uses trained ML model for job field prediction
"""

import pickle
import os
import numpy as np

# Check if sklearn is available (required for loading pickled models)
# Import all sklearn classes that might be needed during unpickling
try:
    import sklearn
    # Import all model types that might be in the pickled file
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Only print warning once - use a simple message
    import sys
    if not hasattr(sys, '_sklearn_warning_printed'):
        print("Note: scikit-learn not found. Using keyword-based prediction. Install with: pip install scikit-learn")
        sys._sklearn_warning_printed = True

class JobFieldPredictor:
    """Class to handle ML model predictions for job field classification"""
    
    def __init__(self, model_dir='./models'):
        """
        Initialize the predictor with trained model and vectorizer
        
        Parameters:
        - model_dir: Directory containing saved model files
        """
        self.model_dir = model_dir
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load trained model and vectorizer from disk"""
        # Check if sklearn is available first
        if not SKLEARN_AVAILABLE:
            # Warning already printed at module level, just set status
            self.is_loaded = False
            return
        
        model_path = os.path.join(self.model_dir, 'job_field_classifier.pkl')
        vectorizer_path = os.path.join(self.model_dir, 'tfidf_vectorizer.pkl')
        
        try:
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                # Load model - sklearn classes must be imported before pickle.load()
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                self.is_loaded = True
                print(f"ML Model loaded successfully from {self.model_dir}")
            else:
                print(f"Warning: Model files not found in {self.model_dir}")
                print("   Using fallback keyword-based prediction")
                self.is_loaded = False
        except (ImportError, ModuleNotFoundError) as e:
            error_msg = str(e)
            if 'numpy' in error_msg.lower() or '_core' in error_msg.lower():
                print(f"Error loading model: NumPy version incompatibility detected")
                print(f"   The model requires a different NumPy version. Using fallback prediction.")
                print(f"   To fix: pip install --upgrade numpy (restart Streamlit after)")
            elif 'sklearn' in error_msg.lower() or 'scikit' in error_msg.lower():
                print(f"Error loading model: sklearn module required but not installed")
                print(f"   Details: {error_msg}")
                print("   Install with: pip install scikit-learn")
            else:
                print(f"Error loading model: Missing module - {error_msg}")
            print("   Using fallback keyword-based prediction")
            self.is_loaded = False
        except Exception as e:
            error_msg = str(e)
            if 'numpy' in error_msg.lower() or '_core' in error_msg.lower():
                print(f"Error loading model: NumPy version incompatibility")
                print(f"   Details: {error_msg}")
                print("   The model was trained with a different NumPy version.")
                print("   Using fallback keyword-based prediction (this works fine!)")
            elif 'sklearn' in error_msg.lower() or 'scikit' in error_msg.lower():
                print(f"Error loading model: {error_msg}")
                print("   Install scikit-learn with: pip install scikit-learn")
            else:
                print(f"Error loading model: {error_msg}")
            print("   Using fallback keyword-based prediction")
            self.is_loaded = False
    
    def predict_job_field(self, resume_text, skills_list=None):
        """
        Predict job field from resume text and skills
        
        Parameters:
        - resume_text: Full text content of the resume
        - skills_list: List of skills extracted from resume (optional)
        
        Returns:
        - predicted_field: Predicted job field
        - confidence: Prediction confidence score
        - probabilities: Dictionary of probabilities for each field
        """
        if not self.is_loaded:
            return None, 0.0, {}
        
        try:
            # Combine resume text and skills for better prediction
            if skills_list:
                skills_text = ' '.join(skills_list) if isinstance(skills_list, list) else str(skills_list)
                combined_text = f"{resume_text} {skills_text}"
            else:
                combined_text = resume_text
            
            # Vectorize input
            text_vector = self.vectorizer.transform([combined_text])
            
            # Predict
            prediction = self.model.predict(text_vector)[0]
            
            # Get probabilities
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(text_vector)[0]
                classes = self.model.classes_
                prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
                confidence = float(max(probabilities))
            else:
                prob_dict = {prediction: 1.0}
                confidence = 1.0
            
            return prediction, confidence, prob_dict
            
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, 0.0, {}
    
    def get_recommended_skills(self, predicted_field):
        """
        Get recommended skills based on predicted job field
        (Same as keyword-based approach but triggered by ML prediction)
        """
        skill_recommendations = {
            'Data Science': [
                'Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                'Data Mining', 'Clustering & Classification', 'Data Analytics',
                'Quantitative Analysis', 'Web Scraping', 'ML Algorithms',
                'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow',
                'Flask', 'Streamlit'
            ],
            'Web Development': [
                'React', 'Django', 'Node JS', 'React JS', 'php', 'laravel',
                'Magento', 'wordpress', 'Javascript', 'Angular JS', 'c#',
                'Flask', 'SDK'
            ],
            'Android Development': [
                'Android', 'Android development', 'Flutter', 'Kotlin', 'XML',
                'Java', 'Kivy', 'GIT', 'SDK', 'SQLite'
            ],
            'IOS Development': [
                'IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch',
                'Xcode', 'Objective-C', 'SQLite', 'Plist', 'StoreKit',
                'UI-Kit', 'AV Foundation', 'Auto-Layout'
            ],
            'UI-UX Development': [
                'UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin',
                'Balsamiq', 'Prototyping', 'Wireframes', 'Storyframes',
                'Adobe Photoshop', 'Editing', 'Illustrator', 'After Effects',
                'Premier Pro', 'Indesign', 'Wireframe', 'Solid', 'Grasp',
                'User Research'
            ],
            'NA': ['No Recommendations']
        }
        
        return skill_recommendations.get(predicted_field, ['No Recommendations'])
