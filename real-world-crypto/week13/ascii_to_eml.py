#!/usr/bin/env python3
"""
Script 2: Convert readable ASCII back to encrypted.eml format
Pipeline: Readable ASCII → Binary DER → Base64 → Modified EML
"""

import subprocess
import sys
import os
import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

def ascii_to_eml(ascii_file, eml_file, original_eml=None):
    """
    Complete pipeline to convert readable ASCII back to EML format
    
    Steps:
    1. Convert ASCII back to binary DER using ascii2der
    2. Encode binary DER to base64
    3. Create EML file with proper headers and base64 payload
    
    Args:
        ascii_file: Path to the input ASCII file
        eml_file: Path to the output EML file
        original_eml: Optional path to original EML (to copy headers)
    """
    
    try:
        # Step 1: Check if input file exists
        if not os.path.exists(ascii_file):
            print(f"✗ Error: Input file '{ascii_file}' not found")
            return False
        
        print(f"[1/4] Reading ASCII format file...")
        with open(ascii_file, 'r') as f:
            ascii_content = f.read()
        print(f"✓ Loaded ASCII content ({len(ascii_content)} characters)")
        
        # Step 2: Convert ASCII back to binary DER
        print(f"[2/4] Converting ASCII to binary DER format...")
        temp_der_file = 'temp_from_ascii.der'
        try:
            # ascii2der reads ASCII and outputs binary DER
            result = subprocess.run(
                ['ascii2der', '-i', ascii_file, '-o', temp_der_file],
                capture_output=True,
                text=True,
                check=True
            )
            
            with open(temp_der_file, 'rb') as f:
                der_data = f.read()
            print(f"✓ Converted to binary DER ({len(der_data)} bytes)")
        except FileNotFoundError:
            print(f"✗ Error: ascii2der not found. Please install it.")
            print(f"  On Ubuntu/Debian: sudo apt install asn1c")
            return False
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running ascii2der: {e.stderr}")
            return False
        
        # Step 3: Encode binary DER to base64
        print(f"[3/4] Encoding DER to base64...")
        try:
            with open(temp_der_file, 'rb') as f:
                der_data = f.read()
            base64_data = base64.b64encode(der_data).decode('ascii')
            print(f"✓ Encoded to base64 ({len(base64_data)} characters)")
        except Exception as e:
            print(f"✗ Error encoding to base64: {e}")
            return False
        
        # Step 4: Create EML file with proper headers
        print(f"[4/4] Creating EML file with headers...")
        try:
            eml_headers = ""
            
            # Try to extract headers from original EML if provided
            if original_eml and os.path.exists(original_eml):
                with open(original_eml, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if line.strip() == '':
                        break
                    eml_headers += line
            else:
                # Create default headers
                eml_headers = """From: sender.efail.upb@mail.de
To: efail.rub@mail.de
Subject: http://xxxxxxxx.ngrok.io
Date: Fri, 10 Jul 2024 18:00:00 +0100
MIME-Version: 1.0
Content-Type: application/pkcs7-mime; smime-type=enveloped-data; name=smime.p7m
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=smime.p7m
"""
            
            # Write EML file
            with open(eml_file, 'w') as f:
                f.write(eml_headers)
                f.write('\n')
                
                # Format base64 with line breaks (76 chars per line is standard)
                for i in range(0, len(base64_data), 76):
                    f.write(base64_data[i:i+76] + '\n')
            
            print(f"✓ Created EML file with proper format")
        except Exception as e:
            print(f"✗ Error creating EML file: {e}")
            return False
        finally:
            # Clean up temporary DER file
            if os.path.exists(temp_der_file):
                os.remove(temp_der_file)
        
        print(f"✓ Output saved to: {eml_file}")
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    # Define input and output files
    ascii_file = "readable.txt"
    eml_file = "modified.eml"
    original_eml = "encrypted.eml"
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        ascii_file = sys.argv[1]
    if len(sys.argv) > 2:
        eml_file = sys.argv[2]
    if len(sys.argv) > 3:
        original_eml = sys.argv[3]
    
    print("=" * 60)
    print("Readable ASCII to EML Converter")
    print("=" * 60)
    print(f"Input ASCII:  {ascii_file}")
    print(f"Output EML:   {eml_file}")
    if original_eml:
        print(f"Original EML (for headers): {original_eml}")
    print("-" * 60)
    
    # Perform conversion
    success = ascii_to_eml(ascii_file, eml_file, original_eml)
    
    if success:
        print("-" * 60)
        print("Preview of output EML (first 20 lines):")
        print("-" * 60)
        with open(eml_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 20:
                    print(line.rstrip())
                else:
                    print(f"\n... (rest of base64 payload)")
                    break
    
    sys.exit(0 if success else 1)
