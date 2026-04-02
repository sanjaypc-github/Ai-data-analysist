import sys
import os
os.chdir('backend')
sys.path.insert(0, '.')

from app.report_generator import generate_report
from app.utils import load_task_metadata

# Get latest task
from pathlib import Path
tasks_dir = Path("data/tasks")
latest_task = sorted(tasks_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[0]
task_id = latest_task.name

print(f"Testing report generation for: {task_id}")

try:
    metadata = load_task_metadata(task_id)
    print(f"✓ Metadata loaded: {metadata.get('question')}")
    print(f"  Status: {metadata.get('status')}")
    
    report_path = generate_report(task_id, metadata)
    print(f"✓ Report generated: {report_path}")
    
    if os.path.exists(report_path):
        print(f"✓ Report file exists! Size: {os.path.getsize(report_path)} bytes")
    else:
        print("✗ Report file not found!")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
