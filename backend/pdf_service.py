"""PDF generator for MP Suvidha Demonstration Certificates and Service Reports.
Built using standard PDF 1.4 specification with robust character handling.
"""
import textwrap

# Common Hindi to English transliteration map for graceful fallback in Type-1 fonts
HINDI_CHAR_MAP = {
    'अ': 'A', 'आ': 'Aa', 'इ': 'I', 'ई': 'Ee', 'उ': 'U', 'ऊ': 'Oo', 'ऋ': 'Ri',
    'ए': 'E', 'ऐ': 'Ai', 'ओ': 'O', 'औ': 'Au', 'अं': 'An', 'अः': 'Ah',
    'क': 'Ka', 'ख': 'Kha', 'ग': 'Ga', 'घ': 'Gha', 'ङ': 'Nga',
    'च': 'Cha', 'छ': 'Chha', 'ज': 'Ja', 'झ': 'Jha', 'ञ': 'Nya',
    'ट': 'Ta', 'ठ': 'Tha', 'ड': 'Da', 'ढ': 'Dha', 'ण': 'Na',
    'त': 'Ta', 'थ': 'Tha', 'द': 'Da', 'ध': 'Dha', 'न': 'Na',
    'प': 'Pa', 'फ': 'Pha', 'ब': 'Ba', 'भ': 'Bha', 'म': 'Ma',
    'य': 'Ya', 'र': 'Ra', 'ल': 'La', 'व': 'Va', 'श': 'Sha',
    'ष': 'Sha', 'स': 'Sa', 'ह': 'Ha', 'क्ष': 'Ksha', 'त्र': 'Tra', 'ज्ञ': 'Gya',
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', '्': '',
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    '₹': 'Rs.', '—': '-', '–': '-', '“': '"', '”': '"', '‘': "'", '’': "'", '•': '*'
}

def clean_pdf_text(value: str) -> str:
    """Sanitizes text to safe characters for Helvetica, transliterating Hindi characters gracefully."""
    if not value:
        return ""
    val = str(value).replace("\r", " ").replace("\n", " ").replace("\t", " ")
    
    # Check if there are non-ASCII characters
    res = []
    for ch in val:
        if ord(ch) < 128:
            res.append(ch)
        elif ch in HINDI_CHAR_MAP:
            res.append(HINDI_CHAR_MAP[ch])
        else:
            # Fallback for unknown unicode
            res.append(" ")
    cleaned = "".join(res)
    # Remove consecutive spaces
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    return cleaned.strip()

