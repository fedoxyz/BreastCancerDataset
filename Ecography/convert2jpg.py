import os
import numpy as np
from PIL import Image

def convert_to_jpg(dataset_path):
    """
    Convert all PNG images and masks to JPG format.
    - Regular images: Standard JPEG conversion
    - Masks: Strictly binary values (0 or 255)
    
    Args:
        dataset_path: Path to the main dataset directory containing class subdirectories
    """
    # Iterate through all BIRADS class directories
    for birads_class in os.listdir(dataset_path):
        class_path = os.path.join(dataset_path, birads_class)
        if not os.path.isdir(class_path):
            continue
            
        # Process both images and masks directories
        for dir_type in ['images', 'masks']:
            dir_path = os.path.join(class_path, dir_type)
            if not os.path.exists(dir_path):
                continue
                
            print(f"Processing {dir_type} in BIRADS class {birads_class}...")
            
            # Process each file in the directory
            for file_name in os.listdir(dir_path):
                if not file_name.endswith('.png'):
                    continue
                    
                file_path = os.path.join(dir_path, file_name)
                jpg_filename = os.path.splitext(file_name)[0] + '.jpg'
                jpg_path = os.path.join(dir_path, jpg_filename)
                
                # Open the image
                img = Image.open(file_path)
                
                if dir_type == 'masks':
                    # Process masks: ensure binary values
                    mask_array = np.array(img)
                    # Convert to strictly binary values: 0 or 255
                    binary_mask = np.where(mask_array > 0, 255, 0).astype(np.uint8)
                    img = Image.fromarray(binary_mask)
                    
                    # Save as JPEG
                    img.save(jpg_path, 'JPEG', quality=100)
                    
                else:
                    # Process regular images: standard JPEG conversion
                    if img.mode == 'RGBA':
                        # Convert RGBA to RGB
                        img = img.convert('RGB')
                    img.save(jpg_path, 'JPEG', quality=95)
                
                # Remove the original PNG file
                os.remove(file_path)
                
                print(f"Converted {file_name} to {jpg_filename}")

if __name__ == "__main__":
    dataset_path = './dataset'  # Adjust this path as needed
    convert_to_jpg(dataset_path)
    print("Conversion completed successfully!")
