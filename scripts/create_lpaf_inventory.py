#!/usr/bin/env python3

import sys
import os

# Add the parent directory to Python path to import the web module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from web import create_app
from web.models import db, LPAFInventoryFolder, LPAFProduction, LPAFStatus, LPAFInventoryMaterial

def create_lpaf_inventory_tables():
    """Create LPAF inventory system tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables
            print("Creating LPAF inventory tables...")
            
            # Create all LPAF inventory related tables
            db.create_all()
            
            # Create some default data
            print("Adding default LPAF inventory data...")
            
            # Default folders
            default_folders = [
                {'name': 'Organic Agricultural Production', 'description': 'Organic farming and agricultural production materials'},
                {'name': 'Equipment Management', 'description': 'Agricultural equipment and machinery'},
                {'name': 'Crop Production', 'description': 'Crop specific production materials'},
                {'name': 'Livestock Management', 'description': 'Livestock and animal husbandry materials'}
            ]
            
            for folder_data in default_folders:
                existing_folder = LPAFInventoryFolder.query.filter_by(name=folder_data['name']).first()
                if not existing_folder:
                    folder = LPAFInventoryFolder(**folder_data)
                    db.session.add(folder)
            
            # Default productions
            default_productions = [
                {'name': 'Rice Production', 'description': 'Rice farming and cultivation'},
                {'name': 'Vegetable Production', 'description': 'Vegetable growing and harvesting'},
                {'name': 'Corn Production', 'description': 'Corn farming operations'},
                {'name': 'Fruit Production', 'description': 'Fruit tree cultivation and management'},
                {'name': 'Livestock Feed Production', 'description': 'Feed production for livestock'}
            ]
            
            for prod_data in default_productions:
                existing_production = LPAFProduction.query.filter_by(name=prod_data['name']).first()
                if not existing_production:
                    production = LPAFProduction(**prod_data)
                    db.session.add(production)
            
            # Default statuses
            default_statuses = [
                {'name': 'In Stock', 'description': 'Items currently available in inventory'},
                {'name': 'Low Stock', 'description': 'Items with low inventory levels'},
                {'name': 'Out of Stock', 'description': 'Items currently not available'},
                {'name': 'On Order', 'description': 'Items that have been ordered but not yet received'},
                {'name': 'Available', 'description': 'Items ready for use'},
                {'name': 'Under Maintenance', 'description': 'Items currently being maintained or repaired'}
            ]
            
            for status_data in default_statuses:
                existing_status = LPAFStatus.query.filter_by(name=status_data['name']).first()
                if not existing_status:
                    status = LPAFStatus(**status_data)
                    db.session.add(status)
            
            # Commit all changes
            db.session.commit()
            
            print("✓ LPAF inventory tables created successfully!")
            print("✓ Default data added successfully!")
            
            # Verify tables were created
            folder_count = LPAFInventoryFolder.query.count()
            production_count = LPAFProduction.query.count()
            status_count = LPAFStatus.query.count()
            
            print(f"✓ Created {folder_count} default folders")
            print(f"✓ Created {production_count} default productions")
            print(f"✓ Created {status_count} default statuses")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating LPAF inventory tables: {str(e)}")
            return False
        
        return True

if __name__ == '__main__':
    success = create_lpaf_inventory_tables()
    if success:
        print("\n🎉 LPAF inventory system setup completed successfully!")
    else:
        print("\n💥 LPAF inventory system setup failed!")
        sys.exit(1)