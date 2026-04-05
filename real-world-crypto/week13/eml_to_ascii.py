#!/usr/bin/env python3
"""
Script 1: Convert encrypted.eml to readable ASCII format
Pipeline: EML (base64) → Binary DER → Readable ASCII
"""

import subprocess
import sys
import os
import base64

def eml_to_ascii(input_file, output_file):
    """
    Complete pipeline to convert encrypted.eml to readable ASCII format
    
    Steps:
    1. Extract base64 content from EML (skip headers)
    2. Decode base64 to binary DER
    3. Convert binary DER to readable ASCII format
    
    Args:
        input_file: Path to the input encrypted.eml file
        output_file: Path to the output ASCII file
    """
    
    try:
        # Step 1: Check if input file exists
        if not os.path.exists(input_file):
            print(f"✗ Error: Input file '{input_file}' not found")
            return False
        
        print(f"[1/3] Reading {input_file}...")
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        # Find where base64 content starts (after headers and blank line)
        base64_start = None
        for i, line in enumerate(lines):
            if line.strip() == '':
                base64_start = i + 1
                break
        
        if base64_start is None:
            print(f"✗ Error: Could not find base64 content in EML file")
            return False
        
        # Extract base64 content (continuous lines without email headers)
        base64_content = ''.join([line.rstrip('\n') for line in lines[base64_start:]])
        print(f"✓ Extracted base64 content ({len(base64_content)} characters)")
        
        # Step 2: Decode base64 to binary DER
        print(f"[2/3] Decoding base64 to binary DER format...")
        try:
            der_data = base64.b64decode(base64_content)
            temp_der_file = 'temp_encrypted.der'
            with open(temp_der_file, 'wb') as f:
                f.write(der_data)
            print(f"✓ Decoded to binary DER ({len(der_data)} bytes)")
        except Exception as e:
            print(f"✗ Error decoding base64: {e}")
            return False
        
        # Step 3: Convert binary DER to readable ASCII
        print(f"[3/3] Converting DER to readable ASCII format...")
        try:
            with open(output_file, 'w') as out:
                result = subprocess.run(
                    ['der2ascii', '-i', temp_der_file, '-o', output_file],
                    capture_output=True,
                    text=True,
                    check=True
                )
            print(f"✓ Successfully converted to ASCII")
        except FileNotFoundError:
            # Fallback to openssl
            try:
                with open(output_file, 'w') as out:
                    result = subprocess.run(
                        ['openssl', 'asn1parse', '-in', temp_der_file, '-inform', 'DER', '-i'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    out.write(result.stdout)
                print(f"✓ Successfully converted to ASCII (using openssl)")
            except Exception as e:
                print(f"✗ Error: {e}")
                return False
        finally:
            # Clean up temporary DER file
            if os.path.exists(temp_der_file):
                os.remove(temp_der_file)
        
        print(f"✓ Output saved to: {output_file}")
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    # Define input and output files
    input_file = "encrypted.eml"
    output_file = "readable.txt"
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print("=" * 60)
    print("EML to Readable ASCII Converter")
    print("=" * 60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print("-" * 60)
    
    # Perform conversion
    success = eml_to_ascii(input_file, output_file)
    
    if success:
        print("-" * 60)
        print("Preview (first 30 lines):")
        print("-" * 60)
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i < 30:
                    print(line.rstrip())
                else:
                    remaining = sum(1 for _ in f) + 1
                    print(f"\n... ({remaining} more lines)")
                    break
    
    sys.exit(0 if success else 1)
