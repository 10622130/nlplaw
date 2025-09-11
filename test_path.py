import sys
print("sys.path when running from script location:")
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")

try:
    import api
    print("✓ Successfully imported api")
except ImportError as e:
    print(f"✗ Failed to import api: {e}")