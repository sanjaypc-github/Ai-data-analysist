import sys
sys.path.insert(0, 'backend')

from pathlib import Path
from app.data_validator import validate_and_preprocess_csv
import json

print("=" * 60)
print("Testing Data Validation & Preprocessing")
print("=" * 60)

# Test with messy data
result = validate_and_preprocess_csv(Path('data/sample_orders_messy.csv'))

print(f"\n✅ Validation Success: {result['success']}")
print(f"📁 Original: {Path(result['original_path']).name}")
print(f"📁 Processed: {Path(result['processed_path']).name}")
print(f"🔧 Preprocessing Needed: {result['preprocessing_needed']}")

if result['preprocessing_actions']:
    print(f"\n🔨 Preprocessing Actions ({len(result['preprocessing_actions'])}):")
    for action in result['preprocessing_actions']:
        print(f"   • {action}")

print(f"\n📊 Quality Report:")
qr = result['quality_report']
print(f"   Rows: {qr['total_rows']}")
print(f"   Columns: {qr['total_columns']}")
print(f"   Missing Values: {qr['missing_cells']} ({qr['missing_percentage']}%)")
print(f"   Has Duplicates: {qr['has_duplicates']}")

print(f"\n📋 Column Details:")
for col in qr['columns']:
    if col['missing_count'] > 0:
        print(f"   • {col['name']}: {col['missing_count']} missing ({col['missing_percentage']:.1f}%)")

print("\n" + "=" * 60)
print("✅ Test completed successfully!")
print("=" * 60)
