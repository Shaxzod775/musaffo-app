"""
Seed script to populate Firestore with initial projects
"""
from app.config.firebase import get_db
from datetime import datetime

db = get_db()

# Project data matching the frontend structure
PROJECTS = [
    {
        "title": "Green Belt",
        "description": "Planting 1000 plane trees to protect Sergeli from dust.",
        "titleKey": "project_greenbelt_title",
        "descKey": "project_greenbelt_desc",
        "targetAmount": 500000000,  # 500M
        "currentAmount": 325000000,  # 325M (65%)
        "status": "active",
        "image": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&q=80&w=800",
        "votesFor": 0,
        "votesAgainst": 0
    },
    {
        "title": "Yakkasaray Industrial Zone Monitoring",
        "description": "Installation of 25 IoT sensors to control factory emissions.",
        "titleKey": "project_yakka_title",
        "descKey": "project_yakka_desc",
        "targetAmount": 180000000,  # 180M
        "currentAmount": 95400000,   # 95.4M (53%)
        "status": "active",
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&q=80&w=800",
        "votesFor": 0,
        "votesAgainst": 0
    },
    {
        "title": "Yunusabad Bike Lanes",
        "description": "Construction of 5km bike lanes to reduce emissions.",
        "titleKey": "project_bike_title",
        "descKey": "project_bike_desc",
        "targetAmount": 350000000,  # 350M
        "currentAmount": 119000000,  # 119M (34%)
        "status": "active",
        "image": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&q=80&w=800",
        "votesFor": 0,
        "votesAgainst": 0
    },
    {
        "title": "Filters for Schools #34, #110",
        "description": "Installation of HEPA filters in classrooms.",
        "titleKey": "project_schools_title",
        "descKey": "project_schools_desc",
        "targetAmount": 120000000,  # 120M
        "currentAmount": 84000000,   # 84M (70%)
        "status": "active",
        "image": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?auto=format&fit=crop&q=80&w=800",
        "votesFor": 0,
        "votesAgainst": 0
    },
    {
        "title": "Mirabad Greening",
        "description": "Planting 500 trees in Mirabad district. Completed in September 2025.",
        "titleKey": "project_mirabad_title",
        "descKey": "project_mirabad_desc",
        "targetAmount": 250000000,  # 250M
        "currentAmount": 250000000,  # 250M (100%)
        "status": "completed",
        "image": "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&q=80&w=800",
        "votesFor": 0,
        "votesAgainst": 0
    }
]

def seed_projects():
    """Add all projects to Firestore"""
    print("🌱 Starting to seed projects...")
    
    projects_ref = db.collection('projects')
    
    # Clear existing projects (optional - comment out if you want to keep existing data)
    # existing_docs = projects_ref.stream()
    # for doc in existing_docs:
    #     doc.reference.delete()
    #     print(f"Deleted existing project: {doc.id}")
    
    # Add new projects
    for project in PROJECTS:
        project_data = {
            **project,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        doc_ref = projects_ref.document()
        doc_ref.set(project_data)
        
        print(f"✅ Created project: {project['title']} (ID: {doc_ref.id})")
    
    print(f"\n🎉 Successfully seeded {len(PROJECTS)} projects!")

if __name__ == "__main__":
    seed_projects()