def pdf_escape(value: str) -> str:
    """Escapes special PDF string characters: parentheses and backslashes."""
    return clean_pdf_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def generate_pdf_document(title: str, subtitle: str, entries: list[tuple[str, str]]) -> bytes:
    """Builds a multi-page PDF document using standard PDF 1.4 specifications."""
    rows: list[tuple[str, str]] = []
    for kind, raw in entries:
        val = clean_pdf_text(raw)
        if kind in ("heading", "subheading", "badge", "spacer", "divider"):
            rows.append((val, kind))
        else:
            wrapped = textwrap.wrap(val, width=86, break_long_words=True, break_on_hyphens=False) or [""]
            rows.extend((line, "body") for line in wrapped)

    pages: list[list[tuple[str, str]]] = []
    current_page: list[tuple[str, str]] = []
    y = 700

    for row in rows:
        val, kind = row
        if kind == "heading":
            height = 22
        elif kind == "subheading":
            height = 18
        elif kind == "spacer":
            height = 10
        elif kind == "divider":
            height = 8
        elif kind == "badge":
            height = 16
        else:
            height = 13

        if y - height < 60 and current_page:
            pages.append(current_page)
            current_page = []
            y = 700
        current_page.append(row)
        y -= height

    if current_page or not pages:
        pages.append(current_page)

    num_pages = len(pages)
    page_ids = [4 + 2 * i for i in range(num_pages)]
    objects: list[bytes | None] = [None] * (4 + 2 * num_pages)
    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[2] = f"<< /Type /Pages /Kids [{kids}] /Count {num_pages} >>".encode("ascii")
    objects[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    for idx, page_rows in enumerate(pages):
        page_id = 4 + idx * 2
        stream_id = 5 + idx * 2

        cmds = [
            # Top Primary Navy Banner (#123B63 -> r:0.071, g:0.231, b:0.388)
            "q 0.071 0.231 0.388 rg 0 760 595 82 re f Q",
            # Saffron Orange Accent Bar (#F4A340 -> r:0.957, g:0.639, b:0.251)
            "q 0.957 0.639 0.251 rg 0 756 595 4 re f Q",
            # Brand Title
            f"BT /F1 16 Tf 1 1 1 rg 40 802 Td ({pdf_escape('MP SUVIDHA · MADHYA PRADESH DIGITAL SERVICES')}) Tj ET",
            f"BT /F1 9 Tf 0.92 0.95 0.98 rg 40 778 Td ({pdf_escape(subtitle or 'CITIZEN INFORMATION & DEMONSTRATION RECORD')}) Tj ET",
            # Page Title
            f"BT /F1 14 Tf 0.071 0.231 0.388 rg 40 730 Td ({pdf_escape(title)}) Tj ET",
            "0.88 0.91 0.94 RG 40 716 m 555 716 l S",
        ]

        curr_y = 698
        for value, kind in page_rows:
            if kind == "spacer":
                curr_y -= 8
            elif kind == "divider":
                cmds.append(f"0.88 0.91 0.94 RG 40 {curr_y} m 555 {curr_y} l S")
                curr_y -= 6
            elif kind == "heading":
                curr_y -= 4
                cmds.append(f"BT /F1 11 Tf 0.071 0.231 0.388 rg 40 {curr_y} Td ({pdf_escape(value)}) Tj ET")
                curr_y -= 16
            elif kind == "subheading":
                cmds.append(f"BT /F1 10 Tf 0.09 0.41 0.66 rg 40 {curr_y} Td ({pdf_escape(value)}) Tj ET")
                curr_y -= 14
            elif kind == "badge":
                cmds.append(f"BT /F1 9 Tf 0.086 0.549 0.514 rg 40 {curr_y} Td ({pdf_escape(value)}) Tj ET")
                curr_y -= 13
            else:
                cmds.append(f"BT /F1 9 Tf 0.12 0.16 0.22 rg 40 {curr_y} Td ({pdf_escape(value)}) Tj ET")
                curr_y -= 13

        # Footer divider and disclaimer
        cmds.extend([
            "0.88 0.91 0.94 RG 40 42 m 555 42 l S",
            f"BT /F1 8 Tf 0.40 0.46 0.52 rg 40 28 Td ({pdf_escape('MP Suvidha · Independent Demonstration Portal · Not affiliated with Government of MP')}) Tj ET",
            f"BT /F1 8 Tf 0.40 0.46 0.52 rg 518 28 Td ({idx + 1} / {num_pages}) Tj ET",
        ])

        stream_bytes = "\n".join(cmds).encode("ascii")
        objects[page_id] = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {stream_id} 0 R >>".encode("ascii")
        objects[stream_id] = f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii") + stream_bytes + b"\nendstream"

    # Assemble cross reference and trailer
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj_id in range(1, len(objects)):
        offsets.append(len(output))
        output.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        output.extend(objects[obj_id] or b"")
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects)}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii"))

    return bytes(output)


