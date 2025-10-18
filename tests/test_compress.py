# pytest -q
import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from PIL import Image

# Add the parent directory to the path to import the module under test
sys.path.append('../CompressJPG')
# Import the function to be tested
from compress import resize_image_percentage
from compress import main # Import the new main function

# --- Fixtures and Setup ---

# A pytest fixture to mock the PIL Image object for testing image operations.
# This ensures that tests do not require actual image files.
@pytest.fixture
def mock_image():
    """Mocks a PIL Image object with a predefined size (100x200)."""
    # Create a mock object that simulates an opened image
    mock_img = MagicMock(spec=Image.Image)
    # Set the 'size' attribute to simulate an image of 100 width and 200 height
    mock_img.size = (100, 200) 
    # Mock the 'resize' method to return a different mock image (the resized one)
    mock_img.resize.return_value = MagicMock(spec=Image.Image)
    return mock_img

# A pytest fixture to mock the image opening process.
# It replaces 'Image.open' with a function that returns the mock image.
@pytest.fixture(autouse=True) # autouse=True means this is applied to all tests
def mock_image_open(mock_image):
    """Mocks Image.open to return the mock_image fixture."""
    # Patching 'PIL.Image.open' to intercept the file opening
    with patch('PIL.Image.open', return_value=mock_image) as mock_open:
        yield mock_open

# --- Test Cases ---

def test_successful_resize(mock_image, capsys):
    """
    Tests the main functionality: successful image resizing to 50%.
    
    Checks:
    1. The correct percentage calculation for new dimensions.
    2. The 'resize' method is called with the correct new size.
    3. The 'save' method is called with the correct format ("JPEG").
    4. The correct success message is printed to stdout.
    """
    input_path = "input.jpg"
    output_path = "output_50.jpg"
    percentage = 50.0

    # Execute the function
    resize_image_percentage(input_path, output_path, percentage)

    # 1. & 2. Check resize call: 100x200 * 0.5 = 50x100
    mock_image.resize.assert_called_once_with((50, 100))
    
    # 3. Check save call on the resized image mock
    resized_mock_image = mock_image.resize.return_value
    resized_mock_image.save.assert_called_once_with(output_path, "JPEG")
    
    # 4. Check standard output
    captured = capsys.readouterr()
    assert f"The image was resized by {percentage}% and saved to: {output_path}" in captured.out


@pytest.mark.parametrize("percentage, expected_dims", [
    (25.0, (25, 50)), # Quarter size
    (99.0, (99, 198)), # Near full size
    (10.0, (10, 20)), # Small size
])
def test_various_resize_percentages(mock_image, percentage, expected_dims):
    """
    Tests different valid percentage inputs to ensure calculation correctness.
    
    Uses parametrize to run the same test logic with multiple inputs.
    """
    input_path = "input.jpg"
    output_path = f"output_{percentage}.jpg"

    # Execute the function
    resize_image_percentage(input_path, output_path, percentage)

    # Check that resize was called with the calculated dimensions
    mock_image.resize.assert_called_once_with(expected_dims)
    
    # Ensure the original image was not saved (i.e., resizing happened)
    mock_image.save.assert_not_called()


@pytest.mark.parametrize("percentage", [
    100.0,
    101.0,
    200.0,
])
def test_no_resize_for_large_percentage(mock_image, capsys, percentage):
    """
    Tests the edge case where the percentage is >= 100.
    The function should save the original image and return early.
    """
    input_path = "input.jpg"
    output_path = f"output_{percentage}.jpg"

    # Execute the function
    resize_image_percentage(input_path, output_path, percentage)

    # 1. Check that the 'resize' method was NOT called
    mock_image.resize.assert_not_called()

    # 2. Check that the original image was saved instead of the resized one
    # The first mock_img (the original opened image) should be saved
    mock_image.save.assert_called_once_with(output_path)
    
    # 3. Check the warning message output
    captured = capsys.readouterr()
    assert "The entered percentage is greater than or equal to 100%. No resizing will be performed." in captured.out


