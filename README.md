# Phone Format E.164

A Python utility for managing international phone number formats according to the E.164 standard.

## Features

- Dynamically fetches up-to-date phone number formats from Google's libphonenumber library
- Includes Government of Canada country codes (ISO, GC_ID, English and French abbreviations)
- Provides maximum digit length for each country
- Generates regex patterns for validation
- Outputs data in UTF-8 encoded JSON format with proper accent support

## Usage

Run the script to generate an updated `phone_formats_e164.json` file:

```bash
python phone_format.py
```

The generated JSON file contains:
- Country code information
- Maximum phone number length by country
- Example formats
- Total maximum digits
- Regex patterns for validation
- Government of Canada specific country codes

## Dependencies

- Python 3.x
- requests
- phonenumbers (Python port of Google's libphonenumber)

## Installation

```bash
pip install requests phonenumbers
```

## License

MIT