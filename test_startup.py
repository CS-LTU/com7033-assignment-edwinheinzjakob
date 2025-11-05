"""Test script to verify application startup"""
import sys
import io

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from app import create_app
    app = create_app('development')
    print("[SUCCESS] Application initialized successfully!")
    print("[SUCCESS] All blueprints registered")
    print("[SUCCESS] Ready to run: python run.py")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

