#!/usr/bin/env python3
"""
Script to create inventory tables and add sample data
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from web import create_app
from web.models import db, InventoryFolder, CoreCompetency, Category, InspectionRemark, InventoryMaterial

def create_inventory_tables():
    """Create inventory tables and add sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✓ Inventory tables created successfully!")
            
            # Add sample folders for TVET
            folders = [
                {'name': 'Organic Agricultural Production', 'description': 'Materials for organic farming courses', 'department': 'TVET'},
                {'name': 'Livestock Management', 'description': 'Materials for animal husbandry training', 'department': 'TVET'},
                {'name': 'Farm Equipment Training', 'description': 'Tools and equipment for practical training', 'department': 'TVET'},
            ]
            
            for folder_data in folders:
                if not InventoryFolder.query.filter_by(name=folder_data['name'], department=folder_data['department']).first():
                    folder = InventoryFolder(**folder_data)
                    db.session.add(folder)
            
            # Add sample core competencies for TVET
            competencies = [
                {'name': 'Crop Production', 'description': 'Skills in growing various crops', 'department': 'TVET'},
                {'name': 'Livestock Management', 'description': 'Animal care and breeding', 'department': 'TVET'},
                {'name': 'Soil Management', 'description': 'Soil health and fertility management', 'department': 'TVET'},
                {'name': 'Farm Tools', 'description': 'Use and maintenance of farm equipment', 'department': 'TVET'},
                {'name': 'Pest Management', 'description': 'Organic pest control methods', 'department': 'TVET'},
            ]
            
            for comp_data in competencies:
                if not CoreCompetency.query.filter_by(name=comp_data['name'], department=comp_data['department']).first():
                    competency = CoreCompetency(**comp_data)
                    db.session.add(competency)
            
            # Add sample categories for TVET
            categories = [
                {'name': 'Seeds', 'description': 'Various types of seeds for planting', 'department': 'TVET'},
                {'name': 'Feed', 'description': 'Animal feed and supplements', 'department': 'TVET'},
                {'name': 'Fertilizer', 'description': 'Organic and inorganic fertilizers', 'department': 'TVET'},
                {'name': 'Equipment', 'description': 'Tools and machinery', 'department': 'TVET'},
                {'name': 'Organic Pesticide', 'description': 'Natural pest control products', 'department': 'TVET'},
            ]
            
            for cat_data in categories:
                if not Category.query.filter_by(name=cat_data['name'], department=cat_data['department']).first():
                    category = Category(**cat_data)
                    db.session.add(category)
            
            # Add sample inspection remarks for TVET
            remarks = [
                {'name': 'Good condition', 'description': 'Items are in good working condition', 'department': 'TVET'},
                {'name': 'Excellent', 'description': 'Items are in excellent condition', 'department': 'TVET'},
                {'name': 'Needs replenishment', 'description': 'Stock needs to be replenished', 'department': 'TVET'},
                {'name': 'Complete set', 'description': 'All items in the set are present', 'department': 'TVET'},
                {'name': 'Low stock', 'description': 'Inventory level is low', 'department': 'TVET'},
            ]
            
            for remark_data in remarks:
                if not InspectionRemark.query.filter_by(name=remark_data['name'], department=remark_data['department']).first():
                    remark = InspectionRemark(**remark_data)
                    db.session.add(remark)
            
            # Commit the basic data first
            db.session.commit()
            print("✓ Sample folders, competencies, categories, and remarks added!")
            
            # Now add sample materials
            # Get the IDs for relationships
            crop_production = CoreCompetency.query.filter_by(name='Crop Production', department='TVET').first()
            livestock_mgmt = CoreCompetency.query.filter_by(name='Livestock Management', department='TVET').first()
            soil_mgmt = CoreCompetency.query.filter_by(name='Soil Management', department='TVET').first()
            farm_tools = CoreCompetency.query.filter_by(name='Farm Tools', department='TVET').first()
            pest_mgmt = CoreCompetency.query.filter_by(name='Pest Management', department='TVET').first()
            
            seeds_cat = Category.query.filter_by(name='Seeds', department='TVET').first()
            feed_cat = Category.query.filter_by(name='Feed', department='TVET').first()
            fert_cat = Category.query.filter_by(name='Fertilizer', department='TVET').first()
            equip_cat = Category.query.filter_by(name='Equipment', department='TVET').first()
            pest_cat = Category.query.filter_by(name='Organic Pesticide', department='TVET').first()
            
            good_cond = InspectionRemark.query.filter_by(name='Good condition', department='TVET').first()
            excellent = InspectionRemark.query.filter_by(name='Excellent', department='TVET').first()
            needs_rep = InspectionRemark.query.filter_by(name='Needs replenishment', department='TVET').first()
            complete = InspectionRemark.query.filter_by(name='Complete set', department='TVET').first()
            low_stock = InspectionRemark.query.filter_by(name='Low stock', department='TVET').first()
            
            organic_folder = InventoryFolder.query.filter_by(name='Organic Agricultural Production', department='TVET').first()
            
            sample_materials = [
                {
                    'folder_id': organic_folder.id if organic_folder else None,
                    'competency_id': crop_production.id if crop_production else None,
                    'category_id': seeds_cat.id if seeds_cat else None,
                    'inspection_remark_id': good_cond.id if good_cond else None,
                    'item': 'Tomato Seeds',
                    'specification': 'Hybrid variety, 95% germination',
                    'quantity_required': 500,
                    'quantity_on_site': 450,
                    'quantity_y1': 200,
                    'quantity_y2': 300,
                    'department': 'TVET'
                },
                {
                    'folder_id': organic_folder.id if organic_folder else None,
                    'competency_id': livestock_mgmt.id if livestock_mgmt else None,
                    'category_id': feed_cat.id if feed_cat else None,
                    'inspection_remark_id': excellent.id if excellent else None,
                    'item': 'Pig Feed',
                    'specification': 'Starter feed, 20% protein',
                    'quantity_required': 100,
                    'quantity_on_site': 120,
                    'quantity_y1': 60,
                    'quantity_y2': 40,
                    'department': 'TVET'
                },
                {
                    'folder_id': organic_folder.id if organic_folder else None,
                    'competency_id': soil_mgmt.id if soil_mgmt else None,
                    'category_id': fert_cat.id if fert_cat else None,
                    'inspection_remark_id': needs_rep.id if needs_rep else None,
                    'item': 'Organic Compost',
                    'specification': 'Well-decomposed, pH 6.5-7.0',
                    'quantity_required': 200,
                    'quantity_on_site': 180,
                    'quantity_y1': 100,
                    'quantity_y2': 100,
                    'department': 'TVET'
                },
                {
                    'folder_id': organic_folder.id if organic_folder else None,
                    'competency_id': farm_tools.id if farm_tools else None,
                    'category_id': equip_cat.id if equip_cat else None,
                    'inspection_remark_id': complete.id if complete else None,
                    'item': 'Hand Trowel',
                    'specification': 'Stainless steel, ergonomic handle',
                    'quantity_required': 25,
                    'quantity_on_site': 25,
                    'quantity_y1': 15,
                    'quantity_y2': 10,
                    'department': 'TVET'
                },
                {
                    'folder_id': organic_folder.id if organic_folder else None,
                    'competency_id': pest_mgmt.id if pest_mgmt else None,
                    'category_id': pest_cat.id if pest_cat else None,
                    'inspection_remark_id': low_stock.id if low_stock else None,
                    'item': 'Neem Oil',
                    'specification': '100% pure, cold-pressed',
                    'quantity_required': 50,
                    'quantity_on_site': 35,
                    'quantity_y1': 25,
                    'quantity_y2': 25,
                    'department': 'TVET'
                }
            ]
            
            for material_data in sample_materials:
                if not InventoryMaterial.query.filter_by(item=material_data['item'], department=material_data['department']).first():
                    material = InventoryMaterial(**material_data)
                    db.session.add(material)
            
            db.session.commit()
            print("✓ Sample inventory materials added!")
            
            return True
            
        except Exception as e:
            print(f"✗ Error creating inventory tables: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Creating inventory tables and sample data...")
    success = create_inventory_tables()
    
    if success:
        print("\n✓ Inventory system setup completed successfully!")
        print("You can now access the TVET inventory with full functionality.")
    else:
        print("\n✗ Setup failed. Please check the error messages above.")