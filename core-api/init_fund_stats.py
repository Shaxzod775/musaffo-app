"""
Script to initialize fund stats in Firestore
Run once to add initial fund amount
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin
cred = credentials.Certificate('musaffo-33cf5-firebase-adminsdk-fbsvc-9215754308.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Add fund stats
fund_stats = {
    'totalDonations': 1400000000,  # 1.4 billion
    'totalDonors': 15234,
    'totalProjects': 12,
    'activeProjects': 5,
    'lastUpdated': datetime.now()
}

# Create or update stats document
db.collection('fund_stats').document('current').set(fund_stats)

print(f"✅ Fund stats initialized:")
print(f"   Total Donations: {fund_stats['totalDonations']:,} сум")
print(f"   Total Donors: {fund_stats['totalDonors']:,}")
print(f"   Total Projects: {fund_stats['totalProjects']}")
print(f"   Active Projects: {fund_stats['activeProjects']}")
