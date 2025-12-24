"""
Image Filter Module - Remove advertisement images from translated content
Filters out promotional content like QR codes, "More Free Book", "Listen It" banners, etc.
"""
import re
from pathlib import Path


# Patterns to identify advertisement content
AD_IMAGE_PATTERNS = [
    r'-full\.png',           # Full page ads typically named with "-full.png"
    r'-\d+-1\.png',          # Second image on a page often is an ad banner
]

# Text patterns that indicate surrounding content is promotional
AD_TEXT_PATTERNS = [
    r'Install Bookey App',
    r'Unlock Full Text',
    r'Scan to Download',
    r'More Free Book',
    r'Listen It',
    r'bookey\.app',
]


def is_ad_image(image_path: str) -> bool:
    """Check if an image path matches advertisement patterns."""
    for pattern in AD_IMAGE_PATTERNS:
        if re.search(pattern, image_path):
            return True
    return False


def filter_ad_images_from_markdown(md_text: str, aggressive: bool = False) -> str:
    """
    Remove advertisement images from markdown content.
    
    Args:
        md_text: The markdown text to filter
        aggressive: If True, also remove images that appear near ad-related text
        
    Returns:
        Filtered markdown text
    """
    lines = md_text.split('\n')
    filtered_lines = []
    skip_next_image = False
    removed_count = 0
    
    for i, line in enumerate(lines):
        # Check for ad-related text patterns
        is_ad_text = any(re.search(pattern, line, re.IGNORECASE) for pattern in AD_TEXT_PATTERNS)
        
        if is_ad_text:
            if aggressive:
                skip_next_image = True
            # Skip ad-related text lines entirely
            continue
        
        # Check if this line contains an image
        image_match = re.search(r'!\[.*?\]\((.*?)\)', line)
        
        if image_match:
            image_path = image_match.group(1)
            
            # Skip if this is an advertisement image
            if is_ad_image(image_path):
                removed_count += 1
                continue
            
            # Skip if previous line flagged this as ad content
            if skip_next_image:
                skip_next_image = False
                removed_count += 1
                continue
        
        filtered_lines.append(line)
    
    print(f"🧹 Removed {removed_count} advertisement images/text")
    return '\n'.join(filtered_lines)


def filter_ad_images_from_html(html_text: str) -> str:
    """
    Remove advertisement images from HTML content.
    
    Args:
        html_text: The HTML text to filter
        
    Returns:
        Filtered HTML text
    """
    removed_count = 0
    
    # Remove img tags that match ad patterns
    for pattern in AD_IMAGE_PATTERNS:
        matches = re.findall(rf'<img[^>]*src="[^"]*{pattern}[^"]*"[^>]*/>', html_text)
        removed_count += len(matches)
        html_text = re.sub(rf'<p>\s*<img[^>]*src="[^"]*{pattern}[^"]*"[^>]*/>\s*</p>', '', html_text)
        html_text = re.sub(rf'<img[^>]*src="[^"]*{pattern}[^"]*"[^>]*/>', '', html_text)
    
    # Remove paragraphs containing ad-related text
    for pattern in AD_TEXT_PATTERNS:
        html_text = re.sub(rf'<p>[^<]*{pattern}[^<]*</p>', '', html_text, flags=re.IGNORECASE)
        html_text = re.sub(rf'<h3[^>]*>[^<]*{pattern}[^<]*</h3>', '', html_text, flags=re.IGNORECASE)
    
    print(f"🧹 Removed {removed_count} advertisement images from HTML")
    return html_text


def process_translated_markdown(input_path: str, output_path: str = None) -> str:
    """
    Process a translated markdown file to remove advertisements.
    
    Args:
        input_path: Path to the translated markdown file
        output_path: Optional path to save filtered content (defaults to overwrite input)
        
    Returns:
        Filtered markdown content
    """
    if output_path is None:
        output_path = input_path
    
    print(f"📄 Processing: {input_path}")
    
    md_text = Path(input_path).read_text(encoding='utf-8')
    filtered_text = filter_ad_images_from_markdown(md_text, aggressive=True)
    
    Path(output_path).write_text(filtered_text, encoding='utf-8')
    print(f"✅ Saved filtered content to: {output_path}")
    
    return filtered_text


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ad_filter.py <markdown_file> [output_file]")
        print("       python ad_filter.py output/temp_md/translated.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    process_translated_markdown(input_file, output_file)
