import base64
from pathlib import Path
import os

def get_image_as_base64(image_path: str) -> str:
    """
    Convert an image file to base64 string.
    
    Args:
        image_path: Path to the image file relative to the workspace root
        
    Returns:
        Base64 encoded string of the image with appropriate data URI prefix
    """
    try:
        # Get the absolute path
        abs_path = Path(os.path.abspath(image_path))
        
        # Read the image file
        with open(abs_path, "rb") as image_file:
            # Get the file extension to determine the MIME type
            ext = abs_path.suffix.lower()
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/png')
            
            # Encode the image
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Return the data URI
            return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        # Return a placeholder image (1x1 transparent pixel)
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" 