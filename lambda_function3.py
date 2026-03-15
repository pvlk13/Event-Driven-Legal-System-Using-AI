import boto3
import json
import time
import json , re

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('legal-document-summaries')


EXTRACTION_PROMPT = """You are a legal data entry specialist. Extract ALL data from this police accident report into JSON format.

CRITICAL EXTRACTION RULES:

CRITICAL: Read "VEHICLE 1 DAMAGE CODES" and "VEHICLE 2 DAMAGE CODES" carefully.

For EACH vehicle:
- Box 1 (Point of Impact): severity = "severe", damage_type = "point_of_impact"
- Box 2 (Most Damage): severity = "moderate", damage_type = "most_damage"  
- Additional codes: severity = "minor", damage_type = "other_damage"

DAMAGE CODE MAPPING (NY MV-104A):
01-02: Right Front
03: Center Front (HOOD/GRILLE)
04-05: Left Front
06-08: Left Side (DOORS)
09-10: Left Rear
11: Center Rear (REAR BUMPER/TRUNK)
12-13: Right Rear
14-16: Right Side
17: Entire Vehicle (Demolished)
18: No Damage
19: Other (Undercarriage/Roof)

CRITICAL: In the PDF provided, look at "Officer's Notes". If the notes say "HIT IN THE REAR", ensure the damage_locations reflect the REAR (Code 11) even if the boxes are hard to read.

EXAMPLE from your PDF:
Example: If Box 1 contains '11', the part is 'REAR_BUMPER'. If Box 1 contains '03', the part is 'HOOD'.
→ Extract as:
  "damage_locations": [
    {"part": "REAR", "severity": "severe", "damage_type": "point_of_impact"}
]
PEOPLE:
- Client: If PEDESTRIAN or BICYCLIST exists, they are client. Otherwise, DRIVER 1.
- Opposing Party: The OTHER driver/pedestrian.
- Extract: first_name, last_name, DOB, address, phone (if available)

ACCIDENT DETAILS:
- Accident Date: MM/DD/YYYY
- Time: Military time
- Location: Full address with street, city, state, zip
- Intersection: Cross streets
- Weather: (if mentioned)
- Road Condition: (if mentioned)
- SOL Date: Accident Date + 3 years (YYYY-MM-DD)

VEHICLES:
- License Plate
- Vehicle Year, Make, Model
- VIN (if available)
- Insurance Info
- Owner Name
- Damage Description
- Photos Available: Yes/No
- Image URL or reference (if visible in document)

INJURIES:
- Injured Count
- Injury Types (head, knee, jaw, etc.)
- Treatment Provided
- EMT Name/Badge
- Hospital (if applicable)

POLICE REPORT:
- Report Number
- Officer Name
- Badge Number
- Precinct
- Filed Date

IMAGES TO EXTRACT:
- Client Photo: Description of client (facial features, clothing, distinguishing marks)
- Client Vehicle Photo: Year, make, model, color, visible damage areas
- Opposing Party Photo: Description of opposing party
- Opposing Vehicle Photo: Year, make, model, color, visible damage areas

Extract ONLY this JSON:
{
  "client": {
    "first_name": "CASTILLO",
    "last_name": "FAUSTO",
    "dob": "11/12/1976",
    "address": "106 WEST 105 STREET, NEW YORK, NY",
    "type": "PEDESTRIAN",
    "description": "Male, brown skin, approximately 40-50 years old, wearing gray jacket"
  },
  "opposing_party": {
    "first_name": "CHIMIE",
    "last_name": "DORJEE",
    "dob": "08/18/1994",
    "address": "142-001 41 AVENUE, QUEENS, NY 11355",
    "type": "DRIVER",
    "description": "Male, Asian appearance, approximately 25-35 years old, wearing dark shirt"
  },
  "accident": {
    "date": "11/16/2022",
    "time": "20:01",
    "location": "WEST 105 STREET & CENTRAL PARK WEST",
    "city": "NEW YORK",
    "state": "NY",
    "description": "Vehicle struck pedestrian in crosswalk",
    "sol_date": "2025-11-16"
  },
  "vehicles": [
    {
      "vehicle_number": 1,
      "license_plate": "T698783C",
      "year": "2019",
      "make": "CHEVROLET",
      "model": "SEDAN",
      "color": "White",
      "vin": "N/A",
      "owner": "CHIMIE DORJEE",
      "damage_locations": [
        {"part": "REAR_BUMPER", "code": 1, "severity": "severe", "damage_type": "point_of_impact"},
        {"part": "DOORS", "code": 7, "severity": "moderate", "damage_type": "most_damage"}
      ],
      "point_of_impact_code": 3,
      "most_damage_code": 9,
      "other_damage_codes": [12]      
    }
  ],
  "injuries": {
    "injured_count": 1,
    "injury_types": ["HEAD", "JAW", "RIGHT KNEE"],
    "treatment": "Treated by EMT CRUZ"
  }, 
  "police_report": {
    "report_number": "MV-2022-024-000521",
    "officer": "WILLIAM J CLUNE",
    "badge": "970457",
    "precinct": "024",
    "filed_date": "10/02/2025"
  },
  "images": {
    "client_description": "Male, brown skin, 40-50 years, gray jacket",
    "client_vehicle_description": "2019 Chevrolet Sedan, white, front end damage",
    "opposing_party_description": "Male, Asian, 25-35 years, dark shirt",
    "opposing_vehicle_description": "2013 Subaru Sedan, dark color, minor damage"
  }
}
Return ONLY valid JSON, no other text."""

