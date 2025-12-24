"""
Builder Module - Markdown to EPUB/PDF conversion
Uses pypandoc for both EPUB and PDF generation
"""
import pypandoc
from pathlib import Path
import subprocess
import shutil
import os

# Check if pandoc is installed and add to PATH if needed
def check_pandoc():
    """Check if pandoc is installed on the system."""
    pandoc_path = shutil.which("pandoc")
    
    # If not found, try common installation locations on Windows
    if not pandoc_path:
        common_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Pandoc'),
            os.path.join(os.environ.get('ProgramFiles', ''), 'Pandoc'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Pandoc'),
        ]
        
        for path in common_paths:
            pandoc_exe = os.path.join(path, 'pandoc.exe')
            if os.path.exists(pandoc_exe):
                # Add to PATH for this session
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
                print(f"📍 Found Pandoc at: {path}")
                return True
        
        print("❌ Pandoc not found! Please install:")
        print("   Windows: winget install pandoc")
        print("   Or download from: https://pandoc.org/installing.html")
        return False
    
    return True



def build_epub(md_path: str, output_path: str = "output/final/result.epub", resource_path: str = "output/"):
    """
    Convert Markdown to EPUB using pypandoc.
    
    Args:
        md_path: Path to translated markdown file
        output_path: Path for output EPUB file
        resource_path: Path to resources (images folder)
    """
    if not check_pandoc():
        return None
        
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📚 Building EPUB: {output_path}")
    
    # Convert markdown to EPUB
    pypandoc.convert_file(
        md_path,
        'epub',
        outputfile=str(output_file),
        extra_args=[
            f'--resource-path={resource_path}',
            '--toc',  # Table of contents
            '--toc-depth=2',
        ]
    )
    
    print(f"✅ EPUB created: {output_file}")
    return str(output_file)


# CSS styling for PDF output embedded in HTML
PDF_STYLES = """
<style>
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12pt;
    line-height: 1.8;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    font-size: 24pt;
    color: #1a1a2e;
    margin-top: 2em;
    margin-bottom: 0.5em;
    page-break-before: always;
}

h1:first-of-type {
    page-break-before: avoid;
}

h2 {
    font-size: 18pt;
    color: #16213e;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    border-bottom: 2px solid #e94560;
    padding-bottom: 0.3em;
}

h3 {
    font-size: 14pt;
    color: #0f3460;
    margin-top: 1em;
}

p {
    margin-bottom: 1em;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}

code {
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', monospace;
    font-size: 10pt;
}

pre {
    background: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 10pt;
}

blockquote {
    border-left: 4px solid #e94560;
    margin-left: 0;
    padding-left: 1em;
    color: #555;
    font-style: italic;
}

ul, ol {
    margin-bottom: 1em;
    padding-left: 2em;
}

strong {
    color: #1a1a2e;
}
</style>
"""


def build_pdf(md_path: str, output_path: str = "output/final/result.pdf", resource_path: str = "output/"):
    """
    Convert Markdown to PDF using pypandoc.
    Uses pandoc's built-in PDF engine (requires LaTeX or wkhtmltopdf).
    Falls back to HTML output if PDF generation fails.
    
    Args:
        md_path: Path to translated markdown file
        output_path: Path for output PDF file
        resource_path: Path to resources (images folder)
    """
    if not check_pandoc():
        return None
        
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📄 Building PDF: {output_path}")
    
    try:
        # Try using pandoc directly to PDF (requires LaTeX like MiKTeX or TeX Live)
        pypandoc.convert_file(
            md_path,
            'pdf',
            outputfile=str(output_file),
            extra_args=[
                f'--resource-path={resource_path}',
                '--pdf-engine=xelatex',  # Better Unicode/Vietnamese support
                '-V', 'geometry:margin=2.5cm',
                '-V', 'mainfont:Segoe UI',
                '-V', 'CJKmainfont:Segoe UI',
            ]
        )
        print(f"✅ PDF created: {output_file}")
        return str(output_file)
        
    except Exception as e:
        print(f"⚠️ Direct PDF generation failed: {e}")
        print("   Falling back to HTML output...")
        
        # Fallback: Generate HTML instead
        html_path = output_file.with_suffix('.html')
        
        # Read markdown and convert to HTML
        html_content = pypandoc.convert_file(
            md_path,
            'html',
            extra_args=[f'--resource-path={resource_path}']
        )
        
        # Fix image paths: output/images/ -> ../images/ (relative to output/final/)
        html_content = html_content.replace('src="output/images/', 'src="../images/')
        html_content = html_content.replace("src='output/images/", "src='../images/")
        
        # Wrap with styling
        full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <title>Poker Book - Vietnamese Translation</title>
    {PDF_STYLES}
</head>
<body>
{html_content}
</body>
</html>
"""
        
        html_path.write_text(full_html, encoding='utf-8')
        print(f"✅ HTML created: {html_path}")
        print("   💡 Tip: Open HTML in browser and use Print -> Save as PDF")
        
        return str(html_path)


def build_html(md_path: str, output_path: str = "output/final/result.html", resource_path: str = "output/"):
    """
    Convert Markdown to styled HTML.
    This is useful when PDF generation is not available.
    
    Args:
        md_path: Path to translated markdown file
        output_path: Path for output HTML file
        resource_path: Path to resources (images folder)
    """
    if not check_pandoc():
        return None
        
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"🌐 Building HTML: {output_path}")
    
    # Convert markdown to HTML
    html_content = pypandoc.convert_file(
        md_path,
        'html',
        extra_args=[f'--resource-path={resource_path}']
    )
    
    # Fix image paths: output/images/ -> ../images/ (relative to output/final/)
    html_content = html_content.replace('src="output/images/', 'src="../images/')
    html_content = html_content.replace("src='output/images/", "src='../images/")
    
    # Wrap with styling
    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <title>Poker Book - Vietnamese Translation</title>
    {PDF_STYLES}
</head>
<body>
{html_content}
</body>
</html>
"""
    
    output_file.write_text(full_html, encoding='utf-8')
    print(f"✅ HTML created: {output_file}")
    
    return str(output_file)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python builder.py <markdown_file> [epub|pdf|html|all]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_type = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    if not Path(md_file).exists():
        print(f"❌ File not found: {md_file}")
        sys.exit(1)
    
    if output_type in ["epub", "all"]:
        build_epub(md_file)
    
    if output_type in ["pdf", "all"]:
        build_pdf(md_file)
    
    if output_type in ["html", "all"]:
        build_html(md_file)
