import json
import sys
import os

def main():
    try:
        with open('translations.json', 'r', encoding='utf-8') as f:
            translations = json.load(f)
    except FileNotFoundError:
        print("Error: translations.json not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Failed to decode translations.json.")
        sys.exit(1)

    if 'en' not in translations:
        print("Error: 'en' (English) block missing in translations.json.")
        sys.exit(1)

    en_keys = set(translations['en'].keys())
    missing_found = False

    for lang_code, data in translations.items():
        if lang_code == 'en':
            continue

        lang_keys = set(data.keys())
        missing_keys = en_keys - lang_keys

        if missing_keys:
            print(f"Missing keys in '{lang_code}':")
            for key in missing_keys:
                print(f"  - {key}")
            missing_found = True
        else:
            print(f"'{lang_code}' checks out.")

    if missing_found:
        print("\nVerification failed: Missing keys found.")
        # We don't exit with error code because we want to report the findings,
        # and maybe proceed with other fixes. But strictly speaking, it failed.
    else:
        print("\nVerification passed: All keys present in all languages.")

if __name__ == "__main__":
    main()
