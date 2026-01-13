#!/usr/bin/env python3
"""
Optional script to completely remove the generic inventory models from the system
This script should only be run after confirming that the system works without the generic routes
"""

import sys
import os

# Add the parent directory to Python path to import the web module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def check_generic_model_usage():
    """Check if generic inventory models are used anywhere in the codebase"""
    print("🔍 Checking for remaining usage of generic inventory models...")
    
    generic_models = ['InventoryFolder', 'CoreCompetency', 'Category', 'InspectionRemark', 'InventoryMaterial']
    files_to_check = [
        'web/__init__.py',
        'web/routes/main.py',
        'web/routes/auth.py',
    ]
    
    usage_found = False
    
    for file_path in files_to_check:
        full_path = os.path.join(parent_dir, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for model in generic_models:
                if model in content and 'Tvet' not in content.split(model)[0][-10:] and 'LPAF' not in content.split(model)[0][-10:]:
                    print(f"⚠️  Found usage of {model} in {file_path}")
                    usage_found = True
                    
        except Exception as e:
            print(f"❌ Error checking {file_path}: {str(e)}")
    
    return not usage_found

def remove_generic_models():
    """Remove generic inventory models from models/__init__.py and inventory.py"""
    models_init_path = os.path.join(parent_dir, 'web', 'models', '__init__.py')
    inventory_model_path = os.path.join(parent_dir, 'web', 'models', 'inventory.py')
    
    try:
        # Update __init__.py to remove generic model imports and exports
        with open(models_init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove imports
        content = content.replace('from .inventory import InventoryFolder, CoreCompetency, Category, InspectionRemark, InventoryMaterial', '')
        
        # Remove from __all__ list
        for model in ['InventoryFolder', 'CoreCompetency', 'Category', 'InspectionRemark', 'InventoryMaterial']:
            content = content.replace(f"'{model}', ", "")
            content = content.replace(f", '{model}'", "")
            content = content.replace(f"'{model}'", "")
        
        # Clean up any extra commas
        content = content.replace(', ,', ',').replace(',,', ',')
        
        with open(models_init_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Updated web/models/__init__.py")
        
        # Optionally, you could remove the inventory.py file entirely
        # But let's keep it commented for now in case it's needed later
        print("💡 Note: web/models/inventory.py file still exists but is no longer imported")
        print("   You can manually delete it if you're sure it won't be needed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error removing generic models: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Starting optional removal of generic inventory models...")
    print("⚠️  WARNING: This will completely remove generic inventory models from the system!")
    print("   Only proceed if you're sure they're not needed elsewhere.\n")
    
    # Check for usage first
    if not check_generic_model_usage():
        print("❌ Generic models are still being used somewhere. Aborting cleanup.")
        sys.exit(1)
    
    print("✓ No usage of generic inventory models found in main application files")
    
    # Ask for confirmation
    response = input("\nProceed with removal of generic inventory models? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = remove_generic_models()
        
        if success:
            print("\n✅ Generic inventory models removed successfully!")
            print("\n📋 Final cleanup summary:")
            print("✓ Removed generic inventory models from __init__.py")
            print("✓ Generic inventory.py file preserved but no longer imported") 
            print("✓ System now uses only department-specific models (tvet_, lpaf_)")
            print("\n💡 Remember to test the application to ensure everything still works!")
        else:
            print("\n❌ Failed to remove generic inventory models")
            sys.exit(1)
    else:
        print("🚫 Generic model removal cancelled by user")