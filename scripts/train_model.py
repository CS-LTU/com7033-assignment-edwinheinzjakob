import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(PROJECT_ROOT, 'app', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'stroke_model.joblib')

data_path = os.path.join(PROJECT_ROOT, 'data', 'healthcare-dataset-stroke-data.csv')
df = pd.read_csv(data_path)

df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')

print("Missing values in each column:")
print(df.isnull().sum())
print(f"\nTotal samples: {len(df)}")

feature_cols = ['gender', 'age', 'hypertension', 'heart_disease', 'work_type', 'bmi', 'smoking_status']
target_col = 'stroke'

X = df[feature_cols].copy()
y = df[target_col].astype(int)

categorical_features = ['gender', 'work_type', 'smoking_status']
numeric_features = ['age', 'bmi', 'hypertension', 'heart_disease']

numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),  
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(transformers=[
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features),
])

clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)

pipeline = ImbPipeline(steps=[
    ('preprocessor', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('clf', clf)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42, test_size=0.2
)

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

print("\n" + "="*50)
print("MODEL EVALUATION")
print("="*50)
print("ROC AUC:", roc_auc_score(y_test, y_proba))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

joblib.dump(pipeline, MODEL_PATH)
print(f"\nSaved model to {MODEL_PATH}")