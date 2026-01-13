#!/usr/bin/env python3
"""
Script to add sample LPAF employees to the database.
Run this from the project root directory.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app, db
from web.models.employee import Employee
from datetime import datetime

def create_lpaf_employees():
    app = create_app()
    
    with app.app_context():
        # Sample LPAF employees
        lpaf_employees = [
            {
                'name': 'Maria Santos',
                'position': 'Finance Manager',
                'job_description': 'Oversees financial operations, budgeting, and financial planning for the LPAF department. Manages financial reports and ensures compliance with accounting standards.',
                'department': 'LPAF'
            },
            {
                'name': 'Roberto Cruz',
                'position': 'Accounting Supervisor',
                'job_description': 'Supervises accounting staff and ensures accurate financial record keeping. Manages accounts payable, receivable, and general ledger maintenance.',
                'department': 'LPAF'
            },
            {
                'name': 'Ana Reyes',
                'position': 'Budget Analyst',
                'job_description': 'Analyzes financial data and prepares budget reports. Monitors departmental spending and provides financial forecasting support.',
                'department': 'LPAF'
            },
            {
                'name': 'Carlos Mendoza',
                'position': 'Procurement Officer',
                'job_description': 'Manages procurement processes, vendor relationships, and supply chain operations. Ensures cost-effective purchasing and contract management.',
                'department': 'LPAF'
            },
            {
                'name': 'Elena Torres',
                'position': 'Financial Analyst',
                'job_description': 'Performs financial analysis, risk assessment, and investment evaluation. Prepares detailed financial models and performance reports.',
                'department': 'LPAF'
            },
            {
                'name': 'Miguel Fernandez',
                'position': 'Treasury Specialist',
                'job_description': 'Manages cash flow, banking relationships, and investment portfolios. Handles treasury operations and financial risk management.',
                'department': 'LPAF'
            }
        ]
        
        # Check if LPAF employees already exist
        existing_lpaf = Employee.query.filter_by(department='LPAF').first()
        if existing_lpaf:
            print("LPAF employees already exist in the database.")
            return
        
        # Add employees to database
        for emp_data in lpaf_employees:
            employee = Employee(**emp_data)
            db.session.add(employee)
        
        try:
            db.session.commit()
            print(f"Successfully added {len(lpaf_employees)} LPAF employees to the database!")
            
            # Print summary
            print("\nAdded LPAF Employees:")
            for emp in lpaf_employees:
                print(f"- {emp['name']} - {emp['position']}")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error adding LPAF employees: {e}")

if __name__ == '__main__':
    create_lpaf_employees()