import os
import json
import requests
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def call_gemini_with_retry(prompt, max_retries=3):
    """Call Gemini API with exponential backoff retry"""
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.1,
                )
            )
            
            return response.text
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Gemini API failed after {max_retries} attempts: {e}")
                return None
            
            # Exponential backoff
            wait_time = (2 ** attempt) + 1
            print(f"Gemini API attempt {attempt + 1} failed, retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    return None

def parse_llm_response(response_text):
    """Parse structured LLM response"""
    try:
        lines = response_text.strip().split('\n')
        
        summary = ""
        score = 0
        issues = "None"
        follow_ups = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Summary:'):
                summary = line.replace('Summary:', '').strip()
                current_section = 'summary'
            elif line.startswith('Score:'):
                try:
                    score = int(line.replace('Score:', '').strip())
                except:
                    score = 0
                current_section = 'score'
            elif line.startswith('Issues:'):
                issues = line.replace('Issues:', '').strip()
                current_section = 'issues'
            elif line.startswith('Follow-Ups:'):
                current_section = 'follow_ups'
            elif line.startswith('•') or line.startswith('-'):
                if current_section == 'follow_ups':
                    follow_ups += line + '\n'
        
        return {
            'summary': summary,
            'score': max(1, min(10, score)),  # Ensure score is 1-10
            'issues': issues,
            'follow_ups': follow_ups.strip()
        }
        
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return None

def evaluate_applicant(applicant_data):
    """Generate Gemini evaluation for an applicant"""
    
    prompt = f"""You are a recruiting analyst. Given this JSON applicant profile, do four things:

1. Provide a concise 75-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Applicant Data:
{json.dumps(applicant_data, indent=2)}

Return exactly in this format:
Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>"""

    return call_gemini_with_retry(prompt)

def process_llm_evaluation():
    """Main LLM evaluation function"""
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
        existing_summary = applicant['fields'].get('LLM Summary', '')
        
        # Skip if already processed and JSON hasn't changed
        if existing_summary and compressed_json:
            continue
        
        if not compressed_json:
            print(f"No compressed JSON for applicant {applicant_id}")
            continue
        
        try:
            data = json.loads(compressed_json)
        except json.JSONDecodeError:
            print(f"Invalid JSON for applicant {applicant_id}")
            continue
        
        # Get Gemini evaluation
        gemini_response = evaluate_applicant(data)
        
        if not gemini_response:
            print(f"Failed to get Gemini evaluation for applicant {applicant_id}")
            continue
        
        # Parse response
        parsed = parse_llm_response(gemini_response)
        
        if not parsed:
            print(f"Failed to parse Gemini response for applicant {applicant_id}")
            continue
        
        # Update applicant record
        update_data = {
            'fields': {
                'LLM Summary': parsed['summary'],
                'LLM Score': parsed['score'],
                'LLM Follow-Ups': parsed['follow_ups']
            }
        }
        
        update_url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Applicants/{applicant_id}'
        response = requests.patch(update_url, headers=HEADERS, json=update_data)
        
        if response.status_code == 200:
            print(f"Updated Gemini evaluation for applicant {applicant_id}")
        else:
            print(f"Error updating applicant {applicant_id}: {response.text}")
        
        # Rate limiting - don't overwhelm APIs
        time.sleep(1)

if __name__ == "__main__":
    process_llm_evaluation()
