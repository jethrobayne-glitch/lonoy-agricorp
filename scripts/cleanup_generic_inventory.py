#!/usr/bin/env python3
"""
Script to remove unused generic inventory routes and models from the system
"""

import sys
import os

# Add the parent directory to Python path to import the web module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def remove_generic_inventory_routes():
    """Remove the generic inventory routes from main.py"""
    main_py_path = os.path.join(parent_dir, 'web', 'routes', 'main.py')
    
    try:
        with open(main_py_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the start and end of the generic inventory section
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if '# Inventory Management API Routes' in line:
                start_idx = i
            elif start_idx is not None and '# Certificate Management Routes' in line:
                end_idx = i
                break
        
        if start_idx is not None and end_idx is not None:
            print(f"Found generic inventory routes from line {start_idx + 1} to {end_idx}")
            
            # Remove the generic inventory section (keep the certificate line)
            new_lines = lines[:start_idx] + lines[end_idx:]
            
            # Write back the modified content
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"✓ Removed {end_idx - start_idx} lines of generic inventory routes")
            return True
        else:
            print("❌ Could not find generic inventory routes section")
            return False
            
    except Exception as e:
        print(f"❌ Error removing generic inventory routes: {str(e)}")
        return False

def update_imports():
    """Remove generic inventory model imports from files that no longer need them"""
    files_to_update = [
        'web/__init__.py',
        'web/routes/main.py',
        'web/models/__init__.py'
    ]
    
    for file_path in files_to_update:
        full_path = os.path.join(parent_dir, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove generic inventory model imports but keep them in __all__ for backwards compatibility
            if file_path == 'web/models/__init__.py':
                # Keep the imports but we can remove them later if not used elsewhere
                print(f"✓ Keeping generic inventory imports in {file_path} for backwards compatibility")
            elif file_path == 'web/__init__.py':
                # Remove from web/__init__.py if imported there
                content = content.replace(', InventoryFolder, CoreCompetency, Category, InspectionRemark, InventoryMaterial', '')
                print(f"✓ Updated imports in {file_path}")
            elif file_path == 'web/routes/main.py':
                # Remove from routes/main.py since we're removing the routes
                content = content.replace('InventoryFolder, CoreCompetency, Category, InspectionRemark, InventoryMaterial, ', '')
                print(f"✓ Updated imports in {file_path}")
            
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Updated {file_path}")
                
        except Exception as e:
            print(f"⚠️  Error updating {file_path}: {str(e)}")

if __name__ == '__main__':
    print("🚀 Starting cleanup of unused generic inventory routes and models...")
    
    # Step 1: Remove generic inventory routes
    routes_success = remove_generic_inventory_routes()
    
    # Step 2: Update imports
    if routes_success:
        print("\n📝 Updating imports...")
        update_imports()
    
    # Step 3: Summary
    if routes_success:
        print("\n✅ Cleanup completed successfully!")
        print("\n📋 Summary of changes:")
        print("✓ Removed all generic inventory API routes (/api/inventory/*)")
        print("✓ Updated import statements in affected files")
        print("✓ Generic inventory models preserved in models/__init__.py for backwards compatibility")
        print("\n💡 Next steps:")
        print("1. Test the application to ensure TVET and LPAF inventory still work")
        print("2. If everything works, you can optionally remove the generic models entirely")
        print("3. The generic database tables still exist but are empty")
    else:
        print("\n💥 Cleanup failed!")
        sys.exit(1)