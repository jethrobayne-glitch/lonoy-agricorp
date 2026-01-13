#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app, db
from web.models.employee import Employee
from web.models.employee_document import EmployeeDocument

app = create_app()

with app.app_context():
    try:
        print("Creating employee tables...")
        
        # Create all tables including employees and employee_documents
        db.create_all()
        print("✓ Created employee tables")
        
        # Ensure uploads directory exists
        os.makedirs("web/static/uploads/employee_documents", exist_ok=True)
        print("✓ Created employee documents upload directory")
        
        # Create some sample employees
        sample_employees = [
            {
                'name': 'Dr. Rosa Maria Villanueva',
                'position': 'TVET Director',
                'job_description': 'Overall management and supervision of TVET programs, curriculum development, and strategic planning'
            },
            {
                'name': 'Engr. Mark Anthony Cruz',
                'position': 'Agricultural Production Instructor',
                'job_description': 'Teaching crop production techniques, soil management, and sustainable farming practices'
            },
            {
                'name': 'Dr. Carmen Dela Torre',
                'position': 'Livestock Management Instructor',
                'job_description': 'Teaching animal husbandry, veterinary care, and livestock production management'
            },
            {
                'name': 'Prof. James Rodriguez',
                'position': 'Farm Equipment Technician',
                'job_description': 'Maintenance and operation of farm machinery, equipment troubleshooting and repair'
            },
            {
                'name': 'Ms. Luisa Mae Gonzales',
                'position': 'Administrative Assistant',
                'job_description': 'Student records management, enrollment processing, and general administrative support'
            }
        ]
        
        for emp_data in sample_employees:
            # Check if employee already exists
            existing = Employee.query.filter_by(name=emp_data['name']).first()
            if not existing:
                employee = Employee(**emp_data)
                db.session.add(employee)
                print(f"Added employee: {emp_data['name']}")
            else:
                print(f"Employee already exists: {emp_data['name']}")
        
        db.session.commit()
        print(f"\nSample employees created successfully!")
        
        # Verify the data
        all_employees = Employee.query.all()
        print(f"Total employees in database: {len(all_employees)}")
        for employee in all_employees:
            print(f"- {employee.name} ({employee.position})")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error creating employee tables: {e}")
        import traceback
        traceback.print_exc()