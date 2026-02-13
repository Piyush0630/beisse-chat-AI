import fitz  # PyMuPDF
from typing import List, Dict, Any

def extract_text_and_bbox(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text blocks along with their bounding boxes and page numbers from a PDF.
    """
    doc = fitz.open(pdf_path)
    text_blocks = []
    
    for page_num, page in enumerate(doc):
        # get_text("blocks") returns a list of tuples:
        # (x0, y0, x1, y1, "text", block_no, block_type)
        blocks = page.get_text("blocks")
        for b in blocks:
            text = b[4].strip()
            if text:
                text_blocks.append({
                    "text": text,
                    "bbox": {
                        "x": b[0],
                        "y": b[1],
                        "width": b[2] - b[0],
                        "height": b[3] - b[1]
                    },
                    "page": page_num + 1,
                    "block_type": b[6]
                })
    doc.close()
    return text_blocks

def chunk_text(text_blocks: List[Dict[str, Any]], chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Groups text blocks into chunks of approximately chunk_size words.
    """
    chunks = []
    current_chunk_text = ""
    current_blocks = []
    
    for block in text_blocks:
        block_text = block["text"]
        
        # If adding this block exceeds chunk_size, save current and start new
        # Using word count as a proxy for tokens
        if len(current_chunk_text.split()) + len(block_text.split()) > chunk_size and current_chunk_text:
            # Save current chunk
            chunks.append({
                "text": current_chunk_text.strip(),
                "page": current_blocks[0]["page"],
                "bbox": current_blocks[0]["bbox"], # Use first block's bbox as primary
                "all_blocks": current_blocks
            })
            
            # Start new chunk. For now, simple overlap by taking last few words 
            # might be complex with blocks, so let's just start next chunk.
            # In a more advanced version, we'd handle overlap better.
            current_chunk_text = ""
            current_blocks = []
        
        current_chunk_text += block_text + " "
        current_blocks.append(block)
            
    # Add last chunk
    if current_chunk_text:
        chunks.append({
            "text": current_chunk_text.strip(),
            "page": current_blocks[0]["page"],
            "bbox": current_blocks[0]["bbox"],
            "all_blocks": current_blocks
        })
        
    return chunks
