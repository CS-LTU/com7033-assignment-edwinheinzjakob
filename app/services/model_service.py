import os
import joblib
import pandas as pd
import numpy as np

class ModelService:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'stroke_model.joblib')
        self.model = joblib.load(model_path)
    
    def predict_proba(self, data):
        try:
            age = float(data.get('age', 0))
            hypertension = int(data.get('hypertension', 0))
            heart_disease = int(data.get('heart_disease', 0))
            bmi = float(data.get('bmi', 0))
            
            gender = str(data.get('gender', 'Male')).strip()
            work_type = str(data.get('work_type', 'Private')).strip()
            smoking_status = str(data.get('smoking_status', 'never')).strip()
            
            smoking_lower = smoking_status.lower()
            if 'never' in smoking_lower:
                smoking_status = 'never smoked'
            elif 'former' in smoking_lower:
                smoking_status = 'formerly smoked'
            elif 'smoke' in smoking_lower and 'former' not in smoking_lower:
                smoking_status = 'smokes'
            else:
                smoking_status = 'never smoked'   
            
            df = pd.DataFrame([{
                'gender': gender,
                'age': age,
                'hypertension': hypertension,
                'heart_disease': heart_disease,
                'work_type': work_type,
                'bmi': bmi,
                'smoking_status': smoking_status
            }])
            
            print(f"Input DataFrame:\n{df}")
            print(f"Columns: {df.columns.tolist()}")

            pred_prob = self.model.predict_proba(df)[0][1]
            prediction = int(pred_prob >= 0.5)
            
            return {'prediction': prediction, 'probability': pred_prob}
            
        except Exception as e:
            raise ValueError(f"Error processing input for prediction: {e}")

model_service = ModelService()