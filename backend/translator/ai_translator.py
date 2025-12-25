"""
AI Translator Module - Chunking and LLM Translation
Handles splitting markdown and translating with OpenAI/Gemini
"""
import os
import re
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# System prompt với thuật ngữ Poker theo đúng file plan
TRANSLATION_SYSTEM_PROMPT = """You are a professional Poker player and translator. Translate the following Markdown content from English to Vietnamese.

CRITICAL RULES:
1. OUTPUT ONLY THE VIETNAMESE TRANSLATION. Do NOT include the original English text.
2. Do NOT output both English and Vietnamese versions. Only Vietnamese.
3. Replace ALL English text with Vietnamese, except for poker terminology listed below.

FORMATTING RULES:
4. Keep all Markdown syntax strictly unchanged (especially ![]() image links, **bold**, headers).
5. Do not translate code blocks or URLs.
6. Maintain natural Vietnamese reading flow.

POKER TERMINOLOGY (Keep Original):
   - 'Hand' -> 'Hand bài' (not 'bàn tay')
   - 'Fold' -> 'Fold' or 'Bỏ bài' (not 'Gấp')
   - 'Bet' -> 'Bet' or 'Cược'
   - 'Range' -> 'Range' or 'Khoảng bài'
   - 'Bluff' -> 'Bluff'
   - 'All-in' -> 'All-in'
   - 'Pot' -> 'Pot'
   - 'Stack' -> 'Stack'
   - 'Check' -> 'Check'
   - 'Call' -> 'Call' or 'Theo'
   - 'Raise' -> 'Raise' or 'Tăng'
   - 'Flop', 'Turn', 'River' -> Keep original

REMEMBER: Your output should be 100% Vietnamese (except poker terms). No English sentences should remain."""


def chunk_by_headers(md_text: str, max_chars: int = 4000) -> list[str]:
    """
    Split markdown by headers (# or ##) or by character count.
    Strategy: Split by Headers (#, ##) or generic character count (~2000 words/chunk)
    """
    # Split by major headers
    header_pattern = r'(^#{1,2}\s+.+$)'
    sections = re.split(header_pattern, md_text, flags=re.MULTILINE)
    
    chunks = []
    current_chunk = ""
    
    for section in sections:
        if not section.strip():
            continue
            
        # If adding this section exceeds max_chars, save current and start new
        if len(current_chunk) + len(section) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = section
        else:
            current_chunk += section
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # If chunks are still too large, split further by paragraphs
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chars:
            # Split by double newlines (paragraphs)
            paragraphs = chunk.split('\n\n')
            sub_chunk = ""
            for para in paragraphs:
                if len(sub_chunk) + len(para) > max_chars and sub_chunk:
                    final_chunks.append(sub_chunk.strip())
                    sub_chunk = para + "\n\n"
                else:
                    sub_chunk += para + "\n\n"
            if sub_chunk.strip():
                final_chunks.append(sub_chunk.strip())
        else:
            final_chunks.append(chunk)
    
    return final_chunks


def translate_with_openai(text: str) -> str:
    """Translate text using OpenAI GPT-4o-mini"""
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.3  # Lower temperature for more consistent translations
    )
    
    return response.choices[0].message.content