def build_certificate_pdf(cert: dict) -> bytes:
    """Builds a formatted demo certificate document for MP Suvidha."""
    entries = [
        ("badge", "★ DEMONSTRATION RECORD · SIMULATED E-GOVERNANCE CERTIFICATE ★"),
        ("spacer", ""),
        ("body", "This is to certify that the following citizen application has been verified"),
        ("body", "and approved within the MP Suvidha Madhya Pradesh Digital Services Portal:"),
        ("spacer", ""),
        ("heading", f"ISSUED TO:  {cert.get('applicant_name', 'Applicant Name')}"),
        ("divider", ""),
        ("subheading", f"Service Name:           {cert.get('service_name', 'N/A')}"),
        ("body",       f"Certificate Number:     {cert.get('number', 'N/A')}"),
        ("body",       f"Issuing Department:     {cert.get('department', 'N/A')}"),
        ("body",       f"Date of Issue:          {cert.get('issue_date', 'N/A')}"),
        ("body",       f"Application ID:         {cert.get('application_id', 'N/A')}"),
        ("body",       f"Verification Status:    {cert.get('status', 'Valid')} (Demo Registered)"),
        ("spacer", ""),
        ("divider", ""),
        ("heading", "Demonstration Record Declaration"),
        ("body", "1. This certificate is digitally generated as an informational demonstration workflow showcasing citizen service delivery."),
        ("body", "2. It exhibits complete end-to-end citizen application lifecycle: online submission, document review, officer verification, and automated certificate issuance."),
        ("body", "3. Certificate authenticity can be verified anytime on MP Suvidha via the Certificate Verification module."),
        ("spacer", ""),
        ("body", "DISCLAIMER: This certificate is created strictly for demonstration purposes on MP Suvidha and holds no legal, administrative, or statutory validity with the Government of Madhya Pradesh or any official agency."),
    ]
    return generate_pdf_document("DEMONSTRATION CERTIFICATE OF SERVICE", "MADHYA PRADESH DIGITAL SERVICES · RECORD", entries)


def build_evaluation_report_pdf(item: dict) -> bytes:
    """Builds an internal E-Governance Portal Evaluation report."""
    scores = item.get("scores", {})
    entries = [
        ("badge", "INTERNAL SYSTEM ASSESSMENT · E-GOVERNANCE PORTAL AUDIT REPORT"),
        ("spacer", ""),
        ("heading", "1. PORTAL INFORMATION & EVALUATION METADATA"),
        ("body", f"Target Portal Name:     {item.get('portal_name', 'Local Portal')}"),
        ("body", f"Portal URL / Access:    {item.get('portal_url') or 'Not provided'}"),
        ("body", f"Governing Department:   {item.get('department') or 'Public Administration'}"),
        ("body", f"Evaluation Date:        {item.get('evaluation_date', 'N/A')}"),
        ("body", f"Evaluation Group:       {item.get('evaluator_group') or 'Audit Team'}"),
        ("body", f"Lead Evaluator:         {item.get('evaluator') or 'System Reviewer'}"),
        ("spacer", ""),
        ("heading", "2. PORTAL OVERVIEW & OBJECTIVE"),
        ("body", item.get("description") or "Comprehensive assessment of digital public service efficiency, navigation clarity, and citizen usability."),
        ("spacer", ""),
        ("heading", "3. EVALUATION SCORES (Scale: 1 = Needs Improvement, 5 = Excellent)"),
    ]

    criteria = [
        "User Friendliness", "Navigation and Interface", "Accessibility", "Service Availability",
        "Application Process", "Application Tracking", "Information Accuracy", "Security and Privacy",
        "Mobile Responsiveness", "Overall User Experience"
    ]
    total_score = 0
    for crit in criteria:
        val = int(scores.get(crit, 0))
        total_score += val
        stars = "* " * val + "- " * (5 - val)
        entries.append(("body", f"- {crit.ljust(26)} :  {val} / 5   [{stars.strip()}]"))

    avg = round(total_score / len(criteria), 2)
    entries.append(("subheading", f"Overall Evaluation Score: {avg} / 5.00 ({total_score} of 50 points)"))
    entries.append(("spacer", ""))

    sections = [
        ("4. PORTAL STRENGTHS", item.get("strengths") or "Clear categorization and service discovery."),
        ("5. PORTAL LIMITATIONS", item.get("limitations") or "Multi-step navigation barriers."),
        ("6. TECHNICAL ISSUES", item.get("technical_issues") or "Mobile responsiveness constraints."),
        ("7. RECOMMENDATIONS", item.get("recommendations") or "Adopt unified digital design standards and instant tracking."),
    ]

    for title, text in sections:
        entries.append(("heading", title))
        entries.append(("body", text))
        entries.append(("spacer", ""))

    return generate_pdf_document("PORTAL AUDIT REPORT", "DIGITAL SERVICES EVALUATION", entries)
