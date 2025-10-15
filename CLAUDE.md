# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multimodal PDF-to-Markdown parser that combines LlamaParse with Gemini 2.5 series models. It provides both a CLI tool for batch processing and an interactive Streamlit web interface with model selection capabilities. The parser is optimized for technical documents, especially medical and scientific literature.

## Environment Setup

**Required API Keys** (stored in `.env`):
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- `LLAMA_CLOUD_API_KEY` - Get from [LlamaCloud](https://cloud.llamaindex.ai/)

**Virtual Environment**:
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

**Install Dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

**Quick Start** (recommended):
```bash
./run.sh
```
This unified script will:
- Check Python version (≥3.10 required)
- Create/activate virtual environment
- Install all dependencies (including MarkItDown)
- Show interactive menu to choose version
- Launch selected application

**Command Line Options**:
```bash
./run.sh              # Show interactive menu
./run.sh --smart      # Launch Smart Fallback version (recommended)
./run.sh --fixed      # Launch Fixed version
./run.sh --enhanced   # Launch Enhanced version
./run.sh --original   # Launch Original version
./run.sh --batch      # Run batch processing
./run.sh --help       # Show help
```

**Manual Start - Specific Versions**:
```bash
source venv/bin/activate

# Smart Fallback version with MarkItDown (recommended)
streamlit run streamlit_app_with_markitdown.py

# Fixed version with optimized prompts
streamlit run streamlit_app_fixed.py

# Enhanced version with multiple parsers
streamlit run streamlit_app_enhanced.py

# Original version
streamlit run streamlit_app.py
```

**CLI Batch Processing**:
```bash
./run.sh --batch
# or manually:
source venv/bin/activate
python medical_journal_parser.py
```
This processes all PDFs in `medical_journals/` directory and outputs to `parsed_journals/`.

## Architecture

### Core Components

**medical_journal_parser.py** - Core parsing logic
- `initialize_parser()`: Configures LlamaParse with Gemini 2.5 Pro and document-specific parsing instructions
- `process_pdf(pdf_path, output_dir)`: Parses a single PDF to Markdown
- `batch_process_pdfs(pdf_dir, output_dir)`: Processes all PDFs in a directory
- Default model: `gemini-2.5-pro`

**Application Versions**:

1. **streamlit_app_with_markitdown.py** - Smart Fallback version (recommended)
   - Integrates Microsoft MarkItDown as fallback parser
   - Three parsing modes: Smart mode, LlamaParse priority, MarkItDown local-only
   - Automatic fallback when LlamaParse encounters errors
   - No API required for MarkItDown mode

2. **streamlit_app_fixed.py** - Fixed version
   - Optimized prompts to avoid recitation policy errors
   - Uses Gemini 2.0 Flash by default
   - Enhanced error handling with user-friendly messages

3. **streamlit_app_enhanced.py** - Enhanced version
   - Multiple local PDF parsers (PyPDF2, pdfplumber, PyMuPDF)
   - Smart error handling and retry mechanism
   - Chunked processing for large files

4. **streamlit_app.py** - Original version
   - Basic LlamaParse functionality
   - Model selection: Gemini 2.5 Pro, Flash, or Flash Lite

**run.sh** - Unified launcher script
- Checks Python version (≥3.10 required)
- Creates/activates virtual environment
- Installs all dependencies including MarkItDown
- Interactive menu for version selection
- Command-line options for direct launching

### Document Parsing Guidelines

The parser uses specific content guidelines optimized for technical documents:
1. **Tables** - Extracted as Markdown tables with proper headers and cell alignment
2. **Figures** - Detailed descriptions including axes labels, data points, and visual trends
3. **References** - Extracted in proper citation format
4. **Sections** - Maintains document hierarchy (Abstract, Introduction, Methods, Results, Discussion, etc.)
5. **Technical terms** - Preserves exact terminology, units, and scientific notation
6. **Equations** - Converts to Markdown math notation (LaTeX format)

### Available Gemini Models

Users can select from three Gemini 2.5 models in the Streamlit interface:

- **gemini-2.5-pro**: Highest quality, best for complex documents requiring maximum accuracy
- **gemini-2.5-flash**: Balanced speed and quality, suitable for most documents
- **gemini-2.5-flash-lite**: Fastest processing, ideal for simple documents or rapid iteration

### Directory Structure

- `medical_journals/` - Input PDFs for batch processing
- `parsed_journals/` - Output Markdown files from batch processing
- `temp_uploads/` - Temporary storage for Streamlit uploads (auto-cleaned)
- `parsed_results/` - Temporary output for Streamlit (auto-cleaned)

## Key Technical Details

**LlamaParse Configuration**:
- Supports Gemini 2.5 series models (Pro, Flash, Flash Lite)
- Result type: Markdown
- Cache invalidation enabled for fresh parsing on each run
- Custom content guidelines for technical/medical documents
- Uses `use_vendor_multimodal_model=True` for Gemini integration

**API Integration**:
- Gemini 2.5 models provide multimodal vision and parsing capabilities
- LlamaParse orchestrates the document processing pipeline
- Environment variables loaded via `python-dotenv` from `.env` file
- API keys can also be entered directly in Streamlit interface

**Streamlit Implementation**:
- Model selection dynamically updates the parser configuration
- Progress indicators using `st.spinner()` for UX feedback
- Temporary file management with automatic cleanup in `finally` block
- Session-based file storage prevents conflicts

## Modifying Parsing Behavior

**CLI Tool** (`medical_journal_parser.py`):
- Modify `content_guideline` in `initialize_parser()` function
- Change model by updating `vendor_multimodal_model_name` parameter
- Current default: `gemini-2.5-pro`

**Streamlit App** (`streamlit_app.py`):
- Users select model via dropdown (no code changes needed)
- To modify parsing guidelines: edit `content_guideline` string in the parsing function (around line 134)
- To add new models: update the `options` list in `st.sidebar.selectbox()` (line 34-38)
