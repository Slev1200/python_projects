import sys
import os

# PyMuPDF
import fitz

import json
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def extract_text(filepath):
    if not os.path.exists(filepath):
        sys.exit(f"Error: File '{filepath}' not found.")
    if filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)
    elif filepath.endswith(".txt"):
        with open(filepath, "r") as f:
            return f.read()
    else:
        sys.exit("Error: Only .pdf and .txt files are supported.")

def chunk_text(text, chunk_size=2000):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def query_openai(text):
    prompt = f"""
    Analyze the following document excerpt and extract this information in JSON format:
    - parties: list of people or companies involved
    - effective_date: start date (or null if not mentioned)
    - expiry_date: end date (or null if not mentioned)
    - auto_renewal: true or false (or null if not mentioned)
    - key_obligations: list of 2-3 main obligations or topics discussed

    Document:
    {text}

    Respond with valid JSON only. No explanation. No markdown.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        sys.exit(f"API Error: {e}")

def parse_extraction(response):
    try:
        cleaned = re.sub(r"```json|```", "", response).strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Could not parse response", "raw": response}

def save_results(data, output_path="results.json"):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Results saved to {output_path}")

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python project.py <filename> [output.json]")
    filepath = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "results.json"

    print(f"File received: {filepath}")

    print("Extracting text...")
    text = extract_text(filepath)
    print(f"Extracted {len(text)} characters")

    print("Chunking text...")
    chunks = chunk_text(text)
    print(f"Split into {len(chunks)} chunks")

    all_results = []
    for i, chunk in enumerate(chunks):
        print(f"Analyzing chunk {i + 1} of {len(chunks)}...")
        raw_response = query_openai(chunk)
        parsed = parse_extraction(raw_response)
        all_results.append(parsed)

    save_results(all_results, output_path)
    print("\nDone!")

if __name__ == "__main__":
    main()
