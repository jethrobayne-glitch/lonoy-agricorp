#!/usr/bin/env python3

import sys
import os

# Add the parent directory to Python path to import the web module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from web import create_app
from web.models import db, LPAFInventoryMaterial

def add_item_code_field():
    """Add item_code field to LPAF materials table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Adding item_code field to LPAF materials table...")
            
            # Execute raw SQL to add column
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE lpaf_inventory_materials ADD COLUMN item_code VARCHAR(50)'))
                conn.commit()
            
            print("✓ Added item_code column")
            
            # Update existing materials with sample item codes
            print("Updating existing materials with sample item codes...")
            
            materials = LPAFInventoryMaterial.query.all()
            
            for i, material in enumerate(materials, 1):
                if material.item_name:
                    # Generate item code based on item name
                    name_parts = material.item_name.split()
                    if len(name_parts) >= 2:
                        code = f"{name_parts[0][:4].upper()}-{str(i).zfill(3)}"
                    else:
                        code = f"{material.item_name[:4].upper()}-{str(i).zfill(3)}"
                    
                    material.item_code = code
                    print(f"  • {material.item_name} -> {code}")
            
            db.session.commit()
            
            print("✓ Updated existing materials with item codes")
            
            # Verify materials were updated
            material_count = LPAFInventoryMaterial.query.filter(LPAFInventoryMaterial.item_code.isnot(None)).count()
            print(f"✓ {material_count} materials now have item codes")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating LPAF materials table: {str(e)}")
            return False
        
        return True

if __name__ == '__main__':
    success = add_item_code_field()
    if success:
        print("\n🎉 Item code field added successfully!")
    else:
        print("\n💥 Item code field addition failed!")
        sys.exit(1)