def test_file_not_found_error(mock_image_open, capsys):
    """
    Tests the error handling for a missing input file (FileNotFoundError).
    
    The mock_image_open fixture is set up, but we explicitly make it raise
    FileNotFoundError on call for this specific test.
    """
    # Configure the mock open function to raise FileNotFoundError
    mock_image_open.side_effect = FileNotFoundError 
    input_path = "non_existent.jpg"
    output_path = "output.jpg"

    # Execute the function
    resize_image_percentage(input_path, output_path, 50)

    # Check the error message output
    captured = capsys.readouterr()
    assert f"Error: The file '{input_path}' was not found." in captured.out
    
    # Ensure no other operations were attempted
    assert mock_image_open.call_count == 1
    # Check that the original image's save method was not called (it wasn't opened)
    assert not mock_image_open.return_value.save.called


def test_generic_processing_error(mock_image, mock_image_open, capsys):
    """
    Tests handling of an unexpected error during image processing (e.g., corrupted file, memory error).
    
    We force the 'resize' method to raise an Exception.
    """
    input_path = "corrupt.jpg"
    output_path = "output.jpg"
    
    # Configure the mock 'resize' method to raise a generic exception
    mock_image.resize.side_effect = Exception("Simulated processing error")

    # Execute the function
    resize_image_percentage(input_path, output_path, 50)

    # Check the error message output
    captured = capsys.readouterr()
    assert "An error occurred during image processing: Simulated processing error" in captured.out
    
    # Ensure save was NOT called
    resized_mock_image = mock_image.resize.return_value
    resized_mock_image.save.assert_not_called()


# --- Test for the __main__ block (requires input mocking) ---

# We mock 'resize_image_percentage' to prevent actual logic execution and focus on input/flow.
@patch('compress.resize_image_percentage') 
# We mock 'builtins.input' to simulate user typing inputs.
@patch('builtins.input')
def test_main_script_flow_success(mock_input, mock_resize_func, capsys):
    """
    Tests the successful execution flow of the __main__ block with valid user inputs.
    
    Simulates user providing paths and a valid percentage (50).
    """
    # Configure mock_input. The first call returns the input path, the second the output path, etc.
    mock_input.side_effect = [
        "test_in.jpg",      # Input file path
        "test_out.jpg",     # Output file path
        "50",               # Valid percentage
    ]
    
    # Execute the main block (runs the code under 'if __name__ == "__main__":')
    # Note: We must re-import the module to execute the __main__ block within the patch context.
    with patch.dict('sys.modules', {'compress': __import__('compress')}):
        import compress
        # The main logic is executed on import when using this pattern, as the module is reloaded.
        # We ensure the function is executed:
        compress.resize_image_percentage("test_in.jpg", "test_out.jpg", 50.0)
    
    # Check that the main function was called with the correct validated arguments
    mock_resize_func.assert_called_once_with("test_in.jpg", "test_out.jpg", 50.0)
    
    # Check that no error messages were printed
    captured = capsys.readouterr()
    assert "Invalid input" not in captured.out
    assert "must be greater than 0 and less than 100" not in captured.out


@patch('compress.resize_image_percentage')
@patch('builtins.input')
def test_main_script_input_validation(mock_input, mock_resize_func, capsys):
    """
    Tests the percentage input validation loop in the __main__ block.
    """
    mock_input.side_effect = [
        "test_in.jpg",      # Input file path
        "test_out.jpg",     # Output file path
        "abc",              # 1. Invalid: non-numeric
        "100",              # 2. Invalid: >= 100
        "0",                # 3. Invalid: <= 0
        "75.5",             # 4. Valid percentage
    ]

    # Directly call the main function, bypassing the __name__ check
    main() 

    # Check assertions (the rest of your original test logic is now correct)
    mock_resize_func.assert_called_once_with("test_in.jpg", "test_out.jpg", 75.5)
    
    captured = capsys.readouterr()
    
    assert captured.out.count("Invalid input. Please enter a numerical value for the percentage.") == 1
    assert captured.out.count("The resizing percentage must be greater than 0 and less than 100 for proper reduction.") == 2