#!/usr/bin/env python3
"""
Final cleanup script to remove the unused inventory.py file
"""

import os
import shutil

def remove_inventory_file():
    """Remove the unused inventory.py file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    inventory_file = os.path.join(parent_dir, 'web', 'models', 'inventory.py')
    backup_file = os.path.join(parent_dir, 'web', 'models', 'inventory.py.backup')
    
    if os.path.exists(inventory_file):
        # Create a backup first
        shutil.copy2(inventory_file, backup_file)
        print(f"✓ Created backup: {backup_file}")
        
        # Remove the original file
        os.remove(inventory_file)
        print(f"✓ Removed: {inventory_file}")
        
        print("\n✅ Cleanup complete!")
        print("📋 The generic inventory.py file has been removed")
        print("📁 A backup was created just in case you need it later")
        
        return True
    else:
        print("❌ inventory.py file not found")
        return False

if __name__ == '__main__':
    print("🗑️  Final cleanup: Removing unused inventory.py file...")
    print("⚠️  This will permanently remove web/models/inventory.py")
    
    response = input("\nProceed with file removal? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        remove_inventory_file()
    else:
        print("🚫 File removal cancelled")