def translate_with_gemini(text: str, max_retries: int = 3) -> tuple[str, dict]:
    """
    Translate text using Google Gemini Flash (cost-effective for long books)
    
    Returns:
        tuple: (translated_text, token_stats)
        token_stats contains: input_tokens, output_tokens, total_tokens
    """
    import google.generativeai as genai
    import time
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Combine system prompt with user content
    full_prompt = f"{TRANSLATION_SYSTEM_PROMPT}\n\n---\n\nContent to translate:\n\n{text}"
    
    token_stats = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(full_prompt)
            
            # Extract token usage if available
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                token_stats = {
                    "input_tokens": getattr(usage, 'prompt_token_count', 0),
                    "output_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0),
                }
            
            return response.text, token_stats
        except Exception as e:
            error_str = str(e)
            # Check if it's a rate limit error (429)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                wait_time = (2 ** attempt) * 30  # 30s, 60s, 120s
                print(f"\n⏳ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                raise e
    
    # If all retries failed, raise the last error
    raise Exception(f"Failed after {max_retries} retries due to rate limiting")


def translate_markdown(md_text: str, provider: str = None, output_dir: str = "output") -> str:
    """
    Translate full markdown document.
    
    Args:
        md_text: Source markdown text
        provider: 'openai' or 'gemini' (defaults to env var or gemini)
        output_dir: Output directory for saving results
        
    Returns:
        Translated markdown text
    """
    # Determine provider
    if provider is None:
        provider = os.getenv("TRANSLATION_PROVIDER", "gemini").lower()
    
    print(f"🌐 Using translation provider: {provider}")
    
    # Select translation function
    translate_fn = translate_with_gemini if provider == "gemini" else translate_with_openai
    
    # Chunk the markdown
    chunks = chunk_by_headers(md_text)
    print(f"📦 Split into {len(chunks)} chunks for translation")
    
    translated_chunks = []
    
    # Token tracking
    total_tokens = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    
    # Translate each chunk with progress bar
    for i, chunk in enumerate(tqdm(chunks, desc="Translating")):
        try:
            if provider == "gemini":
                translated, token_stats = translate_fn(chunk)
                # Accumulate token usage
                total_tokens["input_tokens"] += token_stats.get("input_tokens", 0)
                total_tokens["output_tokens"] += token_stats.get("output_tokens", 0)
                total_tokens["total_tokens"] += token_stats.get("total_tokens", 0)
            else:
                translated = translate_fn(chunk)
            translated_chunks.append(translated)
        except Exception as e:
            print(f"\n⚠️ Error translating chunk {i+1}: {e}")
            # Keep original if translation fails
            translated_chunks.append(chunk)
    
    # Join all translated chunks
    full_translation = "\n\n".join(translated_chunks)
    
    # Save translated markdown
    output_path = Path(output_dir) / "temp_md"
    output_path.mkdir(parents=True, exist_ok=True)
    
    translated_file = output_path / "translated.md"
    translated_file.write_text(full_translation, encoding="utf-8")
    print(f"✅ Translation saved: {translated_file}")
    print(f"   Translated {len(full_translation):,} characters")
    
    # Display token usage report
    if provider == "gemini" and total_tokens["total_tokens"] > 0:
        print(f"\n📊 TOKEN USAGE REPORT")
        print(f"   ├─ Input tokens:  {total_tokens['input_tokens']:,}")
        print(f"   ├─ Output tokens: {total_tokens['output_tokens']:,}")
        print(f"   └─ Total tokens:  {total_tokens['total_tokens']:,}")
        
        # Gemini Flash pricing (as of Dec 2024): $0.075/1M input, $0.30/1M output
        # For prompts <= 128K tokens
        input_cost = (total_tokens["input_tokens"] / 1_000_000) * 0.075
        output_cost = (total_tokens["output_tokens"] / 1_000_000) * 0.30
        total_cost = input_cost + output_cost
        
        print(f"\n💰 ESTIMATED COST (Gemini 2.0 Flash)")
        print(f"   ├─ Input:  ${input_cost:.4f}")
        print(f"   ├─ Output: ${output_cost:.4f}")
        print(f"   └─ Total:  ${total_cost:.4f}")
    
    # Auto post-processing to remove any duplicate English content
    try:
        from post_processor import remove_duplicate_english, clean_table_of_contents
        print(f"\n🧹 Running post-processor to clean duplicates...")
        cleaned = remove_duplicate_english(full_translation)
        if len(cleaned) < len(full_translation):
            full_translation = cleaned
            translated_file.write_text(full_translation, encoding="utf-8")
            print(f"   ✅ Cleaned and saved")
        else:
            print(f"   ✅ No duplicates found")
        
        # Clean Table of Contents formatting
        print(f"🧹 Cleaning Table of Contents formatting...")
        cleaned = clean_table_of_contents(full_translation)
        if cleaned != full_translation:
            full_translation = cleaned
            translated_file.write_text(full_translation, encoding="utf-8")
            print(f"   ✅ ToC cleaned")
    except ImportError:
        pass  # post_processor not available, skip
    
    return full_translation


if __name__ == "__main__":
    # Test translation with a sample text
    sample = """# Introduction to Poker

When you're dealt a strong **hand**, you have several options. You can **fold** if you're not confident, **bet** to build the pot, or **check** to see more cards for free.

Understanding your **range** is crucial. A good player knows when to **bluff** and when to play straightforward.

## Pre-flop Strategy

Your position at the table matters. Being on the button gives you the advantage of acting last."""

    print("Testing translation...")
    result = translate_markdown(sample, provider="gemini")
    print("\n--- Translated Result ---")
    print(result[:500] + "..." if len(result) > 500 else result)
