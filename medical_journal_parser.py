from llama_parse import LlamaParse
from llama_index.core.schema import TextNode
from typing import List
import json
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def initialize_parser():
    # 醫療期刊解析指令
    content_guideline = """
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
        vendor_multimodal_model_name="gemini-2.5-pro",  # 使用 Gemini 2.5 Pro
        content_guideline_instruction=content_guideline,  # 使用新的指令參數
        invalidate_cache=True
    )

def process_pdf(pdf_path, output_dir):
    try:
        # Initialize parser
        parser = initialize_parser()
        
        # Parse PDF
        print(f"Processing {pdf_path}...")
        json_objs = parser.get_json_result(pdf_path)
        
        if not json_objs or len(json_objs) == 0:
            raise ValueError("No content parsed from PDF")
            
        json_list = json_objs[0]["pages"]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save parsed content
        output_path = os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', '.md'))
        with open(output_path, 'w', encoding='utf-8') as f:
            for page in json_list:
                f.write(page['md'])
                f.write('\n\n')
        
        print(f"Saved parsed content to {output_path}")
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")

def batch_process_pdfs(pdf_dir, output_dir):
    if not os.path.exists(pdf_dir):
        print(f"Error: Directory '{pdf_dir}' does not exist")
        return
        
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            process_pdf(pdf_path, output_dir)

if __name__ == "__main__":
    # Configuration
    PDF_DIR = "medical_journals"  # Directory containing PDFs
    OUTPUT_DIR = "parsed_journals"  # Directory to save markdown files
    
    # Create directories if they don't exist
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Process all PDFs in directory
    batch_process_pdfs(PDF_DIR, OUTPUT_DIR) 