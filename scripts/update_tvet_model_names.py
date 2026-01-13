#!/usr/bin/env python3
"""
Script to update TVET model names from TvetXxx to TVETXxx in routes file
"""

import sys
import os
import re

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def update_tvet_model_names():
    """Update TVET model names in the routes file"""
    routes_file = os.path.join(parent_dir, 'web', 'routes', 'main.py')
    
    try:
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace all TVET model references
        replacements = {
            'TvetInventoryFolder': 'TVETInventoryFolder',
            'TvetCoreCompetency': 'TVETCoreCompetency',
            'TvetCategory': 'TVETCategory',
            'TvetInspectionRemark': 'TVETInspectionRemark',
            'TvetInventoryMaterial': 'TVETInventoryMaterial'
        }
        
        for old_name, new_name in replacements.items():
            # Use word boundary to ensure we don't replace partial matches
            pattern = r'\b' + old_name + r'\b'
            content = re.sub(pattern, new_name, content)
            count = len(re.findall(pattern, original_content))
            if count > 0:
                print(f"✓ Replaced {count} occurrences of {old_name} with {new_name}")
        
        # Write the updated content back
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Successfully updated TVET model names in {routes_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating TVET model names: {str(e)}")
        return False

if __name__ == '__main__':
    print("🔄 Updating TVET model names to use uppercase TVET prefix...")
    
    success = update_tvet_model_names()
    
    if success:
        print("\n📋 All TVET model names updated:")
        print("  • TvetInventoryFolder → TVETInventoryFolder")
        print("  • TvetCoreCompetency → TVETCoreCompetency")
        print("  • TvetCategory → TVETCategory")
        print("  • TvetInspectionRemark → TVETInspectionRemark")
        print("  • TvetInventoryMaterial → TVETInventoryMaterial")
        print("\n💡 TVET models now match LPAF naming convention!")
    else:
        sys.exit(1)