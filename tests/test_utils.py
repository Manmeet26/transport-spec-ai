from utils import clean_text, extract_section_info, split_into_chunks


def test_clean_text_collapses_whitespace():
    assert clean_text("Concrete   shall\n\ncure") == "Concrete shall cure"


def test_extract_section_info_parses_caltrans_header():
    section, title = extract_section_info("90-1.02C Concrete Requirements")

    assert section == "90-1.02C"
    assert title == "Concrete Requirements"


def test_split_into_chunks_preserves_section_metadata():
    text = (
        "90-1.02C Concrete Requirements\n"
        "Concrete shall cure for at least seven days.\n"
        "90-1.03A Cold Weather\n"
        "Use insulated blankets when temperatures drop below 40F."
    )

    chunks = split_into_chunks(text, chunk_size=8, overlap=2)

    assert len(chunks) >= 2
    assert chunks[0]["section"] == "90-1.02C"
    assert "Concrete shall cure" in chunks[0]["text"]
