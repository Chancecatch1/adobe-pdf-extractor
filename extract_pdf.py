import json
import os
import tempfile
import zipfile
import shutil
from pypdf import PdfReader, PdfWriter
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.config.client_config import ClientConfig
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_renditions_element_type import ExtractRenditionsElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.table_structure_type import TableStructureType
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult


PAGES_PER_BATCH = 100  # Adobe API limit for scanned PDFs


def get_extract_params(option: int) -> ExtractPDFParams:
    """Return ExtractPDFParams based on selected option (1, 2, or 3 only)"""
    
    if option == 1:  # Text only
        return ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TEXT]
        )
    
    elif option == 2:  # Images only
        return ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TEXT],
            elements_to_extract_renditions=[ExtractRenditionsElementType.FIGURES]
        )
    
    elif option == 3:  # Tables only
        return ExtractPDFParams(
            elements_to_extract=[ExtractElementType.TABLES],
            table_structure_type=TableStructureType.CSV
        )
    
    else:
        raise ValueError("Invalid option. Use 1, 2, or 3.")


def extract_text_from_json(json_path: str) -> str:
    """Extract plain text from structuredData.json"""
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    text_parts = []
    
    for element in data.get("elements", []):
        if "Text" in element:
            text_parts.append(element["Text"])
    
    return "\n".join(text_parts)


def process_zip_output(zip_path: str, output_dir: str, option: int, base_name: str) -> list:
    """Extract ZIP and organize files based on option"""
    
    created_files = []
    
    with zipfile.ZipFile(zip_path, "r") as zf:
        # Create temp directory for extraction
        temp_dir = tempfile.mkdtemp()
        zf.extractall(temp_dir)
        
        if option == 1:  # Text only -> .txt file
            json_path = os.path.join(temp_dir, "structuredData.json")
            if os.path.exists(json_path):
                text = extract_text_from_json(json_path)
                txt_path = os.path.join(output_dir, "text.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(text)
                created_files.append(txt_path)
        
        elif option == 2:  # Images only -> images folder
            figures_src = os.path.join(temp_dir, "figures")
            if os.path.exists(figures_src):
                figures_dst = os.path.join(output_dir, "images")
                if os.path.exists(figures_dst):
                    shutil.rmtree(figures_dst)
                shutil.copytree(figures_src, figures_dst)
                created_files.append(figures_dst)
        
        elif option == 3:  # Tables only -> tables folder
            tables_src = os.path.join(temp_dir, "tables")
            if os.path.exists(tables_src):
                tables_dst = os.path.join(output_dir, "tables")
                if os.path.exists(tables_dst):
                    shutil.rmtree(tables_dst)
                shutil.copytree(tables_src, tables_dst)
                created_files.append(tables_dst)
        
        # Option 4 is handled separately in main() by running 1, 2, 3 sequentially
        
        # Clean up temp directory
        shutil.rmtree(temp_dir)
    
    # Remove ZIP file after extraction
    os.remove(zip_path)
    
    return created_files


def split_pdf(pdf_path: str, pages_per_batch: int = PAGES_PER_BATCH) -> list:
    """Split PDF into smaller parts. Returns list of temp file paths."""
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    if total_pages <= pages_per_batch:
        return [pdf_path]
    
    temp_files = []
    
    for start in range(0, total_pages, pages_per_batch):
        end = min(start + pages_per_batch, total_pages)
        
        writer = PdfWriter()
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        writer.write(temp_file)
        temp_file.close()
        temp_files.append(temp_file.name)
    
    return temp_files


def extract_single_pdf(pdf_services, pdf_path: str, output_path: str, option: int):
    """Extract content from a single PDF file"""
    
    with open(pdf_path, "rb") as file:
        input_asset = pdf_services.upload(input_stream=file, mime_type=PDFServicesMediaType.PDF)
    
    extract_pdf_params = get_extract_params(option)
    extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)
    location = pdf_services.submit(extract_pdf_job)
    pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)
    
    result_asset = pdf_services_response.get_result().get_resource()
    stream_asset = pdf_services.get_content(result_asset)
    
    with open(output_path, "wb") as f:
        f.write(stream_asset.get_input_stream())


