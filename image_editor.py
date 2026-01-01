import os
from dotenv import load_dotenv
import google.genai as genai
from PIL import Image

# Load environment variables from the .env file
load_dotenv()

# Read the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate the API key
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    raise ValueError(
        "GEMINI_API_KEY not found or not set. "
        "Please create a .env file and add your API key: "
        "GEMINI_API_KEY='YOUR_API_KEY'"
    )

# Initialize the Gemini client (API key is read from the environment).
client = genai.Client()

def get_detailed_prompt() -> str:
    """
    Generates a detailed prompt for the image editing API (Gemini).
    """
    return (
        "You are an AI image processing expert integrated into a car's computer system. Your task is to clean up the image displayed on the infotainment screen. "
        "**CONTEXT:** "
        "The input image is a photograph of a car's interior, showing an infotainment screen. This screen displays a live feed from a dirty rear-view camera. Importantly, the camera view includes a graphical overlay on the left side which displays data from the car's parking sensors. These indicators light up to show when objects are close to the car. "
        "**PRIMARY TASK: CLEAN THE CAMERA VIEW** "
        "1. Identify the area of the photograph that represents the camera view on the screen. "
        "2. Within that area, identify smudges, dirt, and water spots that are on the camera lens. "
        "3. Aggressively remove these lens artifacts. "
        "4. As you clean, you must perfectly preserve and maintain the realism of all underlying details in the outdoor scene, especially people, animals, buildings, and ground textures. "
        "**CRITICAL CONSTRAINT: IGNORE THE CAR INTERIOR** "
        "- You MUST NOT make any changes to the parts of the image showing the car's interior. The dashboard, screen bezel, air vents, etc., must be left completely untouched. "
        "**CONDITIONAL LOGIC FOR SAFETY:** "
        "- First, check the status of the visual parking sensor overlay on the left of the camera view. "
        "- **IF** the sensor overlay is lit up (e.g., shows red or yellow bars), it signifies a nearby object. In this case, you must be extremely cautious. The preservation of any figures (especially people) or objects in the scene takes absolute priority over cleaning. "
        "- **IF** the sensor overlay is NOT lit up, you can proceed with a more confident cleaning of the entire camera view, while still adhering to all preservation rules. "
        "- In all cases, preserving human figures is the most important objective. "
        "Return ONLY the processed image."
    )

def edit_single_image(input_path: str, output_path: str):
    """
    Edits a single image using the Gemini Image Generation API.

    Args:
        input_path: The path to the input image.
        output_path: The path to save the edited image.
    """
    print(f"Processing image: {input_path}")

    try:
        # Load the image with PIL (Pillow)
        img = Image.open(input_path)

        # Send the image and prompt to Gemini via the client
        print("Sending request to Gemini Image Generation API...")
        # Use the global client
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview", # Model name already updated
            contents=[get_detailed_prompt(), img],
        )

        # Find and save the generated image from the response
        image_saved = False
        if response.parts:
            for part in response.parts:
                if part.text is not None:
                    print(f"Gemini returned text content: {part.text}")
                    # If text is returned, it may indicate no image was generated
                    # or that the text describes the problem/result.
                    # We do not expect text for image generation.
                elif part.inline_data is not None:
                    try:
                        generated_image = part.as_image()
                        if generated_image: # Ensure the image is not None
                            generated_image.save(output_path)
                            print(f"Successfully saved processed image to: {output_path}")
                            image_saved = True
                            break  # Exit once an image has been saved
                        else:
                            print("Gemini returned inline_data but part.as_image() returned None.")
                    except ValueError as ve:
                        print(f"Error extracting image from part: {ve}")
                    except Exception as ex:
                        print(f"An unexpected error occurred while processing image part: {ex}")
        
        if not image_saved:
            print("Gemini API did not return a valid image in its response or an error occurred during extraction.")
            # For debugging, it can be useful to see the full text if present
            if response.text:
                print("Full Gemini response (text for debugging):", response.text)

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    # Create the output folder if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Define input and output folders
    input_dir = "input"
    output_dir = "output"

    # Allowed image extensions (lowercase)
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

    # Gather files, filter for images, and sort them
    all_files = os.listdir(input_dir)
    image_files = sorted([f for f in all_files if f.lower().endswith(IMAGE_EXTENSIONS)])

    # Process all image files
    files_to_process = image_files
    print(f"Found {len(image_files)} images. Processing all of them.")

    for filename in files_to_process:
        input_file_path = os.path.join(input_dir, filename)
        
        # Build the output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}-processed{ext}"
        output_file_path = os.path.join(output_dir, output_filename)

        # Run the edit for the image
        edit_single_image(input_file_path, output_file_path)
    
    print("\nProcessing complete for the first 8 images.")