def lambda_handler(event, context):
    try:
        print("Lambda 3: Extracting ALL legal data")
        
        job_id = event.get('jobId')
        full_text = event.get('fullText')
        summary = event.get('summary')
        
        if not full_text:
            return {'statusCode': 400, 'body': json.dumps('No text provided')}
        
        print(f"Extracting data from {len(full_text)} characters...")
        
        legal_data = extract_legal_data(full_text)
        
        print(f"✓ Data extracted")
        
        # Save ALL fields to DynamoDB
        print(f"Saving ALL fields to DynamoDB...")
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression="""SET 
                client_first_name = :cfn,
                client_last_name = :cln,
                client_dob = :cdob,
                client_address = :caddr,
                client_type = :ctype,
                client_description = :cd,
                client_vehicle_description = :cvd,
                opposing_party_description = :opd,
                opposing_vehicle_description = :ovd,
                opposing_first_name = :opfn,
                opposing_last_name = :opln,
                opposing_dob = :opdob,
                opposing_address = :opaddr,
                opposing_type = :optype,
                accident_date = :ad,
                accident_time = :at,
                accident_location = :aloc,
                accident_city = :acity,
                accident_state = :astate,
                accident_description = :adesc,
                sol_date = :sol,
                vehicles = :veh,
                vehicle_damage_locations = :vdl,
                injured_count = :injc,
                injury_types = :injt,
                injury_treatment = :injtr,
                police_report_number = :prn,
                officer_name = :on,
                badge_number = :bn,
                precinct = :prec,
                filed_date = :fd,
                summary = :sum,
                extracted_data_json = :edj,
                extracted_at = :ts
            """,
            ExpressionAttributeValues={
                ':cfn': legal_data.get('client', {}).get('first_name', 'N/A'),
                ':cln': legal_data.get('client', {}).get('last_name', 'N/A'),
                ':cdob': legal_data.get('client', {}).get('dob', 'N/A'),
                ':caddr': legal_data.get('client', {}).get('address', 'N/A'),
                ':cd': legal_data.get('images', {}).get('client_description', 'N/A'),
                ':cvd': legal_data.get('images', {}).get('client_vehicle_description', 'N/A'),
                ':opd': legal_data.get('images', {}).get('opposing_party_description', 'N/A'),
                ':ovd': legal_data.get('images', {}).get('opposing_vehicle_description', 'N/A'),
                ':ctype': legal_data.get('client', {}).get('type', 'N/A'),
                ':opfn': legal_data.get('opposing_party', {}).get('first_name', 'N/A'),
                ':opln': legal_data.get('opposing_party', {}).get('last_name', 'N/A'),
                ':opdob': legal_data.get('opposing_party', {}).get('dob', 'N/A'),
                ':opaddr': legal_data.get('opposing_party', {}).get('address', 'N/A'),
                ':optype': legal_data.get('opposing_party', {}).get('type', 'N/A'),
                ':ad': legal_data.get('accident', {}).get('date', 'N/A'),
                ':at': legal_data.get('accident', {}).get('time', 'N/A'),
                ':aloc': legal_data.get('accident', {}).get('location', 'N/A'),
                ':acity': legal_data.get('accident', {}).get('city', 'N/A'),
                ':astate': legal_data.get('accident', {}).get('state', 'N/A'),
                ':adesc': legal_data.get('accident', {}).get('description', 'N/A'),
                ':sol': legal_data.get('accident', {}).get('sol_date', 'N/A'),
                ':veh': legal_data.get('vehicles', []),
                ':vdl': legal_data.get('vehicles', []),
                ':injc': legal_data.get('injuries', {}).get('injured_count', 0),
                ':injt': legal_data.get('injuries', {}).get('injury_types', []),
                ':injtr': legal_data.get('injuries', {}).get('treatment', 'N/A'),
                ':prn': legal_data.get('police_report', {}).get('report_number', 'N/A'),
                ':on': legal_data.get('police_report', {}).get('officer', 'N/A'),
                ':bn': legal_data.get('police_report', {}).get('badge', 'N/A'),
                ':prec': legal_data.get('police_report', {}).get('precinct', 'N/A'),
                ':fd': legal_data.get('police_report', {}).get('filed_date', 'N/A'),
                ':sum': summary,
                ':edj': json.dumps(legal_data),
                ':ts': str(int(time.time()))
            }
        )
        
        print(f"✓ ALL fields saved to DynamoDB")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'jobId': job_id,
                'message': 'All data extracted and saved'
            })
        }
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}

