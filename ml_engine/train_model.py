import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib

def train():
    print("=== Training EduRisk ML Engine ===")
    
    # 1. Load Dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset', 'student_performance.csv')
    df = pd.read_csv(dataset_path)
    
    X = df[['attendance', 'midterm', 'assignment', 'quiz', 'study_hours', 'backlogs']]
    y = df['risk_level']
    
    # 2. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Scale Features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train_scaled, y_train)
    
    # 5. Evaluate Model
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    # 6. Save Model Artifacts
    model_path = os.path.join(os.path.dirname(__file__), 'model.joblib')
    scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"Successfully saved model to: {model_path}")
    print(f"Successfully saved scaler to: {scaler_path}")

if __name__ == '__main__':
    train()