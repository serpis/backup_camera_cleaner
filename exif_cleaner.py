from PIL import Image
import glob
import os

def remove_exif(file_path):
    """
    Opens an image, removes its EXIF data, and saves it in-place.
    """
    try:
        image = Image.open(file_path)
        
        # Save the image, overwriting the original, but with an empty exif field
        # and a high quality setting.
        image.save(file_path, exif=b'', quality=95)
        
        print(f"Removed EXIF from: {file_path}")

    except Exception as e:
        print(f"Could not process {file_path}: {e}")

if __name__ == "__main__":
    print("Starting EXIF data removal process.")
    print("This will overwrite original files and cannot be undone.")
    
    # Find all .jpg and .jpeg files in the current directory and all subdirectories
    jpg_files = glob.glob('**/*.jpg', recursive=True)
    jpeg_files = glob.glob('**/*.jpeg', recursive=True)
    
    all_images = jpg_files + jpeg_files
    
    if not all_images:
        print("No .jpg or .jpeg images found.")
    else:
        print(f"Found {len(all_images)} images to process.")
        for image_path in all_images:
            remove_exif(image_path)
            
    print("\nEXIF removal process complete.")
