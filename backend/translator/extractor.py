"""
Extractor Module - PDF to Markdown using pymupdf4llm
Handles PDF extraction and image extraction to output/images/
"""
import pymupdf4llm
from pathlib import Path


def extract_pdf_to_markdown(pdf_path: str, output_dir: str = "output") -> str:
    """
    Convert PDF to Markdown with images extracted.
    
    Args:
        pdf_path: Path to source PDF file
        output_dir: Output directory for images and markdown
        
    Returns:
        Markdown text content
    """
    # Ensure output directories exist
    output_path = Path(output_dir)
    image_path = output_path / "images"
    temp_md_path = output_path / "temp_md"
    
    image_path.mkdir(parents=True, exist_ok=True)
    temp_md_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📖 Extracting PDF: {pdf_path}")
    print(f"📁 Images will be saved to: {image_path}")
    
    # Use pymupdf4llm to convert PDF to markdown
    # This automatically extracts images and creates proper markdown links
    md_text = pymupdf4llm.to_markdown(
        pdf_path, 
        write_images=True, 
        image_path=str(image_path)
    )
    
    # Save extracted markdown to temp file
    source_md = temp_md_path / "source.md"
    source_md.write_text(md_text, encoding="utf-8")
    print(f"✅ Markdown extracted: {source_md}")
    
    return md_text


if __name__ == "__main__":
    # Test extraction with input/source.pdf
    import sys
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "input/source.pdf"
    
    if Path(pdf_file).exists():
        md_content = extract_pdf_to_markdown(pdf_file)
        print(f"\n📄 Extracted {len(md_content)} characters of markdown")
    else:
        print(f"❌ File not found: {pdf_file}")
        print("Usage: python extractor.py [path_to_pdf]")
