import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
# Use FIREBASE_CREDENTIALS_PATH env variable (set in Dockerfile for Cloud Run)
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'musaffo-33cf5-firebase-adminsdk-fbsvc-9215754308.json')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

def get_db():
    """Get Firestore database instance"""
    return db
