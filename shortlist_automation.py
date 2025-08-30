import os
import json
import requests
from datetime import datetime
from dateutil.parser import parse
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

# Shortlist criteria
TIER_1_COMPANIES = ['Google', 'Meta', 'OpenAI', 'Microsoft', 'Apple', 'Amazon', 'Netflix']
APPROVED_LOCATIONS = ['US', 'USA', 'United States', 'Canada', 'UK', 'United Kingdom', 'Germany', 'India']

def calculate_experience_years(experience_list):
    """Calculate total years of experience"""
    total_months = 0
    
    for exp in experience_list:
        start_date = exp.get('start_date', '')
        end_date = exp.get('end_date', '') or datetime.now().strftime('%Y-%m-%d')
        
        try:
            start = parse(start_date)
            end = parse(end_date)
            months = (end.year - start.year) * 12 + (end.month - start.month)
            total_months += months
        except:
            continue
    
    return total_months / 12

def check_shortlist_criteria(applicant_data):
    """Check if applicant meets shortlisting criteria"""
    personal = applicant_data.get('personal', {})
    experience = applicant_data.get('experience', [])
    salary = applicant_data.get('salary', {})
    
    reasons = []
    
    # Experience check
    years_experience = calculate_experience_years(experience)
    has_tier1 = any(comp.get('company', '') in TIER_1_COMPANIES for comp in experience)
    
    experience_qualified = years_experience >= 4 or has_tier1
    if years_experience >= 4:
        reasons.append(f"Has {years_experience:.1f} years of experience")
    if has_tier1:
        tier1_companies = [comp.get('company', '') for comp in experience if comp.get('company', '') in TIER_1_COMPANIES]
        reasons.append(f"Worked at Tier-1 company: {', '.join(tier1_companies)}")
    
    # Compensation check
    preferred_rate = salary.get('preferred_rate', float('inf'))
    availability = salary.get('availability', 0)
    
    compensation_qualified = preferred_rate <= 100 and availability >= 20
    if preferred_rate <= 100:
        reasons.append(f"Preferred rate ${preferred_rate}/hr is within budget")
    if availability >= 20:
        reasons.append(f"Available {availability} hours/week")
    
    # Location check
    location = personal.get('location', '').strip()
    location_qualified = any(loc.lower() in location.lower() for loc in APPROVED_LOCATIONS)
    if location_qualified:
        reasons.append(f"Located in approved region: {location}")
    
    # Final qualification
    qualified = experience_qualified and compensation_qualified and location_qualified
    
    return qualified, reasons

def process_shortlisting():
    """Main shortlisting function"""
    # Get all applicants
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
            continue
        
        # Check shortlist criteria
        qualified, reasons = check_shortlist_criteria(data)
        
        # Update shortlist status
        status_update = {
            'fields': {
                'Shortlist Status': 'Yes' if qualified else 'No'
            }
        }
        
        update_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Applicants/{applicant_id}'
        requests.patch(update_url, headers=HEADERS, json=status_update)
        
        # Create shortlisted lead record if qualified
        if qualified:
            lead_data = {
                'fields': {
                    'Applicant': [applicant_id],
                    'Compressed JSON': compressed_json,
                    'Score Reason': '; '.join(reasons),
                    'Created At': datetime.now().isoformat()
                }
            }
            
            leads_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Shortlisted Leads'
            response = requests.post(leads_url, headers=HEADERS, json=lead_data)
            
            if response.status_code == 200:
                print(f"Shortlisted applicant: {data.get('personal', {}).get('name', 'Unknown')}")
            else:
                print(f"Error creating shortlisted lead: {response.text}")

if __name__ == "__main__":
    process_shortlisting()