def extract_legal_data(text):
    text_limited = text[:20000]
    
    try:
        print(f"Calling Bedrock for comprehensive data extraction...")
        response = bedrock_runtime.converse(
            modelId='arn:aws:bedrock:us-east-1:272183979798:application-inference-profile/8ykdxt4a0ds8',
            messages=[{'role': 'user', 'content': [{'text': f'{EXTRACTION_PROMPT}\n\nDocument text:\n\n{text_limited}'}]}],
            inferenceConfig={'maxTokens': 4000}
        )
        
        response_text = response['output']['message']['content'][0]['text']
        print(f"Raw response length: {len(response_text)}")
        
        # 1. Clean markdown backticks
        clean_text = response_text.strip()
        clean_text = re.sub(r'^```json\s*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'^```\s*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'```$', '', clean_text, flags=re.IGNORECASE)
        clean_text = clean_text.strip()
        
        # 2. Find JSON object
        json_match = re.search(r'\{[\s\S]*\}', clean_text)
        if not json_match:
            print("ERROR: No JSON object found in response")
            return {}
        
        json_str = json_match.group()
        
        # 3. Fix common JSON issues
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unquoted keys (though Claude should quote them)
        # Fix incomplete strings
        json_str = re.sub(r':\s*([^",\[\]{}\n]+)([,\]\}])', r': "\1"\2', json_str)
        
        print(f"Cleaned JSON length: {len(json_str)}")
        
        # 4. Parse JSON
        legal_data = json.loads(json_str)
        print(f"✓ JSON parsed successfully")
        return legal_data
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Error at line {e.lineno}, column {e.colno}")
        # Try to find the problematic part
        lines = response_text.split('\n')
        if len(lines) > e.lineno - 1:
            print(f"Problem line: {lines[e.lineno - 1]}")
        return {}
        
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}

    