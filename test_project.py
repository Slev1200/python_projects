from project import chunk_text, parse_extraction, save_results
import json
import os

def test_chunk_text_splits_correctly():
    text = " ".join(["word"] * 5000)
    chunks = chunk_text(text, chunk_size=2000)
    assert len(chunks) == 3

def test_chunk_text_single_chunk():
    text = "this is a short document"
    chunks = chunk_text(text, chunk_size=2000)
    assert len(chunks) == 1

def test_parse_extraction_valid_json():
    fake_response = '{"parties": ["Acme", "Bob"], "effective_date": "2024-01-01"}'
    result = parse_extraction(fake_response)
    assert result["parties"] == ["Acme", "Bob"]

def test_parse_extraction_strips_fences():
    fake_response = '```json\n{"parties": ["Acme"]}\n```'
    result = parse_extraction(fake_response)
    assert "parties" in result

def test_parse_extraction_bad_json():
    fake_response = "this is not json at all"
    result = parse_extraction(fake_response)
    assert "error" in result

def test_save_results_creates_file():
    test_data = [{"parties": ["Acme"], "effective_date": "2024-01-01"}]
    save_results(test_data, "test_output.json")
    assert os.path.exists("test_output.json")
    with open("test_output.json") as f:
        loaded = json.load(f)
    assert loaded[0]["parties"] == ["Acme"]
    os.remove("test_output.json")
