from PIL import Image
import os

def resize_image_percentage(input_path, output_path, percentage):
    """
    Resizes a JPG image based on a given percentage and saves it.

    Args:
        input_path (str): The path to the input JPG file.
        output_path (str): The path where the resized image will be saved.
        percentage (float): The percentage by which the image should be resized (e.g., 50 for 50%).
    """
    try:
        img = Image.open(input_path)
        original_width, original_height = img.size

        if percentage >= 100:
            print("The entered percentage is greater than or equal to 100%. No resizing will be performed.")
            img.save(output_path)
            return

        resize_factor = percentage / 100.0
        new_width = int(original_width * resize_factor)
        new_height = int(original_height * resize_factor)
        resized_img = img.resize((new_width, new_height))
        resized_img.save(output_path, "JPEG")
        print(f"The image was resized by {percentage}% and saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = input("Enter the path to the input JPG image: ")
    output_file = input("Enter the path to save the resized image (including the .jpg filename): ")
    while True:
        try:
            resize_percentage = float(input("Enter the resizing percentage (e.g., 50 for 50%): "))
            if 0 < resize_percentage < 100:
                break
            else:
                print("The resizing percentage must be greater than 0 and less than 100.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    resize_image_percentage(input_file, output_file, resize_percentage)