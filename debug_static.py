from django.conf import settings
import os

print("=== STATIC FILES DEBUG ===")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

print("\nSTORAGES configuration:")
for key, value in settings.STORAGES.items():
    print(f"  {key}: {value}")

print("\nSTATICFILES_FINDERS:")
for finder in settings.STATICFILES_FINDERS:
    print(f"  {finder}")

print("\nEnvironment variables:")
print(f"  USE_MANIFEST_STATIC: {
    os.environ.get('USE_MANIFEST_STATIC', 'Not set')
    }")
print(f"  USE_STATIC_COMPRESSION: {
    os.environ.get('USE_STATIC_COMPRESSION', 'Not set')
    }")

print(f"\nSTATIC_ROOT exists: {os.path.exists(settings.STATIC_ROOT)}")
print(f"STATIC_ROOT is writable: {
    os.access(settings.STATIC_ROOT, os.W_OK)
    if os.path.exists(settings.STATIC_ROOT) else 'Directory does not exist'
    }")
