# Import required libraries
from PIL import Image  # Pillow library for image processing operations
import os  # Standard library for interacting with the operating system (included for completeness)

def resize_image_percentage(input_path, output_path, percentage):
    """
    Resizes a JPG image based on a given percentage and saves it to a specified path.

    Args:
        input_path (str): The file path to the input JPG image.
        output_path (str): The file path where the resized image will be saved.
        percentage (float): The percentage by which the image should be scaled 
                            (e.g., 50 for 50% of the original size).
    """
    # Use a try-except block to gracefully handle file I/O and image processing errors
    try:
        # 1. Open the image file
        img = Image.open(input_path)
        # Get the original width and height of the image
        original_width, original_height = img.size

        # 2. Check for percentage validity (no upscaling or 100% resizing)
        if percentage >= 100:
            # Inform the user that no resizing will occur
            print("The entered percentage is greater than or equal to 100%. No resizing will be performed.")
            # Save the original image to the output path
            img.save(output_path)
            return  # Exit the function

        # 3. Calculate new dimensions
        # Convert the percentage into a scaling factor (e.g., 50 -> 0.5)
        resize_factor = percentage / 100.0
        # Calculate the new width and height, casting to integer values
        new_width = int(original_width * resize_factor)
        new_height = int(original_height * resize_factor)
        
        # 4. Resize and Save
        # Perform the actual image resizing operation
        resized_img = img.resize((new_width, new_height))
        # Save the resized image, explicitly specifying JPEG format for compatibility
        resized_img.save(output_path, "JPEG")
        # Confirmation message for successful operation
        print(f"The image was resized by {percentage}% and saved to: {output_path}")

    # Handle the specific case where the input file does not exist
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
    # Catch any other unexpected errors during processing
    except Exception as e:
        print(f"An error occurred during image processing: {e}")

# Entry point of the script
if __name__ == "__main__":
    # 1. Get file paths from the user
    input_file = input("Enter the path to the input JPG image: ")
    output_file = input("Enter the path to save the resized image (including the .jpg filename): ")
    
    # 2. Input validation loop for the resizing percentage
    while True:
        try:
            # Prompt for percentage and attempt to convert input to a floating-point number
            resize_percentage = float(input("Enter the resizing percentage (e.g., 50 for 50%): "))
            
            # Ensure the percentage is within the desired range (0 < p < 100) for reduction
            if 0 < resize_percentage < 100:
                break  # Valid input received, exit the loop
            else:
                # Error message for out-of-range input
                print("The resizing percentage must be greater than 0 and less than 100 for proper reduction.")
        
        # Handle the error if the user enters non-numeric input
        except ValueError:
            print("Invalid input. Please enter a numerical value for the percentage.")

    # 3. Execute the main function with validated inputs
    resize_image_percentage(input_file, output_file, resize_percentage)