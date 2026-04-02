import sys
sys.path.insert(0, 'backend')

import requests
import json

print("=" * 60)
print("Testing Preprocessing API Endpoints")
print("=" * 60)

BASE_URL = "http://localhost:8000/api"

# Test 1: Upload messy dataset
print("\n1. Uploading messy dataset...")
with open('data/sample_orders_messy.csv', 'rb') as f:
    files = {'file': ('sample_orders_messy.csv', f, 'text/csv')}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    
if response.status_code == 200:
    upload_data = response.json()
    dataset_id = upload_data['dataset_id']
    print(f"✅ Upload successful! Dataset ID: {dataset_id}")
else:
    print(f"❌ Upload failed: {response.text}")
    sys.exit(1)

# Test 2: Get quality report
print(f"\n2. Getting data quality report for {dataset_id}...")
response = requests.get(f"{BASE_URL}/dataset/{dataset_id}/quality")

if response.status_code == 200:
    quality = response.json()
    print(f"✅ Quality report received!")
    print(f"   Rows: {quality['total_rows']}")
    print(f"   Columns: {quality['total_columns']}")
    print(f"   Missing: {quality['missing_cells']} ({quality['missing_percentage']}%)")
    print(f"   Duplicates: {quality['duplicate_count']}")
else:
    print(f"❌ Quality check failed: {response.text}")
    sys.exit(1)

# Test 3: Preprocess with different strategies
strategies_to_test = [
    ("auto", "Auto preprocessing"),
    ("fill_median", "Fill with median"),
    ("fill_zero", "Fill with zero")
]

for strategy, description in strategies_to_test:
    print(f"\n3. Testing {description} ({strategy})...")
    
    payload = {
        "dataset_id": dataset_id,
        "strategy": strategy,
        "handle_duplicates": False
    }
    
    response = requests.post(f"{BASE_URL}/dataset/preprocess", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Preprocessing successful!")
        print(f"   Rows: {result['rows_before']} → {result['rows_after']}")
        print(f"   Actions performed: {len(result['actions'])}")
        for action in result['actions'][:3]:  # Show first 3 actions
            print(f"      • {action}")
        print(f"   New missing %: {result['new_quality']['missing_percentage']}%")
    else:
        print(f"❌ Preprocessing failed: {response.text}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
