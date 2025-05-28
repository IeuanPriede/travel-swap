from profiles.models import Profile
from django_countries import countries

# Build lookup maps
name_to_code = {name.lower(): code for code, name in countries}
valid_codes = {code for code, name in countries}

updated = 0
skipped = 0

for p in Profile.objects.all():
    raw_location = str(p.location).strip() if p.location else ""
    lower_loc = raw_location.lower()

    if not raw_location:
        print(f"⚠ Blank location for {p.user.username}")
        skipped += 1
        continue

    if raw_location in valid_codes:
        print(f"✔ Already valid code '{raw_location}' for {p.user.username}")
        continue

    if lower_loc in name_to_code:
        new_code = name_to_code[lower_loc]
        print(f"🔁 Converting '{raw_location}' → '{new_code}' "
              f"for {p.user.username}")
        p.location = new_code
        p.save()
        updated += 1
    else:
        print(
            f"⛔ Unrecognized location '{raw_location}' for {p.user.username}")
        skipped += 1

print(f"\n✅ Done. Updated: {updated}, Skipped: {skipped}")
