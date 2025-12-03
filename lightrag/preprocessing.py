"""
PDF Preprocessing Module for LightRAG
Converts PDF files to markdown format for better processing
"""

import os
import sys
import json
import io
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

try:
    import pdfplumber
    import fitz  # PyMuPDF
    from PIL import Image
    import pytesseract
    from markdownify import markdownify as mdify
    
    # Try pandas, but make it optional
    try:
        import pandas as pd
        PANDAS_AVAILABLE = True
    except ImportError:
        PANDAS_AVAILABLE = False
        pd = None
    
    PREPROCESSING_AVAILABLE = True
except ImportError as e:
    PREPROCESSING_AVAILABLE = False
    PANDAS_AVAILABLE = False
    MISSING_DEPS = str(e)
    pd = None

class PDFPreprocessor:
    """PDF to Markdown preprocessor for LightRAG"""
    
    def __init__(self, temp_dir: str = None):
        if not PREPROCESSING_AVAILABLE:
            raise ImportError(f"PDF preprocessing dependencies not available: {MISSING_DEPS}")
        
        self.temp_dir = Path(temp_dir) if temp_dir else Path("performance_improvement/output_file")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def ensure_dir(self, p: Path):
        """Ensure directory exists"""
        p.mkdir(parents=True, exist_ok=True)

    def save_pil_image(self, pil_img: Image.Image, path: Path):
        """Save PIL image as PNG"""
        if pil_img.mode not in ("RGB", "RGBA"):
            pil_img = pil_img.convert("RGB")
        pil_img.save(path, format="PNG")

    def ocr_image(self, pil_img: Image.Image) -> str:
        """Extract text from image using OCR"""
        try:
            txt = pytesseract.image_to_string(pil_img, lang='eng')
            return txt.strip()
        except Exception as e:
            # OCR failed (likely Tesseract not installed), return placeholder
            return f"[Image content - OCR unavailable: {type(e).__name__}]"

    def page_image_from_fitz(self, doc, page_num: int, zoom: int = 2) -> Image.Image:
        """Render page to PIL image via PyMuPDF"""
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes()))
        return img

    def table_to_markdown(self, table) -> str:
        """Convert table to markdown format"""
        if PANDAS_AVAILABLE and pd is not None:
            try:
                # Try pandas approach first
                df = pd.DataFrame(table[1:], columns=table[0]) if len(table) >= 2 else pd.DataFrame(table)
                return df.to_markdown(index=False)
            except Exception:
                pass  # Fall through to manual approach
        
        # Manual markdown table creation
        try:
            rows = ["| " + " | ".join(map(str, r)) + " |" for r in table]
            header = rows[0] if rows else ""
            sep = ""
            if header:
                cols = header.count("|") - 1
                sep = "| " + " | ".join(["---"] * cols) + " |"
            return "\n".join([header, sep] + rows[1:])
        except Exception:
            # Ultimate fallback: simple text representation
            return "\n".join(["\t".join(map(str, row)) for row in table])

    def process_pdf(self, pdf_path: str, output_name: str = None) -> Dict[str, Any]:
        """
        Process PDF file and convert to markdown
        
        Returns:
            Dict with processed file paths and metadata
        """
        input_path = Path(pdf_path)
        if not input_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Create unique output directory for this processing
        if output_name:
            out_path = self.temp_dir / output_name
        else:
            out_path = self.temp_dir / f"processed_{input_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.ensure_dir(out_path)
        images_dir = out_path / "images"
        self.ensure_dir(images_dir)

        md_lines = []
        txt_lines = []
        index = {
            "file": str(input_path), 
            "created": datetime.utcnow().isoformat() + "Z", 
            "pages": [],
            "images": [],
            "tables": []
        }

        try:
            # Open both pdfplumber and PyMuPDF
            with pdfplumber.open(str(input_path)) as ppdf, fitz.open(str(input_path)) as mdoc:
                num_pages = len(ppdf.pages)
                
                for i in range(num_pages):
                    print(f"Processing page {i+1}/{num_pages}")
                    page_meta = {"page_number": i+1, "images": [], "tables": []}
                    md_lines.append(f"\n\n# Page {i+1}\n")
                    txt_lines.append(f"\n\n--- PAGE {i+1} ---\n")

                    page = ppdf.pages[i]
                    
                    # Extract text
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        md_lines.append(page_text + "\n")
                        txt_lines.append(page_text + "\n")
                    else:
                        # OCR fallback
                        pil_page = self.page_image_from_fitz(mdoc, i, zoom=2)
                        ocred = self.ocr_image(pil_page)
                        note = "(OCR fallback)"
                        if ocred.strip():
                            md_lines.append(f"{note}\n\n" + ocred + "\n")
                            txt_lines.append(ocred + "\n")
                        else:
                            md_lines.append(f"{note} — (no text extracted)\n")
                            txt_lines.append("\n")

                    # Extract images
                    fitz_page = mdoc.load_page(i)
                    image_list = fitz_page.get_images(full=True)
                    for img_idx, img in enumerate(image_list, start=1):
                        xref = img[0]
                        base_image = mdoc.extract_image(xref)
                        image_bytes = base_image["image"]
                        img_ext = base_image.get("ext", "png")
                        image_name = f"page{i+1}_img{img_idx}.{img_ext}"
                        image_path = images_dir / image_name
                        
                        with open(image_path, "wb") as f:
                            f.write(image_bytes)
                        
                        # OCR for alt text
                        try:
                            pil_img = Image.open(io.BytesIO(image_bytes))
                        except Exception:
                            pil_img = Image.open(str(image_path))
                        
                        alt_text = self.ocr_image(pil_img)
                        if not alt_text:
                            alt_text = f"Extracted image {image_name} (no OCR text found)."
                        
                        # Add to markdown with image reference
                        relative_path = f"images/{image_name}"
                        md_lines.append(f"![{alt_text}]({relative_path})\n")
                        
                        image_info = {
                            "file": str(image_path),
                            "relative_path": relative_path,
                            "alt": alt_text,
                            "page": i+1
                        }
                        page_meta["images"].append(image_info)
                        index["images"].append(image_info)

                    # Extract tables
                    try:
                        tables = page.extract_tables() or []
                    except Exception:
                        tables = []
                    
                    for t_idx, table in enumerate(tables, start=1):
                        if not table:
                            continue
                        md_table = self.table_to_markdown(table)
                        md_lines.append("\n**Table**\n\n")
                        md_lines.append(md_table + "\n")
                        txt_lines.append("\n".join(["\t".join(map(str, r)) for r in table]) + "\n")
                        
                        table_info = {
                            "name": f"page{i+1}_table{t_idx}",
                            "rows": len(table),
                            "page": i+1
                        }
                        page_meta["tables"].append(table_info)
                        index["tables"].append(table_info)

                    index["pages"].append(page_meta)

            # Write output files
            md_file = out_path / "document.md"
            txt_file = out_path / "document.txt"
            idx_file = out_path / "index.json"

            # Add front matter to markdown
            front_matter = f"""---
source: {input_path.name}
extracted_on: {datetime.utcnow().isoformat()}Z
pages: {len(index['pages'])}
images: {len(index['images'])}
tables: {len(index['tables'])}
---

"""
            md_text = front_matter + "\n".join(md_lines)
            
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_text)

            with open(txt_file, "w", encoding="utf-8") as f:
                f.write("\n".join(txt_lines))

            with open(idx_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2)

            return {
                "success": True,
                "markdown_file": str(md_file),
                "text_file": str(txt_file),
                "index_file": str(idx_file),
                "images_dir": str(images_dir),
                "output_dir": str(out_path),
                "metadata": index
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_dir": str(out_path)
            }

    def cleanup_temp_files(self, output_dir: str = None):
        """Clean up temporary processing files"""
        if output_dir:
            cleanup_path = Path(output_dir)
        else:
            cleanup_path = self.temp_dir
        
        if cleanup_path.exists():
            try:
                shutil.rmtree(cleanup_path)
                print(f"🧹 Cleaned up temporary files: {cleanup_path}")
                return True
            except Exception as e:
                print(f"⚠️ Could not clean up {cleanup_path}: {e}")
                return False
        return True

def is_preprocessing_available() -> bool:
    """Check if preprocessing dependencies are available"""
    return PREPROCESSING_AVAILABLE

def preprocess_pdf(pdf_path: str, cleanup: bool = True) -> Dict[str, Any]:
    """
    Convenience function to preprocess a PDF file
    
    Args:
        pdf_path: Path to PDF file
        cleanup: Whether to cleanup temp files after processing
        
    Returns:
        Dict with processing results
    """
    if not is_preprocessing_available():
        return {
            "success": False,
            "error": f"PDF preprocessing not available: {MISSING_DEPS}",
            "fallback_required": True
        }
    
    try:
        preprocessor = PDFPreprocessor()
        result = preprocessor.process_pdf(pdf_path)
        
        if cleanup and result.get("success"):
            # Don't cleanup immediately, let LightRAG process first
            # Cleanup will be handled by the API after processing
            pass
            
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback_required": True
        }
