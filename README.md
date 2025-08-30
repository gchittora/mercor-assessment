# Mercor Assessment Project

## Overview

This project implements a contractor application management system using Airtable and Python automation scripts. It covers data collection via multi-step forms, JSON data compression and decompression, candidate shortlisting based on defined business rules, and AI/ML-powered evaluation using the Gemini LLM API.

## Project Structure

- `compress_json.py`: Gathers applicant data from Airtable tables and compresses into JSON
- `decompress_json.py`: Decompresses JSON back into normalized records
- `shortlist_automation.py`: Implements candidate shortlisting rules and manages shortlisted leads
- `llm_evaluation.py`: Interfaces with Gemini LLM API for AI-based candidate evaluation
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file
- `config.py` or `.env`: Configuration files storing API keys and settings

## Setup Instructions

1. Create an Airtable base with required tables and schema as per project specifications
2. Generate Airtable API key and find Base ID via Airtable API documentation
3. Obtain Gemini API credentials
4. Clone this repository and navigate to project directory
5. Create and activate a Python virtual environment:
6. Install dependencies:
7. Configure your APIs and settings in `.env` or `config.py` file

## Usage

- Fill out the multi-step Airtable forms to input applicant data
- Run `compress_json.py` to generate compressed JSON for each applicant
- Run `shortlist_automation.py` to apply candidate filtering rules
- Run `llm_evaluation.py` to perform AI-driven candidate assessment
- Use `decompress_json.py` to restore data for editing if necessary

## Customization

- Adjust candidate shortlist criteria in `shortlist_automation.py`
- Modify LLM prompt templates in `llm_evaluation.py`
- Extend Airtable schema and update scripts accordingly

## Security

- Store API keys securely; do not hardcode credentials
- Respect API rate limits and implement retry mechanisms

## Deliverables

- Airtable base with linked tables and forms
- Python automation scripts
- Documentation (this file)

## Contact

For any queries or support, contact the project maintainer.
