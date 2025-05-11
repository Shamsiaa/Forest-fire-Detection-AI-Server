from firebase_admin import initialize_app, credentials
from firebase_admin import firestore, storage
import os

# Initialize Firebase
cred = credentials.Certificate("firebase/serviceAccountKey.json")
firebase_app = initialize_app(cred, {
    'storageBucket': 'forestfire-47ced.firebasestorage.app'
})

db = firestore.client()
bucket = storage.bucket()