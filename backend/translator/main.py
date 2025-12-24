"""
Main Entry Point - AI Book Translation Pipeline
Orchestrates: PDF Extraction → Translation → EPUB/PDF Build
"""
import argparse
from pathlib import Path

from extractor import extract_pdf_to_markdown
from ai_translator import translate_markdown
from builder import build_epub, build_pdf


def main():
    parser = argparse.ArgumentParser(
        description="AI Book Translation Pipeline - Poker Domain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Use default input/source.pdf
  python main.py -i mybook.pdf             # Specify input file
  python main.py -p openai                 # Use OpenAI instead of Gemini
  python main.py --skip-extract            # Skip extraction (use existing markdown)
  python main.py --skip-translate          # Skip translation (use existing translated.md)
        """
    )
    
    parser.add_argument(
        "--input", "-i", 
        default="input/source.pdf", 
        help="Input PDF file (default: input/source.pdf)"
    )
    parser.add_argument(
        "--output", "-o", 
        default="output", 
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--provider", "-p", 
        choices=["openai", "gemini"], 
        default=None,
        help="Translation provider (default: from .env or gemini)"
    )
    parser.add_argument(
        "--skip-extract", 
        action="store_true", 
        help="Skip PDF extraction step (use existing source.md)"
    )
    parser.add_argument(
        "--skip-translate", 
        action="store_true", 
        help="Skip translation step (use existing translated.md)"
    )
    parser.add_argument(
        "--epub-only", 
        action="store_true", 
        help="Only generate EPUB output"
    )
    parser.add_argument(
        "--pdf-only", 
        action="store_true", 
        help="Only generate PDF output"
    )
    
    args = parser.parse_args()
    
    # Setup paths
    output_dir = Path(args.output)
    input_dir = Path("input")
    temp_md_dir = output_dir / "temp_md"
    final_dir = output_dir / "final"
    
    # Ensure directories exist
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    temp_md_dir.mkdir(exist_ok=True)
    final_dir.mkdir(exist_ok=True)
    
    source_md_path = temp_md_dir / "source.md"
    translated_md_path = temp_md_dir / "translated.md"
    
    print("=" * 60)
    print("🎰 AI BOOK TRANSLATION PIPELINE - POKER DOMAIN")
    print("=" * 60)
    
    # ========== STEP 1: EXTRACTION ==========
    if not args.skip_extract:
        print("\n📖 STEP 1: Extracting PDF to Markdown...")
        print("-" * 40)
        
        if not Path(args.input).exists():
            print(f"❌ Error: Input file not found: {args.input}")
            print(f"   Please place your PDF in: {input_dir.absolute()}")
            return
        
        md_text = extract_pdf_to_markdown(args.input, str(output_dir))
        print(f"   Extracted {len(md_text):,} characters")
    else:
        print("\n⏭️  STEP 1: Skipping extraction (using existing markdown)")
        if source_md_path.exists():
            md_text = source_md_path.read_text(encoding="utf-8")
        else:
            print(f"❌ Error: source.md not found at {source_md_path}")
            return
    
    # ========== STEP 2: TRANSLATION ==========
    if not args.skip_translate:
        print("\n🌐 STEP 2: Translating to Vietnamese...")
        print("-" * 40)
        
        translated_text = translate_markdown(
            md_text, 
            provider=args.provider,
            output_dir=str(output_dir)
        )
        print(f"   Translated {len(translated_text):,} characters")
    else:
        print("\n⏭️  STEP 2: Skipping translation (using existing translated.md)")
        if not translated_md_path.exists():
            print(f"❌ Error: translated.md not found at {translated_md_path}")
            return
    
    # ========== STEP 3: BUILD OUTPUTS ==========
    print("\n📚 STEP 3: Building final documents...")
    print("-" * 40)
    
    epub_path = str(final_dir / "result.epub")
    pdf_path = str(final_dir / "result.pdf")
    
    if not args.pdf_only:
        build_epub(str(translated_md_path), epub_path, str(output_dir) + "/")
    
    if not args.epub_only:
        build_pdf(str(translated_md_path), pdf_path, str(output_dir) + "/")
    
    # ========== DONE ==========
    print("\n" + "=" * 60)
    print("🎉 TRANSLATION COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output files:")
    
    if not args.pdf_only and Path(epub_path).exists():
        print(f"   📘 EPUB: {epub_path}")
    if not args.epub_only and Path(pdf_path).exists():
        print(f"   📕 PDF:  {pdf_path}")
    
    print(f"\n📂 All files saved in: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