def main():
    # Print title
    print("\n" + "="*50)
    print("  Adobe PDF Extractor")
    print("="*50)
    
    # Get PDF path from user
    pdf_path = input("\nEnter PDF file path: ").strip()
    pdf_path = pdf_path.strip("'\"")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return
    
    # Show options
    print("\n" + "-"*50)
    print("  Select extraction option")
    print("-"*50)
    print("  1. Text only       -> .txt file")
    print("  2. Images only     -> images folder")
    print("  3. Tables only     -> CSV files")
    print("  4. All (1+2+3)     -> text + images + tables")
    print("-"*50)
    
    # Get user choice
    try:
        option = int(input("\nSelect (1-4): ").strip())
        if option < 1 or option > 4:
            raise ValueError()
    except ValueError:
        print("Error: Please enter a number between 1-4")
        return
    
    # Load credentials
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, "pdftojson-3986782-Production.json")
    
    with open(creds_path, "r") as f:
        creds = json.load(f)
    
    oauth_creds = creds["project"]["workspace"]["details"]["credentials"][0]["oauth_server_to_server"]
    
    credentials = ServicePrincipalCredentials(
        client_id=oauth_creds["client_id"],
        client_secret=oauth_creds["client_secrets"][0]
    )
    
    # Configure timeout: connect=10s, read=120s (default is 10s which is too short)
    client_config = ClientConfig(
        connect_timeout=10000,  # 10 seconds
        read_timeout=120000     # 120 seconds (2 minutes)
    )
    
    pdf_services = PDFServices(credentials=credentials, client_config=client_config)
    
    # Check page count
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    print(f"\nTotal pages: {total_pages}")
    
    pdf_dir = os.path.dirname(pdf_path) or "."
    pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
    
    all_created_files = []
    
    if total_pages <= PAGES_PER_BATCH:
        # Single file processing
        # Create output folder
        output_folder = os.path.join(pdf_dir, f"{pdf_basename}")
        os.makedirs(output_folder, exist_ok=True)
        
        if option == 4:
            # Option 4: Run options 1, 2, 3 sequentially
            option_names = {1: "Text", 2: "Images", 3: "Tables"}
            import time
            
            for sub_option in [1, 2, 3]:
                zip_path = os.path.join(pdf_dir, f"{pdf_basename}_temp.zip")
                
                print(f"\n[{sub_option}/3] Extracting {option_names[sub_option]}...")
                print(f"  Uploading PDF...")
                print(f"  Extracting content...")
                
                try:
                    extract_single_pdf(pdf_services, pdf_path, zip_path, sub_option)
                    print(f"  Processing output...")
                    process_zip_output(zip_path, output_folder, sub_option, pdf_basename)
                except Exception as e:
                    print(f"  Warning: {option_names[sub_option]} extraction failed - {e}")
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                
                # Delay between API calls to avoid rate limiting
                if sub_option < 3:
                    time.sleep(2)
        else:
            # Single option (1, 2, or 3)
            zip_path = os.path.join(pdf_dir, f"{pdf_basename}_temp.zip")
            
            print(f"Uploading PDF...")
            print(f"Extracting content...")
            
            extract_single_pdf(pdf_services, pdf_path, zip_path, option)
            
            print(f"Processing output...")
            process_zip_output(zip_path, output_folder, option, pdf_basename)
        
        all_created_files.append(output_folder)
    
    else:
        # Split and process in batches
        num_batches = (total_pages + PAGES_PER_BATCH - 1) // PAGES_PER_BATCH
        print(f"Splitting into {num_batches} parts ({PAGES_PER_BATCH} pages each)...")
        
        temp_files = split_pdf(pdf_path, PAGES_PER_BATCH)
        
        # Create main output folder
        output_folder = os.path.join(pdf_dir, f"{pdf_basename}")
        os.makedirs(output_folder, exist_ok=True)
        
        # Determine which options to run
        options_to_run = [1, 2, 3] if option == 4 else [option]
        option_names = {1: "Text", 2: "Images", 3: "Tables"}
        
        for i, temp_pdf in enumerate(temp_files):
            start_page = i * PAGES_PER_BATCH + 1
            end_page = min((i + 1) * PAGES_PER_BATCH, total_pages)
            
            # Create subfolder for this part
            part_name = f"part{i+1}_p{start_page}-{end_page}"
            part_folder = os.path.join(output_folder, part_name)
            os.makedirs(part_folder, exist_ok=True)
            
            print(f"\n[{i+1}/{num_batches}] Processing pages {start_page}-{end_page}...")
            
            for sub_option in options_to_run:
                zip_path = os.path.join(pdf_dir, f"{pdf_basename}_temp.zip")
                
                if option == 4:
                    print(f"  [{sub_option}/3] Extracting {option_names[sub_option]}...")
                else:
                    print(f"  Extracting...")
                
                try:
                    extract_single_pdf(pdf_services, temp_pdf, zip_path, sub_option)
                    process_zip_output(zip_path, part_folder, sub_option, part_name)
                    
                except Exception as e:
                    print(f"  Error: {e}")
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
            
            # Clean up temp PDF
            if temp_pdf != pdf_path:
                os.unlink(temp_pdf)
        
        all_created_files.append(output_folder)
    
    # Print summary
    print(f"\n" + "="*50)
    print(f"Done! Created {len(all_created_files)} output(s):")
    for f in all_created_files:
        print(f"  - {f}")
    print("="*50)


if __name__ == "__main__":
    main()
