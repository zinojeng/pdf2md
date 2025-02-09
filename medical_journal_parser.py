from llama_parse import LlamaParse
from llama_index.core.schema import TextNode
from typing import List
import json
import os

# Initialize parser with medical-specific instructions
def initialize_parser():
    parsing_instruction = """
    You are parsing a medical journal article. Pay special attention to:
    1. Tables - extract all data into markdown tables with proper headers
    2. Figures - describe each figure in detail including axes, data points, and trends
    3. References - extract all references in proper citation format
    4. Sections - maintain proper section hierarchy (Abstract, Introduction, Methods, Results, Discussion)
    5. Medical terms - preserve exact terminology and units
    6. Equations - convert to proper markdown math notation
    """
    
    return LlamaParse(
        result_type="markdown",
        use_vendor_multimodal_model=True,
        vendor_multimodal_model_name="gemini-2.0-flash",
        parsing_instruction=parsing_instruction,
        invalidate_cache=True
    )

def process_pdf(pdf_path, output_dir):
    # Initialize parser
    parser = initialize_parser()
    
    # Parse PDF
    print(f"Processing {pdf_path}...")
    json_objs = parser.get_json_result(pdf_path)
    json_list = json_objs[0]["pages"]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save parsed content
    output_path = os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', '.md'))
    with open(output_path, 'w') as f:
        for page in json_list:
            f.write(page['md'])
            f.write('\n\n')
    
    print(f"Saved parsed content to {output_path}")

def batch_process_pdfs(pdf_dir, output_dir):
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            process_pdf(pdf_path, output_dir)

if __name__ == "__main__":
    # Configuration
    PDF_DIR = "medical_journals"  # Directory containing PDFs
    OUTPUT_DIR = "parsed_journals"  # Directory to save markdown files
    
    # Process all PDFs in directory
    batch_process_pdfs(PDF_DIR, OUTPUT_DIR) 