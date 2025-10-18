# pytest -q
import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from PIL import Image

# -----------------------------------------------------------------------------
# TEST SUITE FOR compress.py
# -----------------------------------------------------------------------------
# This file contains unit tests for the image compression utility in compress.py.
# We use the pytest framework for execution and unittest.mock for simulating
# external dependencies like file I/O (File System) and image manipulation
# (Pillow library's Image object). This ensures tests are fast, reliable, and
# isolated from the file system.

# The tests cover:
# 1. Successful resizing and correct dimension calculation (Unit Testing).
# 2. Edge case handling (Percentage >= 100).
# 3. Robust error handling (FileNotFoundError, general Exceptions).
# 4. End-to-end user input validation in the main execution block (Integration Testing).

# Add the parent directory to the path to import the module under test
sys.path.append('../CompressJPG')

# Import the functions to be tested
from compress import resize_image_percentage
from compress import main

# --- Fixtures and Setup ---

# A pytest fixture to mock the PIL Image object for testing image operations.
# This ensures that tests do not require actual image files.
@pytest.fixture
def mock_image():
    """Mocks a PIL Image object with a predefined size (100x200) for consistent testing."""
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
    """Mocks Image.open to consistently return the mock_image fixture."""
    # Patching 'PIL.Image.open' to intercept the file opening
    with patch('PIL.Image.open', return_value=mock_image) as mock_open:
        yield mock_open

# --- Test Cases for resize_image_percentage ---

def test_successful_resize(mock_image, capsys):
    """
    Tests the primary success path: correct dimension calculation and file saving.
    
    Verifies that the image is resized correctly and saved in the expected format.
    """
    input_path = "input.jpg"
    output_path = "output_50.jpg"
    percentage = 50.0

    # Execute the function
    resize_image_percentage(input_path, output_path, percentage)

    # Assert 1 & 2: Check resize call. Original size (100, 200) * 0.5 = (50, 100)
    mock_image.resize.assert_called_once_with((50, 100))
    
    # Assert 3: Check save call on the resultant resized image mock
    resized_mock_image = mock_image.resize.return_value
    resized_mock_image.save.assert_called_once_with(output_path, "JPEG")
    
    # Assert 4: Check standard output for success confirmation
    captured = capsys.readouterr()
    assert f"The image was resized by {percentage}% and saved to: {output_path}" in captured.out


@pytest.mark.parametrize("percentage, expected_dims", [
    (25.0, (25, 50)),   # Quarter size reduction
    (99.0, (99, 198)),  # Near full size reduction, testing integer casting
    (10.0, (10, 20)),   # Significant reduction
])
def test_various_resize_percentages(mock_image, percentage, expected_dims):
    """
    Uses parametrization to verify correct dimension calculations across valid input ranges.
    """
    input_path = "input.jpg"
    output_path = f"output_{percentage}.jpg"

    # Execute the function
    resize_image_percentage(input_path, output_path, percentage)

    # Verify that the resize method received the calculated integer dimensions
    mock_image.resize.assert_called_once_with(expected_dims)
    
    # Ensure no early exit occurred and resizing was the chosen path
    mock_image.save.assert_not_called()


@pytest.mark.parametrize("percentage", [
    100.0, # Exact size
    101.0, # Upscaling
    200.0, # Significant upscaling
])
def test_no_resize_for_large_percentage(mock_image, capsys, percentage):
    """
    Tests the critical business logic that prevents upscaling or 100% resizing.
    The original image should be saved to the output path instead.
    """
    input_path = "input.jpg"
    output_path = f"output_{percentage}.jpg"

    # Execute the function
    resize_image_percentage(input_path, output_path, percentage)

    # 1. Verify that the 'resize' method was NOT called, ensuring early exit.
    mock_image.resize.assert_not_called()

    # 2. Verify that the original opened image was saved (instead of a resized one).
    mock_image.save.assert_called_once_with(output_path)
    
    # 3. Check the warning message output for user notification
    captured = capsys.readouterr()
    assert "The entered percentage is greater than or equal to 100%. No resizing will be performed." in captured.out


