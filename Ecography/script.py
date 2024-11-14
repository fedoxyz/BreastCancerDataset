import os
import shutil
import pandas as pd
from PIL import Image

class ImageCounter:
    def __init__(self):
        self.current_count = 1

    def get_next_number(self):
        number = self.current_count
        self.current_count += 1
        return number

def process_mask(mask_path, output_path):
    """
    Process mask by removing alpha channel and replacing it with black background
    """
    # Open the mask image
    mask = Image.open(mask_path)
    
    # Convert to RGBA if not already
    if mask.mode != 'RGBA':
        mask = mask.convert('RGBA')
    
    # Split into channels
    r, g, b, a = mask.split()
    
    # Create a new image with black background
    background = Image.new('RGB', mask.size, (0, 0, 0))
    
    # Paste the mask using alpha channel
    background.paste(mask, mask=a)
    
    # Save the processed mask
    background.save(output_path)

def substitute_birads(birads_label):
    """ Substitutes BIRADS labels like '4a', '4b', '4c' to just '4' """
    if birads_label in ['4a', '4b', '4c']:
        return 3
    return int(birads_label) - 1

def process_busbra_data(busbtra_folder, output_folder, counter):
    """ Processes the BUSBRA data folder and organizes images and masks """
    bus_data = pd.read_csv(os.path.join(busbtra_folder, 'bus_data.csv'))
    
    # Loop over the data and move files to corresponding subfolders
    for idx, row in bus_data.iterrows():
        birads_label = substitute_birads(str(row['BIRADS']))
        image_id = str(row['ID'])
        
        # Assuming Images and Masks folders in BUSBRA folder
        images_folder = os.path.join(busbtra_folder, 'Images')
        masks_folder = os.path.join(busbtra_folder, 'Masks')
        
        image_filename = f"{image_id}.png"
        mask_filename = f"mask_{image_id.split('_')[1]}.png"
        mask_path = os.path.join(masks_folder, mask_filename)

        if os.path.exists(mask_path):
            # Get next number for consistent naming
            next_num = counter.get_next_number()
            
            # Define source file paths
            image_path = os.path.join(images_folder, image_filename)
            
            # Define destination folder paths
            dest_image_folder = os.path.join(output_folder, str(birads_label), 'images')
            dest_mask_folder = os.path.join(output_folder, str(birads_label), 'masks')
            
            # Ensure destination folders exist
            os.makedirs(dest_image_folder, exist_ok=True)
            os.makedirs(dest_mask_folder, exist_ok=True)
            
            # Copy files with new standardized names
            shutil.copy(image_path, os.path.join(dest_image_folder, f"{next_num}.png"))
            shutil.copy(mask_path, os.path.join(dest_mask_folder, f"{next_num}_mask.png"))

def process_breast_data(breast_folder, output_folder, counter):
    """ Processes the BrEaSt data folder and organizes images and masks """
    excel_file = os.path.join(breast_folder, 'BrEaST-Lesions-USG-clinical-data-Dec-15-2023.xlsx')
    df = pd.read_excel(excel_file)
    df['BIRADS'] = df['BIRADS'].apply(substitute_birads)

    for idx, row in df.iterrows():
        birads_label = row['BIRADS']
        image_file = row['Image_filename']
        mask_file = row['Mask_tumor_filename']
        
        # Define source file paths
        image_path = os.path.join(breast_folder, 'BrEaST-Lesions_USG-images_and_masks', image_file)
        mask_path = os.path.join(breast_folder, 'BrEaST-Lesions_USG-images_and_masks', mask_file) if type(mask_file) != float else "123"
        
        if os.path.exists(mask_path):
            # Get next number for consistent naming
            next_num = counter.get_next_number()
            
            # Define destination folder paths
            dest_image_folder = os.path.join(output_folder, str(birads_label), 'images')
            dest_mask_folder = os.path.join(output_folder, str(birads_label), 'masks')

            # Ensure destination folders exist
            os.makedirs(dest_image_folder, exist_ok=True)
            os.makedirs(dest_mask_folder, exist_ok=True)

            # Define output paths
            dest_image_path = os.path.join(dest_image_folder, f"{next_num}.png")
            dest_mask_path = os.path.join(dest_mask_folder, f"{next_num}_mask.png")

            # Copy image as is
            shutil.copy(image_path, dest_image_path)
            
            # Process and save mask
            process_mask(mask_path, dest_mask_path)

def process_breast_images(breast_images_folder, output_folder, counter):
    """ Processes the breast images data and organizes images and masks """
    for birads_label in [0, 2, 4]:
        # Define image and mask folders for each BIRADS label
        image_folder = os.path.join(breast_images_folder, str(birads_label))
        mask_folder = os.path.join(breast_images_folder, str(birads_label))
        
        if not os.path.exists(image_folder) or not os.path.exists(mask_folder):
            continue

        for image_file in os.listdir(image_folder):
            if 'mask' in image_file:
                continue  # Skip mask files here
                
            mask_file = image_file.replace('.png', '_mask.png')
            mask_path = os.path.join(mask_folder, mask_file)
            
            if os.path.exists(mask_path):
                # Get next number for consistent naming
                next_num = counter.get_next_number()
                
                # Define destination paths
                dest_image_folder = os.path.join(output_folder, str(birads_label), 'images')
                dest_mask_folder = os.path.join(output_folder, str(birads_label), 'masks')
                
                os.makedirs(dest_image_folder, exist_ok=True)
                os.makedirs(dest_mask_folder, exist_ok=True)
                
                # Copy files with new standardized names
                shutil.copy(os.path.join(image_folder, image_file), 
                          os.path.join(dest_image_folder, f"{next_num}.png"))
                shutil.copy(mask_path, 
                          os.path.join(dest_mask_folder, f"{next_num}_mask.png"))

def main():
    busbra_folder = './BUSBRA'
    breast_folder = './BrEaST'
    breast_images_folder = './Dataset_BUSI_with_GT'
    output_folder = './dataset'
    
    # Initialize counter for consistent naming across all datasets
    counter = ImageCounter()
    
    # Process each dataset
    process_busbra_data(busbra_folder, output_folder, counter)
    process_breast_data(breast_folder, output_folder, counter)
    process_breast_images(breast_images_folder, output_folder, counter)
    
    print(f"Dataset parsed and organized successfully! Total images processed: {counter.current_count - 1}")

if __name__ == "__main__":
    main()
