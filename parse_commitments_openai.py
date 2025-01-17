import os
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
import json
import pandas as pd

###############################################################################
# CONFIGURATION
###############################################################################
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Select which OpenAI model to use ("gpt-4", or "gpt-3.5-turbo" for lower cost)
OPENAI_MODEL = "gpt-4"

# For large PDFs, we chunk the text to avoid exceeding GPT token limits
MAX_TOKENS_PER_CHUNK = 3000  # rough ~3000 tokens worth of text per chunk

###############################################################################
# 1) EXTRACT TEXT FROM PDF
###############################################################################
def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Extract all textual pages from a PDF using pdfplumber
    and return a single consolidated string.
    """
    all_text = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                all_text.append(page_text)
    return "\n".join(all_text)


###############################################################################
# 2) SPLIT TEXT INTO CHUNKS
###############################################################################
def chunk_text(text: str, max_tokens: int = 2000) -> list:
    """
    Splits the extracted text into manageable chunks based on
    an approximate token-to-character ratio (~1 token = ~4 chars).
    """
    approx_char_limit = max_tokens * 4
    chunks = []
    start = 0
    while start < len(text):
        end = start + approx_char_limit
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks


###############################################################################
# 3) GPT CLASSIFICATION PROMPT
###############################################################################
def classify_text_with_gpt(text_chunk: str) -> str:
    """
    Sends text_chunk to GPT-4 with instructions to classify references
    according to the two taxonomies: forward-looking (Taxonomy A) 
    and past references (Taxonomy B).

    Expects GPT to return a JSON array of objects, where each object might be:
    {
      "statement": "...some snippet...",
      "taxonomyA": [ { "category": 3, "explanation": "..."} ],
      "taxonomyB": [ { "category": 2, "explanation": "..."} ]
    }

    Or an empty list if no relevant references are found.
    """
    # Taxonomy instructions to embed in the prompt:
    taxonomy_instructions = """
TAXONOMY A: PRESENT/FUTURE COMMITMENTS
1) No Mention
2) Generic/High-Level Commitment
3) Specific Numeric Target
4) Net-Zero or Carbon-Neutral Target
5) Detailed Plan or Roadmap
6) Science-Based or External Framework Commitment

TAXONOMY B: REFERENCES TO PAST COMMITMENTS
1) No Past Commitment Mentioned
2) Mention of Past Commitment (Status Unknown)
3) Acknowledged Progress / Achieved
4) Acknowledged Shortfall / Missed Target
5) Updated/Extended Commitments
6) Discontinued or Superseded Commitments
"""

    # We’ll instruct GPT to parse the chunk, identify relevant statements, 
    # and classify them accordingly.
    prompt = f"""
You are a sustainability report analysis assistant. 
We have two taxonomies for classifying references to carbon emissions 
commitments:

{taxonomy_instructions}

Given the text below, identify all statements or sections that 
(1) refer to forward-looking commitments (Taxonomy A), 
(2) refer to past commitments (Taxonomy B), 
or both. 
For each relevant snippet, classify them under one or more categories 
from Taxonomy A and/or Taxonomy B, and provide a brief explanation.

Return your results as a JSON array of objects. 
Each object can be:

{{
  "statement": "<the snippet>",
  "taxonomyA": [ 
     {{ "category": <number>, "explanation": "<why you chose it>" }},
     ...
  ],
  "taxonomyB": [
     {{ "category": <number>, "explanation": "<why you chose it>" }},
     ...
  ]
}}

If you see no relevant references to commitments, return an empty array: [].

