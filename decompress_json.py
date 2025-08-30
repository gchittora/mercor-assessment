import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

def update_or_create_record(table_name, data, record_id=None):
    """Update existing record or create new one"""
    if record_id:
        # Update existing record
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}/{record_id}'
        response = requests.patch(url, headers=HEADERS, json={"fields": data})
    else:
        # Create new record
        url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}'
        response = requests.post(url, headers=HEADERS, json={"fields": data})
    
    return response

def decompress_applicant_data():
    """Decompress JSON data back to normalized tables"""
    
    # Get all applicants with compressed JSON
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Applicants'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error fetching applicants: {response.text}")
        return
    
    applicants = response.json()['records']
    
    for applicant in applicants:
        applicant_id = applicant['id']
        compressed_json = applicant['fields'].get('Compressed JSON', '')
        
        if not compressed_json:
            continue
            
        try:
            data = json.loads(compressed_json)
        except json.JSONDecodeError:
            print(f"Invalid JSON for applicant {applicant_id}")
            continue
        
        # Update Personal Details
        if 'personal' in data:
            personal_data = {
                **data['personal'],
                'Applicant': [applicant_id]
            }
            response = update_or_create_record('Personal Details', personal_data)
            if response.status_code not in [200, 201]:
                print(f"Error updating personal details: {response.text}")
        
        # Update Work Experience
        if 'experience' in data:
            for exp in data['experience']:
                exp_data = {
                    **exp,
                    'Applicant': [applicant_id]
                }
                response = update_or_create_record('Work Experience', exp_data)
                if response.status_code not in [200, 201]:
                    print(f"Error updating work experience: {response.text}")
        
        # Update Salary Preferences
        if 'salary' in data:
            salary_data = {
                **data['salary'],
                'Applicant': [applicant_id]
            }
            response = update_or_create_record('Salary Preferences', salary_data)
            if response.status_code not in [200, 201]:
                print(f"Error updating salary preferences: {response.text}")
        
        print(f"Successfully decompressed data for applicant: {applicant_id}")

if __name__ == "__main__":
    decompress_applicant_data()
