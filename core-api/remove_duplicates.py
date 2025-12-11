"""
Script to check and remove duplicate projects from Firestore
"""
from app.config.firebase import get_db

db = get_db()

def check_duplicates():
    """Check for duplicate projects"""
    projects_ref = db.collection('projects')
    docs = projects_ref.stream()
    
    projects_by_title = {}
    duplicates = []
    
    for doc in docs:
        data = doc.to_dict()
        title = data.get('title', '')
        titleKey = data.get('titleKey', '')
        
        key = titleKey or title
        
        if key in projects_by_title:
            duplicates.append({
                'id': doc.id,
                'title': title,
                'titleKey': titleKey
            })
            print(f"⚠️  Duplicate found: {title} (ID: {doc.id})")
        else:
            projects_by_title[key] = {
                'id': doc.id,
                'title': title,
                'titleKey': titleKey
            }
    
    return duplicates

def delete_project(project_id):
    """Delete a project by ID"""
    db.collection('projects').document(project_id).delete()
    print(f"✅ Deleted project: {project_id}")

if __name__ == "__main__":
    print("🔍 Checking for duplicates...")
    duplicates = check_duplicates()
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate(s)")
        for dup in duplicates:
            print(f"Deleting: {dup['title']} (ID: {dup['id']})")
            delete_project(dup['id'])
        print("\n✨ Cleanup complete!")
    else:
        print("\n✅ No duplicates found!")
