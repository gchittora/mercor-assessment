import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Test environment variables
print("Testing environment setup...")
print(f"Airtable API Key: {'✓' if os.getenv('AIRTABLE_API_KEY') else '✗'}")
print(f"Airtable Base ID: {'✓' if os.getenv('AIRTABLE_BASE_ID') else '✗'}")
print(f"Gemini API Key: {'✓' if os.getenv('GEMINI_API_KEY') else '✗'}")

# Test Airtable API connection
if os.getenv('AIRTABLE_API_KEY') and os.getenv('AIRTABLE_BASE_ID'):
    headers = {'Authorization': f'Bearer {os.getenv("AIRTABLE_API_KEY")}'}
    url = f'https://api.airtable.com/v0/{os.getenv("AIRTABLE_BASE_ID")}/Applicants'
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Airtable API Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Airtable connection successful!")
        else:
            print(f"✗ Airtable error: {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
else:
    print("✗ Missing environment variables")

