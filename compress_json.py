import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

def get_records(table_name):
    """Fetch all records from a table"""
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()['records']
    else:
        print(f"Error fetching {table_name}: {response.text}")
        return []

def compress_applicant_data():
    """Main function to compress data for each applicant"""
    
    # Fetch all records
    applicants = get_records('Applicants')
    personal_details = get_records('Personal Details')
    work_experience = get_records('Work Experience')
    salary_preferences = get_records('Salary Preferences')
    
    for applicant in applicants:
        applicant_id = applicant['fields'].get('Applicant ID', '')
        if not applicant_id:
            continue
            
        # Build JSON structure
        compressed_data = {
            "personal": {},
            "experience": [],
            "salary": {}
        }
        
        # Add personal details
        personal = next((p for p in personal_details if p['fields'].get('Applicant') == [applicant['id']]), None)
        if personal:
            compressed_data["personal"] = {
                "name": personal['fields'].get('Full Name', ''),
                "email": personal['fields'].get('Email', ''),
                "location": personal['fields'].get('Location', ''),
                "linkedin": personal['fields'].get('LinkedIn', '')
            }
        
        # Add work experience
        for exp in work_experience:
            if exp['fields'].get('Applicant') == [applicant['id']]:
                compressed_data["experience"].append({
                    "company": exp['fields'].get('Company', ''),
                    "title": exp['fields'].get('Title', ''),
                    "start_date": exp['fields'].get('Start Date', ''),
                    "end_date": exp['fields'].get('End Date', ''),
                    "technologies": exp['fields'].get('Technologies', '')
                })
        
        # Add salary preferences
        salary = next((s for s in salary_preferences if s['fields'].get('Applicant') == [applicant['id']]), None)
        if salary:
            compressed_data["salary"] = {
                "preferred_rate": salary['fields'].get('Preferred Rate', 0),
                "minimum_rate": salary['fields'].get('Minimum Rate', 0),
                "currency": salary['fields'].get('Currency', 'USD'),
                "availability": salary['fields'].get('Availability', 0)
            }
        
        # Update applicant record with compressed JSON
        update_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Applicants/{applicant["id"]}'
        update_data = {
            "fields": {
                "Compressed JSON": json.dumps(compressed_data, indent=2)
            }
        }
        
        response = requests.patch(update_url, headers=HEADERS, json=update_data)
        if response.status_code == 200:
            print(f"Successfully compressed data for applicant: {applicant_id}")
        else:
            print(f"Error updating applicant {applicant_id}: {response.text}")

if __name__ == "__main__":
    compress_applicant_data()
