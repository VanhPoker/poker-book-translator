"""
Post-processing script to remove duplicate English content that appears before Vietnamese translations.
This happens when the LLM returns both original and translated content.
"""
import re
from pathlib import Path


def remove_duplicate_english(md_text: str) -> str:
    """
    Remove duplicate English content that appears before Vietnamese translations.
    This detects patterns where English Quiz sections are followed by Vietnamese versions.
    """
    lines = md_text.split('\n')
    
    # Find the position where Vietnamese Quiz sections start
    # Pattern: "#### **Chapter X |" appearing twice (English then Vietnamese)
    
    # Track chapter quiz headers
    quiz_header_pattern = r'####.*Chapter \d+.*Quiz and Test'
    
    english_sections = []
    current_section_start = None
    in_quiz_section = False
    vietnamese_marker = None
    
    for i, line in enumerate(lines):
        if re.search(quiz_header_pattern, line):
            if current_section_start is None:
                # First occurrence - might be English
                current_section_start = i
                in_quiz_section = True
            else:
                # Second occurrence - this is Vietnamese, mark English section for removal
                # Check if the new section has Vietnamese content
                if i + 2 < len(lines):
                    next_content = ' '.join(lines[i:min(i+5, len(lines))])
                    # Check for Vietnamese characters
                    if re.search(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', next_content, re.IGNORECASE):
                        # This is Vietnamese section, remove everything from current_section_start to i-1
                        english_sections.append((current_section_start, i - 1))
                current_section_start = None
                in_quiz_section = False
    
    # Remove marked English sections (in reverse order to maintain line numbers)
    if english_sections:
        new_lines = lines.copy()
        for start, end in reversed(english_sections):
            print(f"🧹 Removing duplicate English section: lines {start+1}-{end+1}")
            del new_lines[start:end+1]
        return '\n'.join(new_lines)
    
    return md_text


def clean_table_of_contents(md_text: str) -> str:
    """
    Clean up Table of Contents (ToC) formatting from PDF extraction.
    - Removes excessive dot leaders (...........)
    - Fixes page number formatting
    - Cleans up broken lines
    """
    lines = md_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Pattern: text followed by dots and page number
        # Example: "Chương Một: Poker Cơ Bản .......................... 1"
        
        # Replace 3+ consecutive dots with proper formatting
        # Keep format: "Title ... PageNum"
        cleaned_line = re.sub(r'\.{4,}', ' ... ', line)
        
        # Remove excessive dots followed by numbers (ToC pattern)
        # Pattern: "text.....9 More text.....12"
        cleaned_line = re.sub(r'\.{2,}(\d+)\s*', r' (\1) ', cleaned_line)
        
        # Clean up multiple spaces
        cleaned_line = re.sub(r'\s{3,}', '  ', cleaned_line)
        
        # If line is mostly dots (more than 50%), skip it
        if len(line) > 0:
            dot_ratio = line.count('.') / len(line)
            if dot_ratio > 0.5:
                continue
        
        cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines)



def clean_translated_markdown(input_path: str, output_path: str = None) -> str:
    """
    Clean translated markdown by removing duplicate English content.
    """
    if output_path is None:
        output_path = input_path
    
    print(f"📄 Cleaning: {input_path}")
    
    md_text = Path(input_path).read_text(encoding='utf-8')
    original_len = len(md_text)
    
    cleaned_text = remove_duplicate_english(md_text)
    new_len = len(cleaned_text)
    
    if new_len < original_len:
        removed_chars = original_len - new_len
        print(f"✅ Removed {removed_chars:,} characters of duplicate content")
    else:
        print("ℹ️ No duplicate English content found")
    
    Path(output_path).write_text(cleaned_text, encoding='utf-8')
    print(f"✅ Saved to: {output_path}")
    
    return cleaned_text


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python post_processor.py <markdown_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    clean_translated_markdown(input_file, output_file)
