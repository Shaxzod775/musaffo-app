"""
Delete Yakkasaray Industrial Zone Monitoring project
"""
from app.config.firebase import get_db

db = get_db()

def delete_yakkasaray_project():
    """Find and delete Yakkasaray project"""
    projects_ref = db.collection('projects')
    docs = projects_ref.stream()
    
    deleted_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        title = data.get('title', '')
        titleKey = data.get('titleKey', '')
        
        # Check if this is the Yakkasaray project
        if 'Yakkasaray' in title or 'yakka' in titleKey.lower():
            print(f"Found: {title} (ID: {doc.id})")
            print(f"  titleKey: {titleKey}")
            doc.reference.delete()
            print(f"✅ Deleted!")
            deleted_count += 1
    
    return deleted_count

if __name__ == "__main__":
    print("🔍 Searching for Yakkasaray project...")
    count = delete_yakkasaray_project()
    
    if count > 0:
        print(f"\n✨ Deleted {count} project(s)")
    else:
        print("\n⚠️  Project not found")