def test_file_not_found_error(mock_image_open, capsys):
    """
    Tests graceful error handling when the input file does not exist.
    """
    # Configure the mock open function to simulate a FileNotFoundError
    mock_image_open.side_effect = FileNotFoundError 
    input_path = "non_existent.jpg"
    output_path = "output.jpg"

    # Execute the function
    resize_image_percentage(input_path, output_path, 50)

    # Check the specific error message for FileNotFoundError
    captured = capsys.readouterr()
    assert f"Error: The file '{input_path}' was not found." in captured.out
    
    # Confirm no further image operations were attempted
    assert mock_image_open.call_count == 1
    # We must reset side_effect for other tests that use this autouse fixture
    mock_image_open.side_effect = None


def test_generic_processing_error(mock_image, mock_image_open, capsys):
    """
    Tests the generic exception handler for unexpected issues during PIL operations
    (e.g., corrupted data, memory errors).
    """
    input_path = "corrupt.jpg"
    output_path = "output.jpg"
    
    # Configure the mock 'resize' method to raise a generic exception
    mock_image.resize.side_effect = Exception("Simulated processing error")

    # Execute the function
    resize_image_percentage(input_path, output_path, 50)

    # Check the general error message output
    captured = capsys.readouterr()
    assert "An error occurred during image processing: Simulated processing error" in captured.out
    
    # Ensure the save method was never reached due to the preceding exception
    resized_mock_image = mock_image.resize.return_value
    resized_mock_image.save.assert_not_called()


# --- Test Cases for main() function (User Interaction Flow) ---

# We mock 'resize_image_percentage' to prevent actual image logic execution
@patch('compress.resize_image_percentage') 
# We mock 'builtins.input' to simulate user typing inputs
@patch('builtins.input')
def test_main_script_flow_success(mock_input, mock_resize_func, capsys):
    """
    Tests the end-to-end user experience for a successful run.
    
    Verifies that the main logic correctly gathers input paths and a valid percentage,
    and then calls the core function with the correct arguments.
    """
    # Sequence: Input Path, Output Path, Valid Percentage (50)
    mock_input.side_effect = [
        "test_in.jpg",      # 1. Input file path
        "test_out.jpg",     # 2. Output file path
        "50",               # 3. Valid percentage
    ]
    
    # Execute the user interaction flow
    main()
    
    # Assert that the core function was called with the final validated inputs
    mock_resize_func.assert_called_once_with("test_in.jpg", "test_out.jpg", 50.0)
    
    # Verify no validation error messages were printed
    captured = capsys.readouterr()
    assert "Invalid input" not in captured.out
    assert "must be greater than 0 and less than 100" not in captured.out


@patch('compress.resize_image_percentage')
@patch('builtins.input')
def test_main_script_input_validation(mock_input, mock_resize_func, capsys):
    """
    Tests the robustness of the percentage input validation loop.
    
    Simulates multiple invalid attempts (non-numeric, boundary conditions) before a success.
    """
    # Sequence of inputs: Path, Path, Invalid (text), Invalid (100), Invalid (0), Valid (75.5)
    mock_input.side_effect = [
        "test_in.jpg",      # 1. Input path (for main's prompt)
        "test_out.jpg",     # 2. Output path (for main's prompt)
        "abc",              # 3. Invalid: non-numeric (triggers ValueError)
        "100",              # 4. Invalid: >= 100 (triggers boundary check)
        "0",                # 5. Invalid: <= 0 (triggers boundary check)
        "75.5",             # 6. Valid percentage (exits loop)
    ]

    # Execute the main user interaction logic
    main() 

    # Verify that the core function was only called once with the final, valid input
    mock_resize_func.assert_called_once_with("test_in.jpg", "test_out.jpg", 75.5)
    
    # Check the standard output for all the expected error messages from the loop
    captured = capsys.readouterr()
    
    # Assert 3 error messages occurred (1 ValueError, 2 boundary errors)
    assert captured.out.count("Invalid input. Please enter a numerical value for the percentage.") == 1
    assert captured.out.count("The resizing percentage must be greater than 0 and less than 100 for proper reduction.") == 2