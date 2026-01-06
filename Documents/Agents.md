# adobe-pdf-extractor

## Overview

A tool to extract text, images, and tables from PDF files.
Uses Adobe PDF Services API.

---

## Project Structure

```
adobe-pdf-extractor/
├── README.md              # Project documentation
├── Documents/
│   └── Agents.md          # Development notes
├── extract_pdf.py         # Main script
└── pdftojson-*.json       # Adobe API credentials
```

---

## Options

| Option | Description | Output |
|--------|-------------|--------|
| 1 | Text only | JSON with text |
| 2 | Images only | PNG files |
| 3 | Tables only | CSV files |
| 4 | All | Text + Images + Tables + Metadata |

---

## Code Reference

### Option 1: Text Only

```python
ExtractPDFParams(
    elements_to_extract=[ExtractElementType.TEXT]
)
```

### Option 2: Images Only

```python
ExtractPDFParams(
    elements_to_extract=[ExtractElementType.TEXT],
    elements_to_extract_renditions=[ExtractRenditionsElementType.FIGURES]
)
```

### Option 3: Tables Only

```python
ExtractPDFParams(
    elements_to_extract=[ExtractElementType.TABLES],
    table_structure_type=TableStructureType.CSV
)
```

### Option 4: All

```python
ExtractPDFParams(
    elements_to_extract=[ExtractElementType.TEXT, ExtractElementType.TABLES],
    elements_to_extract_renditions=[
        ExtractRenditionsElementType.TABLES,
        ExtractRenditionsElementType.FIGURES
    ],
    table_structure_type=TableStructureType.CSV,
    add_char_info=True,
    styling_info=True
)
```

---

## Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `elements_to_extract` | `TEXT`, `TABLES` | What to extract |
| `elements_to_extract_renditions` | `FIGURES`, `TABLES` | Render as images |
| `table_structure_type` | `CSV`, `XLSX` | Table output format |
| `add_char_info` | `True/False` | Character position data |
| `styling_info` | `True/False` | Font and style metadata |

---

## Links

- [Adobe PDF Services API](https://developer.adobe.com/document-services/docs/overview/)
- [Python SDK GitHub](https://github.com/adobe/pdfservices-python-sdk)
