import json
import requests
import phonenumbers
from phonenumbers.phonemetadata import PhoneMetadata
from phonenumbers.util import u

def get_up_to_date_phone_formats():
    """
    Fetch up-to-date phone number formats using the phonenumbers library (Google's libphonenumber)
    """
    print("Fetching up-to-date phone number formats...")
    phone_format_data = {}
    
    # Get all available regions
    regions = phonenumbers.SUPPORTED_REGIONS
    
    for region in regions:
        try:
            # Get metadata for the region
            metadata = PhoneMetadata.metadata_for_region(region, None)
            if metadata and metadata.general_desc and metadata.general_desc.possible_length:
                # Get country code
                country_code = str(metadata.country_code)
                
                # Get maximum length allowed for the region
                # The possible_length field contains all possible lengths
                # We'll take the maximum for simplicity
                max_length = max(metadata.general_desc.possible_length)
                
                # Example format
                example_format = f"+{country_code} "
                if max_length <= 4:
                    example_format += "X" * max_length
                elif max_length <= 7:
                    example_format += "XXX " + "X" * (max_length - 3)
                else:
                    example_format += "XXX XXX " + "X" * (max_length - 6)
                
                # Add to our data
                phone_format_data[region] = {
                    "country_code": country_code,
                    "max_length": max_length,
                    "example_format": example_format
                }
        except Exception as e:
            print(f"Error processing region {region}: {e}")
    
    print(f"Successfully fetched formats for {len(phone_format_data)} countries.")
    return phone_format_data

# Main execution
try:
    # Try to use the phonenumbers library to get up-to-date formats
    import phonenumbers
    phone_format_data = get_up_to_date_phone_formats()
except ImportError:
    print("phonenumbers library not found. Using hardcoded data instead.")
    # Fall back to hardcoded data if the library is not available
    phone_format_data = {}

# Add additional useful information to the data
for country_code, data in phone_format_data.items():
    # Add ISO country code as explicit field
    data["ISO"] = country_code
    
    # Add total max digits (country code + max length)
    data["total_max_digits"] = len(data["country_code"]) + data["max_length"]
    
    # Add regex pattern (simplified)
    data["regex"] = f"^\\+{data['country_code']}\\d{{{data['max_length']}}}$"

# Fetch Government of Canada country codes and add to our data
try:
    print("Fetching Government of Canada country codes...")
    url = "https://open.canada.ca/data/en/datastore/dump/bdb33e8c-53ef-4bae-9493-35f343191c02?format=json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    gc_data = response.json()
    print(f"Successfully fetched data from Government of Canada.")
    
    # First, get the field indices for the columns we need
    fields = gc_data.get('fields', [])
    iso_alpha_2_index = None
    gc_id_index = None
    gc_nm_ab_en_index = None
    gc_nm_ab_fr_index = None
    
    for i, field in enumerate(fields):
        if field.get('id') == 'ISO_ALPHA_2_CD':
            iso_alpha_2_index = i
        elif field.get('id') == 'GC_ID':
            gc_id_index = i
        elif field.get('id') == 'GC_NM_AB_EN':
            gc_nm_ab_en_index = i
        elif field.get('id') == 'GC_NM_AB_FR':
            gc_nm_ab_fr_index = i
    
    print(f"Field indices - ISO: {iso_alpha_2_index}, GC_ID: {gc_id_index}, EN: {gc_nm_ab_en_index}, FR: {gc_nm_ab_fr_index}")
    
    # Process records if we have the needed indices
    countries_processed = 0
    records = gc_data.get('records', [])
    
    # If we don't have the field structure, try to determine it from first record
    if iso_alpha_2_index is None and records:
        # Sample field order from the debug output
        # Assuming positions from the sample record:
        # GC_ID might be at index 0 ('1000110')
        # GC_NM_AB_EN might be at index 4 ('Fiji')
        # GC_NM_AB_FR might be at index 5 ('Fidji')
        # ISO_ALPHA_2_CD might be at index 19 ('FJ')
        iso_alpha_2_index = 19  # Based on the sample output
        gc_id_index = 0
        gc_nm_ab_en_index = 4
        gc_nm_ab_fr_index = 5
    
    if all(index is not None for index in (iso_alpha_2_index, gc_id_index, gc_nm_ab_en_index, gc_nm_ab_fr_index)):
        for record in records:
            if len(record) > max(iso_alpha_2_index, gc_id_index, gc_nm_ab_en_index, gc_nm_ab_fr_index):
                iso_code = record[iso_alpha_2_index]
                if iso_code and iso_code in phone_format_data:
                    # Add Government of Canada specific fields
                    phone_format_data[iso_code]['GC_ID'] = record[gc_id_index]
                    phone_format_data[iso_code]['GC_NM_AB_EN'] = record[gc_nm_ab_en_index]
                    phone_format_data[iso_code]['GC_NM_AB_FR'] = record[gc_nm_ab_fr_index]
                    countries_processed += 1
    
    print(f"Added Government of Canada data to {countries_processed} countries.")
except Exception as e:
    print(f"Error fetching Government of Canada data: {e}")
    import traceback
    traceback.print_exc()
    print("Continuing with existing data only.")

# Print country code and ISO for each entry before sorting (for debugging)
print("Before sorting:")
for iso, data in list(phone_format_data.items())[:5]:
    print(f"ISO: {iso}, Country Code: {data['country_code']}")

# Sort data first by country code numerically, then by ISO code alphabetically
sorted_phone_format_data = {}
# Group by country code
country_code_groups = {}
for iso, data in phone_format_data.items():
    country_code = data["country_code"]
    if country_code not in country_code_groups:
        country_code_groups[country_code] = []
    country_code_groups[country_code].append((iso, data))

# Sort country codes numerically
for country_code in sorted(country_code_groups.keys(), key=int):
    # For each country code, sort by ISO alphabetically
    for iso, data in sorted(country_code_groups[country_code], key=lambda x: x[0]):
        sorted_phone_format_data[iso] = data

# Print a few entries after sorting (for debugging)
print("After sorting:")
for iso, data in list(sorted_phone_format_data.items())[:5]:
    print(f"ISO: {iso}, Country Code: {data['country_code']}")

# Write data to a JSON file with proper UTF-8 encoding
with open('phone_formats_e164.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_phone_format_data, f, indent=2, ensure_ascii=False)

print("Phone format data has been written to 'phone_formats_e164.json' with UTF-8 encoding")