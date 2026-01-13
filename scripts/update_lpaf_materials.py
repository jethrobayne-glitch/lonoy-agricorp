#!/usr/bin/env python3

import sys
import os

# Add the parent directory to Python path to import the web module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from web import create_app
from web.models import db, LPAFInventoryMaterial

def add_material_fields():
    """Add item_name and description fields to LPAF materials table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Adding new fields to LPAF materials table...")
            
            # Execute raw SQL to add columns
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE lpaf_inventory_materials ADD COLUMN item_name VARCHAR(200)'))
                conn.execute(db.text('ALTER TABLE lpaf_inventory_materials ADD COLUMN description TEXT'))
                conn.commit()
            
            print("✓ Added item_name and description columns")
            
            # Add some sample materials to demonstrate the functionality
            print("Adding sample materials...")
            
            # Get some existing folders, productions, and statuses
            from web.models import LPAFInventoryFolder, LPAFProduction, LPAFStatus
            
            folder = LPAFInventoryFolder.query.first()
            production = LPAFProduction.query.first()
            status = LPAFStatus.query.first()
            
            sample_materials = [
                {
                    'item_name': 'Premium Hybrid Rice Seeds',
                    'description': 'High-yield hybrid rice seeds for optimal production',
                    'folder_id': folder.id if folder else None,
                    'production_id': production.id if production else None,
                    'status_id': status.id if status else None
                },
                {
                    'item_name': 'Organic Fertilizer',
                    'description': 'Natural compost fertilizer for soil enrichment',
                    'folder_id': folder.id if folder else None,
                    'production_id': production.id if production else None,
                    'status_id': status.id if status else None
                },
                {
                    'item_name': 'Irrigation System',
                    'description': 'Drip irrigation system for efficient water management',
                    'folder_id': folder.id if folder else None,
                    'production_id': production.id if production else None,
                    'status_id': status.id if status else None
                }
            ]
            
            for material_data in sample_materials:
                material = LPAFInventoryMaterial(**material_data)
                db.session.add(material)
            
            db.session.commit()
            
            print("✓ Added sample materials successfully!")
            
            # Verify materials were created
            material_count = LPAFInventoryMaterial.query.count()
            print(f"✓ Total materials in database: {material_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating LPAF materials table: {str(e)}")
            return False
        
        return True

if __name__ == '__main__':
    success = add_material_fields()
    if success:
        print("\n🎉 LPAF materials table updated successfully!")
    else:
        print("\n💥 LPAF materials table update failed!")
        sys.exit(1)