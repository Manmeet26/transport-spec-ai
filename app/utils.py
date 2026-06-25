import re


# -----------------------------
# CLEAN TEXT
# -----------------------------

def clean_text(text):

    """
    Normalize whitespace.
    """

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# -----------------------------
# EXTRACT SECTION INFO
# -----------------------------

def extract_section_info(line):

    """
    Detect section headers.

    Examples:
    90-1.02C Concrete Requirements
    5-1 General
    """

    pattern = (
        r'^(\d+(?:-\d+)*'
        r'(?:\.\d+)?[A-Z]?)'
        r'\s+(.*)'
    )

    match = re.match(
        pattern,
        line.strip()
    )

    if match:

        section = match.group(1)

        title = match.group(2)

        return section, title

    return None, None


# -----------------------------
# SECTION-AWARE CHUNKING
# -----------------------------

def split_into_chunks(
    text,
    chunk_size=350,
    overlap=75
):

    """
    Section-aware chunking.

    1. Detect section headers
    2. Group text by sections
    3. Chunk within sections
    """

    lines = text.split("\n")

    sections = []

    current_section = None

    current_title = None

    current_content = []

    # -----------------------------
    # BUILD SECTIONS
    # -----------------------------

    for line in lines:

        line = line.strip()

        if not line:

            continue

        section, title = extract_section_info(
            line
        )

        # new section found
        if section:

            # save previous section
            if current_content:

                sections.append({

                    "section":
                        current_section,

                    "title":
                        current_title,

                    "content":
                        " ".join(
                            current_content
                        )
                })

            current_section = section

            current_title = title

            current_content = []

        else:

            current_content.append(line)

    # final section
    if current_content:

        sections.append({

            "section":
                current_section,

            "title":
                current_title,

            "content":
                " ".join(
                    current_content
                )
        })

    # -----------------------------
    # CHUNK WITHIN SECTIONS
    # -----------------------------

    final_chunks = []

    for sec in sections:

        content = sec["content"]

        words = content.split()

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk_words = words[
                start:end
            ]

            chunk_text = " ".join(
                chunk_words
            )

            final_chunks.append({

                "section":
                    sec["section"],

                "title":
                    sec["title"],

                "text":
                    chunk_text
            })

            start += (
                chunk_size - overlap
            )

    return final_chunks