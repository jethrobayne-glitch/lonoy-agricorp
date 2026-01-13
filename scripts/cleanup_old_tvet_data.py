#!/usr/bin/env python3
"""
Script to clean up old TVET data from generic inventory tables after migration
"""

import sys
import os

# Add the parent directory to Python path to import the web module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from web import create_app
from web.models import db, InventoryFolder, CoreCompetency, Category, InspectionRemark, InventoryMaterial

def cleanup_old_tvet_data():
    """Remove old TVET data from generic tables after successful migration"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧹 Starting cleanup of old TVET data from generic tables...")
            
            # First check what we have
            tvet_materials = InventoryMaterial.query.filter_by(department='TVET').all()
            tvet_folders = InventoryFolder.query.filter_by(department='TVET').all()
            tvet_competencies = CoreCompetency.query.filter_by(department='TVET').all()
            tvet_categories = Category.query.filter_by(department='TVET').all()
            tvet_remarks = InspectionRemark.query.filter_by(department='TVET').all()
            
            print(f"Found {len(tvet_materials)} TVET materials to remove")
            print(f"Found {len(tvet_folders)} TVET folders to remove")
            print(f"Found {len(tvet_competencies)} TVET competencies to remove")
            print(f"Found {len(tvet_categories)} TVET categories to remove")
            print(f"Found {len(tvet_remarks)} TVET remarks to remove")
            
            if not any([tvet_materials, tvet_folders, tvet_competencies, tvet_categories, tvet_remarks]):
                print("✅ No TVET data found in generic tables. Already clean!")
                return True
            
            # Confirm before deletion
            print(f"\n⚠️  This will permanently delete {len(tvet_materials) + len(tvet_folders) + len(tvet_competencies) + len(tvet_categories) + len(tvet_remarks)} records from generic tables.")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Cleanup cancelled.")
                return False
            
            # Remove TVET materials first (due to foreign key constraints)
            for material in tvet_materials:
                db.session.delete(material)
            print(f"✓ Removed {len(tvet_materials)} old TVET materials")
            
            # Remove TVET folders
            for folder in tvet_folders:
                db.session.delete(folder)
            print(f"✓ Removed {len(tvet_folders)} old TVET folders")
            
            # Remove TVET competencies
            for competency in tvet_competencies:
                db.session.delete(competency)
            print(f"✓ Removed {len(tvet_competencies)} old TVET competencies")
            
            # Remove TVET categories
            for category in tvet_categories:
                db.session.delete(category)
            print(f"✓ Removed {len(tvet_categories)} old TVET categories")
            
            # Remove TVET remarks
            for remark in tvet_remarks:
                db.session.delete(remark)
            print(f"✓ Removed {len(tvet_remarks)} old TVET remarks")
            
            db.session.commit()
            
            # Verify cleanup
            print("\n🔍 Verifying cleanup...")
            remaining_tvet = (
                InventoryMaterial.query.filter_by(department='TVET').count() +
                InventoryFolder.query.filter_by(department='TVET').count() +
                CoreCompetency.query.filter_by(department='TVET').count() +
                Category.query.filter_by(department='TVET').count() +
                InspectionRemark.query.filter_by(department='TVET').count()
            )
            
            if remaining_tvet == 0:
                print("✅ All TVET data successfully removed from generic tables!")
            else:
                print(f"⚠️  Warning: {remaining_tvet} TVET records still remain")
                
            # Show remaining data
            print(f"\n📊 Remaining data in generic tables:")
            print(f"Total Folders: {InventoryFolder.query.count()}")
            print(f"Total Competencies: {CoreCompetency.query.count()}")
            print(f"Total Categories: {Category.query.count()}")
            print(f"Total Remarks: {InspectionRemark.query.count()}")
            print(f"Total Materials: {InventoryMaterial.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during cleanup: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

def check_remaining_usage():
    """Check if generic inventory tables are still being used"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Checking remaining usage of generic inventory tables:")
        
        # Check what departments are still using generic tables
        folders = InventoryFolder.query.all()
        materials = InventoryMaterial.query.all()
        competencies = CoreCompetency.query.all()
        categories = Category.query.all()
        remarks = InspectionRemark.query.all()
        
        departments = set()
        for table, items in [
            ("Folders", folders),
            ("Materials", materials),
            ("Competencies", competencies),
            ("Categories", categories),
            ("Remarks", remarks)
        ]:
            if items:
                table_depts = set(item.department for item in items if hasattr(item, 'department'))
                departments.update(table_depts)
                print(f"{table}: {len(items)} records, departments: {table_depts}")
            else:
                print(f"{table}: 0 records")
        
        print(f"\nDepartments still using generic tables: {departments}")
        
        if not departments:
            print("\n💡 Recommendation: Generic inventory tables are no longer used.")
            print("   You may consider:")
            print("   1. Removing the 'department' field from generic models")
            print("   2. Or repurposing them for other use cases")
            print("   3. Or removing them entirely if not needed")
        elif departments == {'LPAF'}:
            print("\n💡 Recommendation: Only LPAF is using generic tables.")
            print("   Consider migrating LPAF to use dedicated lpaf_ tables as well.")
        else:
            print(f"\n💡 Generic tables are still in use by: {departments}")

if __name__ == '__main__':
    print("🚀 Starting TVET data cleanup from generic inventory tables...")
    
    success = cleanup_old_tvet_data()
    
    if success:
        check_remaining_usage()
        print("\n🎉 Cleanup completed successfully!")
    else:
        print("\n💥 Cleanup failed!")
        sys.exit(1)