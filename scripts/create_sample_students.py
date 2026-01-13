#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app, db
from web.models.student import Student

app = create_app()

with app.app_context():
    # Create sample students
    students_data = [
        {
            'batch': 'BATCH-2023-001',
            'name': 'Juan Dela Cruz',
            'age': 22,
            'address': '123 Main St, Manila, Philippines',
            'contact_no': '+63 9123456789',
            'certificate': 'Certificate in Computer Programming'
        },
        {
            'batch': 'BATCH-2023-001',
            'name': 'Maria Santos',
            'age': 20,
            'address': '456 Oak Ave, Quezon City, Philippines',
            'contact_no': '+63 9234567890',
            'certificate': 'Certificate in Computer Programming'
        },
        {
            'batch': 'BATCH-2023-002',
            'name': 'Pedro Rodriguez',
            'age': 24,
            'address': '789 Pine Rd, Cebu City, Philippines',
            'contact_no': '+63 9345678901',
            'certificate': 'Certificate in Electrical Installation'
        },
        {
            'batch': 'BATCH-2023-002',
            'name': 'Ana Garcia',
            'age': 21,
            'address': '321 Elm St, Davao City, Philippines',
            'contact_no': '+63 9456789012',
            'certificate': 'Certificate in Electrical Installation'
        },
        {
            'batch': 'BATCH-2023-003',
            'name': 'Miguel Torres',
            'age': 23,
            'address': '654 Maple Dr, Iloilo City, Philippines',
            'contact_no': '+63 9567890123',
            'certificate': 'Certificate in Automotive Technology'
        }
    ]
    
    try:
        for student_data in students_data:
            # Check if student already exists
            existing = Student.query.filter_by(name=student_data['name']).first()
            if not existing:
                student = Student(**student_data)
                db.session.add(student)
                print(f"Added student: {student_data['name']}")
            else:
                print(f"Student already exists: {student_data['name']}")
        
        db.session.commit()
        print(f"\nSample students created successfully!")
        
        # Verify the data
        all_students = Student.query.all()
        print(f"Total students in database: {len(all_students)}")
        for student in all_students:
            print(f"- {student.name} (Batch: {student.batch})")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample students: {e}")