TEXT TO ANALYZE:
\"\"\"
{text_chunk}
\"\"\"
"""
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant for ESG analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=800
    )

    content = response.choices[0].message.content
    return content


###############################################################################
# 4) PROCESS PDF, RUN CLASSIFICATION
###############################################################################
def get_pdf_metadata_from_path(pdf_path):
    """
    Extract metadata (category and year) from PDF path based on directory structure.
    Returns a tuple of (category, year)
    """
    # Split the path into components
    parts = os.path.normpath(pdf_path).split(os.sep)
    
    # Find the index of 'Reports' in the path
    try:
        reports_index = parts.index('Reports')
        # Category would be the directory after 'Reports'
        category = parts[reports_index + 1] if len(parts) > reports_index + 1 else "Uncategorized"
        # Year would be the directory after category
        year = parts[reports_index + 2] if len(parts) > reports_index + 2 else "Unknown"
    except ValueError:
        # If 'Reports' is not in path
        category = "Uncategorized"
        year = "Unknown"
    
    return category, year

def find_pdf_files(root_dir):
    """
    Recursively find all PDF files in the directory and its subdirectories
    """
    pdf_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(dirpath, filename))
    return pdf_files

def classify_pdf_sustainability_report(pdf_file_path: str):
    """
    Full pipeline: 
    1) extract raw text with pdfplumber,
    2) chunk if necessary,
    3) call GPT for classification on each chunk,
    4) aggregate and parse final results.
    """
    # Extract PDF text
    raw_text = extract_text_from_pdf(pdf_file_path)
    print(f"Extracted {len(raw_text)} characters from PDF.")

    # Split into chunks to avoid GPT token limit issues
    text_chunks = chunk_text(raw_text, MAX_TOKENS_PER_CHUNK)

    # Accumulate results from all chunks
    all_results = []

    for idx, chunk in enumerate(text_chunks, start=1):
        print(f"\n=== Processing chunk {idx}/{len(text_chunks)} (size={len(chunk)} chars)...")
        # Send chunk to GPT
        gpt_response = classify_text_with_gpt(chunk)

        # Attempt to parse JSON
        try:
            chunk_data = json.loads(gpt_response)
            if isinstance(chunk_data, list):
                all_results.extend(chunk_data)
            else:
                # Possibly a single object or unexpected structure
                all_results.append(chunk_data)
        except json.JSONDecodeError:
            print(f"[WARNING] Could not parse GPT response as JSON for chunk {idx}.")
            print("Raw response:\n", gpt_response)
    
    # Return or save the aggregated classification
    return all_results

def store_classification_results_in_csv(classification_results, output_csv, category, year):
    """
    Modified version to include category and year columns
    """
    rows = []
    for item in classification_results:
        statement = item.get("statement", "")
        
        # Extract forward (Taxonomy A) categories and explanations
        taxonomyA_entries = item.get("taxonomyA", [])
        A_cats = [str(cat_info.get("category")) for cat_info in taxonomyA_entries]
        A_exps = [cat_info.get("explanation", "") for cat_info in taxonomyA_entries]
        
        # Extract past (Taxonomy B) categories and explanations
        taxonomyB_entries = item.get("taxonomyB", [])
        B_cats = [str(cat_info.get("category")) for cat_info in taxonomyB_entries]
        B_exps = [cat_info.get("explanation", "") for cat_info in taxonomyB_entries]
        
        row_data = {
            "Category": category,
            "Year": year,
            "Statement": statement,
            "TaxonomyA_Categories": ", ".join(A_cats),
            "TaxonomyA_Explanations": " | ".join(A_exps),
            "TaxonomyB_Categories": ", ".join(B_cats),
            "TaxonomyB_Explanations": " | ".join(B_exps),
        }
        rows.append(row_data)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"[INFO] Classification results saved to {output_csv}")

###############################################################################
# 5) MAIN EXAMPLE
###############################################################################
def main():
    # Root directory containing PDF files
    root_directory = "Reports"
    print(f"\nSearching for PDFs in: {os.path.abspath(root_directory)}")
    
    # Get all PDF files recursively
    pdf_files = find_pdf_files(root_directory)
    
    # Debug print
    print(f"\nFound {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"- {pdf}")
    
    if not pdf_files:
        print(f"\nNo PDF files found in {root_directory} or its subdirectories")
        print("Please check that:")
        print("1. The 'Reports' directory exists in the current working directory")
        print("2. There are PDF files in the Reports directory or its subdirectories")
        print("3. The PDF files have .pdf extension (case insensitive)")
        return
    
    # Create a directory for results if it doesn't exist
    results_dir = "Classification_Results"
    os.makedirs(results_dir, exist_ok=True)
    print(f"\nCreated results directory: {os.path.abspath(results_dir)}")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"\n{'='*80}")
        print(f"Processing: {pdf_file}")
        print(f"{'='*80}")
        
        try:
            # Get metadata from path
            category, year = get_pdf_metadata_from_path(pdf_file)
            print(f"Extracted metadata - Category: {category}, Year: {year}")
            
            # Get the base filename without extension
            base_filename = os.path.splitext(os.path.basename(pdf_file))[0]
            
            # Process the PDF
            print("Starting PDF classification...")
            results = classify_pdf_sustainability_report(pdf_file)
            
            # Create output CSV filename with category and year
            output_csv = os.path.join(results_dir, f"{category}_{year}_{base_filename}_classification.csv")
            print(f"Saving results to: {output_csv}")
            
            # Save results to CSV with category and year information
            store_classification_results_in_csv(results, output_csv, category, year)
            
            # Print results to console as well
            print(f"\n=== CLASSIFICATION RESULTS FOR {pdf_file} ===")
            print(f"Category: {category}, Year: {year}")
            for i, item in enumerate(results, start=1):
                print(f"Item #{i}: {json.dumps(item, indent=2)}")
                
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
            # Print the full error traceback for debugging
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    print("\nStarting PDF classification script...")
    print(f"Current working directory: {os.getcwd()}")
    main()