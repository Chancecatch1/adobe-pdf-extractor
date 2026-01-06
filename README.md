# adobe-pdf-extractor

Extract text, images, and tables from PDF files using Adobe PDF Services API.

Perfect for academic papers, research documents, and books.

## Features

- **Text extraction** - Get all text from PDF
- **Image extraction** - Export figures and images as PNG
- **Table extraction** - Convert tables to CSV format
- **Full extraction** - Get everything with metadata

## Requirements

- Python 3.8+
- Adobe PDF Services API credentials (free tier: 500 pages/month)

## Installation

```bash
pip install pdfservices-sdk pypdf
```

## Setup - Get Adobe API Credentials

### Step 1: Create Project

1. Go to [Adobe Developer Console](https://developer.adobe.com/console)
2. Sign in with Adobe ID (free to create)
3. Click **"Create new project"**

### Step 2: Download Credentials

1. Go to **Project Overview** page
2. Click **"Download"** button (top right corner)
3. Save the JSON file in this project folder

```
project-folder/
├── extract_pdf.py
├── pdftojson-XXXXX-Production.json  <-- credentials file here
└── ...
```

## Usage

```bash
python extract_pdf.py
```

### Options

```
--------------------------------------------------
  Select extraction option
--------------------------------------------------
  1. Text only       -> .txt file
  2. Images only     -> images folder
  3. Tables only     -> CSV files
  4. All             -> folder with everything
--------------------------------------------------
```

## Output

ZIP is automatically extracted and organized:

| Option | Output |
|--------|--------|
| 1. Text | `filename.txt` |
| 2. Images | `filename_images/` folder with PNG files |
| 3. Tables | `filename_tables/` folder with CSV files |
| 4. All | `filename_extracted/` folder with text, images, tables |

## Auto Split for Large PDFs

For scanned PDFs over 100 pages, the tool automatically:

1. Splits the PDF into 100-page batches
2. Processes each batch separately
3. Creates separate outputs for each part

```
Total pages: 350
Splitting into 4 parts (100 pages each)

## API Pricing

| Plan | Pages | Cost |
|------|-------|------|
| Free | 500/month | $0 |
| Paid | Additional | ~$0.05/page |

## Links

- [Adobe PDF Services API Docs](https://developer.adobe.com/document-services/docs/overview/)
- [Python SDK](https://github.com/adobe/pdfservices-python-sdk)

## License

MIT

