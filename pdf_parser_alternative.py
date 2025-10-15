"""
Alternative PDF parser using free libraries
Provides fallback options when LlamaParse credits are exhausted
"""

import os
import re
import base64
from typing import List, Dict, Optional
import google.generativeai as genai
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import io
import tempfile

class AlternativePDFParser:
    """Multi-method PDF parser with fallback options"""

    def __init__(self, gemini_api_key: str, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the parser with Gemini API

        Args:
            gemini_api_key: Google AI API key
            model_name: Gemini model to use
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model_name)

    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        text = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text.append(f"## Page {page_num + 1}\n\n{page.extract_text()}\n")

            return "\n".join(text)
        except Exception as e:
            return f"PyPDF2 extraction failed: {str(e)}"

    def extract_with_pdfplumber(self, pdf_path: str) -> Dict:
        """Extract text and tables using pdfplumber"""
        content = {
            "text": [],
            "tables": []
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        content["text"].append(f"## Page {i + 1}\n\n{page_text}\n")

                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            content["tables"].append({
                                "page": i + 1,
                                "data": table
                            })

            return content
        except Exception as e:
            return {"error": f"pdfplumber extraction failed: {str(e)}"}

    def extract_with_pymupdf(self, pdf_path: str, extract_images: bool = False) -> Dict:
        """Extract text and optionally images using PyMuPDF"""
        content = {
            "text": [],
            "images": []
        }

        try:
            pdf_document = fitz.open(pdf_path)

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Extract text
                text = page.get_text()
                content["text"].append(f"## Page {page_num + 1}\n\n{text}\n")

                # Extract images if requested
                if extract_images:
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        pix = fitz.Pixmap(pdf_document, xref)

                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            content["images"].append({
                                "page": page_num + 1,
                                "index": img_index,
                                "data": base64.b64encode(img_data).decode()
                            })
                        pix = None

            pdf_document.close()
            return content

        except Exception as e:
            return {"error": f"PyMuPDF extraction failed: {str(e)}"}

    def table_to_markdown(self, table_data: List[List[str]]) -> str:
        """Convert table data to Markdown format"""
        if not table_data or len(table_data) < 2:
            return ""

        markdown = []

        # Header row
        header = table_data[0]
        markdown.append("| " + " | ".join([str(cell) if cell else "" for cell in header]) + " |")
        markdown.append("|" + "---|" * len(header))

        # Data rows
        for row in table_data[1:]:
            markdown.append("| " + " | ".join([str(cell) if cell else "" for cell in row]) + " |")

        return "\n".join(markdown)

    def enhance_with_gemini(self, raw_text: str, task: str = "format") -> str:
        """
        Use Gemini to enhance extracted text

        Args:
            raw_text: Raw extracted text
            task: Type of enhancement (format, summarize, translate)
        """
        prompts = {
            "format": """
                Format the following text as clean Markdown:
                - Preserve all content
                - Add proper headers (##, ###) for sections
                - Format lists properly
                - Clean up spacing and line breaks
                - Preserve technical terms and numbers exactly

                Text:
                {text}
            """,
            "summarize": """
                Create a detailed summary of the following text in Markdown format:
                - Include all key points
                - Maintain section structure
                - Preserve important data and numbers
                - Use bullet points for clarity

                Text:
                {text}
            """,
            "medical": """
                Format this medical/scientific document as structured Markdown:
                - Identify and format sections (Abstract, Introduction, Methods, Results, Discussion)
                - Preserve all medical terminology exactly
                - Format data and statistics clearly
                - Extract key findings as bullet points

                Text:
                {text}
            """
        }

        try:
            prompt = prompts.get(task, prompts["format"]).format(text=raw_text[:10000])  # Limit text length
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini enhancement failed: {str(e)}\n\nOriginal text:\n{raw_text}"

    def parse_pdf_multimethod(self, pdf_path: str, methods: List[str] = None) -> str:
        """
        Parse PDF using multiple methods with fallbacks

        Args:
            pdf_path: Path to PDF file
            methods: List of methods to try ["pypdf2", "pdfplumber", "pymupdf"]
        """
        if methods is None:
            methods = ["pdfplumber", "pymupdf", "pypdf2"]

        results = []

        for method in methods:
            try:
                if method == "pypdf2":
                    text = self.extract_text_pypdf2(pdf_path)
                    results.append(("PyPDF2", text))

                elif method == "pdfplumber":
                    content = self.extract_with_pdfplumber(pdf_path)
                    if "error" not in content:
                        # Combine text and tables
                        text_parts = content["text"]

                        # Add tables as markdown
                        for table_info in content.get("tables", []):
                            table_md = self.table_to_markdown(table_info["data"])
                            if table_md:
                                text_parts.append(f"\n### Table (Page {table_info['page']})\n\n{table_md}\n")

                        text = "\n".join(text_parts)
                        results.append(("pdfplumber", text))

                elif method == "pymupdf":
                    content = self.extract_with_pymupdf(pdf_path, extract_images=False)
                    if "error" not in content:
                        text = "\n".join(content["text"])
                        results.append(("PyMuPDF", text))

            except Exception as e:
                print(f"Method {method} failed: {str(e)}")
                continue

        # Use the best result (usually the longest extraction)
        if results:
            best_method, best_text = max(results, key=lambda x: len(x[1]))

            # Try to enhance with Gemini if possible
            try:
                enhanced = self.enhance_with_gemini(best_text, task="medical")
                return f"# PDF Parsed with {best_method}\n\n{enhanced}"
            except:
                return f"# PDF Parsed with {best_method}\n\n{best_text}"

        return "Failed to extract content from PDF using all available methods."

    def ocr_pdf_pages(self, pdf_path: str, max_pages: int = 5) -> str:
        """
        Use OCR for scanned PDFs (converts pages to images and uses Gemini vision)

        Args:
            pdf_path: Path to PDF
            max_pages: Maximum pages to process (to avoid quota issues)
        """
        try:
            import fitz
            pdf_document = fitz.open(pdf_path)
            extracted_text = []

            for page_num in range(min(len(pdf_document), max_pages)):
                page = pdf_document[page_num]

                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")

                # Save temporarily and send to Gemini
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_file.write(img_data)
                    tmp_path = tmp_file.name

                try:
                    # Upload to Gemini for OCR
                    image = Image.open(tmp_path)
                    prompt = """
                    Extract all text from this image.
                    Format it as clean Markdown with proper structure.
                    Preserve all content including tables, formulas, and technical terms.
                    """

                    response = self.model.generate_content([prompt, image])
                    extracted_text.append(f"## Page {page_num + 1}\n\n{response.text}\n")

                finally:
                    os.unlink(tmp_path)

            pdf_document.close()
            return "\n".join(extracted_text)

        except Exception as e:
            return f"OCR extraction failed: {str(e)}"


def parse_pdf_with_fallbacks(pdf_path: str, gemini_api_key: str, model_name: str = "gemini-2.0-flash") -> str:
    """
    Main function to parse PDF with multiple fallback options

    Args:
        pdf_path: Path to PDF file
        gemini_api_key: Google AI API key
        model_name: Gemini model to use

    Returns:
        Parsed content as Markdown string
    """
    parser = AlternativePDFParser(gemini_api_key, model_name)

    # Try multiple extraction methods
    result = parser.parse_pdf_multimethod(pdf_path)

    # If extraction was poor, try OCR on first few pages
    if len(result) < 1000:
        print("Text extraction was minimal, trying OCR...")
        ocr_result = parser.ocr_pdf_pages(pdf_path, max_pages=3)
        if len(ocr_result) > len(result):
            result = ocr_result

    return result