# adobe-pdf-extractor

Extract text, images, and tables from PDF files using Adobe PDF Services API.

## Usage

```bash
pip install pdfservices-sdk pypdf
python extract_pdf.py
```

1. Enter PDF file path
2. Select extraction option:
   - `1` Text only → `text.txt`
   - `2` Images only → `images/`
   - `3` Tables only → `tables/`
   - `4` All (1+2+3)

## Credentials

Place your Adobe PDF Services credential JSON in the same directory as the script. Update `creds_path` in `extract_pdf.py` to match the filename.

## Output

Output is created next to the input PDF, in a folder named after the file. PDFs over 100 pages are automatically split into batches.

## Links

- [Adobe PDF Services API](https://developer.adobe.com/document-services/docs/overview/)
