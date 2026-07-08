# 🖼️ CompressJPG

[![License](https://img.shields.io/github/license/hrosicka/compress-jpg)](https://github.com/hrosicka/compress-jpg/blob/master/LICENSE)
[![CI](https://github.com/hrosicka/compress-jpg/actions/workflows/ci.yml/badge.svg)](https://github.com/hrosicka/compress-jpg/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![PyPI - Downloads](https://img.shields.io/badge/pypi--not--published-lightgrey)](https://pypi.org/)

> The perfect helper for shrinking your JPG images – because sometimes less really is more!

## 📦 About the Project

**compress-jpg** is a simple yet handy Python script that lets you shrink JPG images to your desired size (by percentage). Just provide the path to your image, choose where to save the result, and specify the percentage for resizing. Done! 🏆

> No more overly large images in emails, presentations, or on your website! 🚀

## ⚙️ How Does It Work?

All the magic happens in [`compress.py`](compress.py):

- Uses the [Pillow](https://python-pillow.org) (PIL) library for image manipulation
- Shrinks images based on the user-defined percentage
- Saves the result as a new JPG file
- If you enter 100% or more, the image won’t be changed (because we know our math 😄)

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hrosicka/compress-jpg.git
   cd compress-jpg
   ```
2. Install the required packages:
   ```bash
   pip install Pillow
   ```

## 🚀 Usage

Run the script in your terminal:

```bash
python compress.py
```

And then just follow the on-screen instructions:

1. Enter the path to your input JPG file (don’t worry, it won’t bite! 🦷)
2. Specify where to save the output file
3. Enter the resizing percentage (e.g., 50 for half the size)

## 💡 Example

```
Enter the path to the input JPG image: /path/to/your/image.jpg
Enter the path to save the resized image (including the .jpg filename): /path/to/output/image_small.jpg
Enter the resizing percentage (e.g., 50 for 50%): 50
The image was resized by 50% and saved to: /path/to/output/image_small.jpg
```

## ❓ FAQ

- **Does it support only JPG?** Yes, for now it’s a JPG specialist. PNG and other formats are still waiting for their time to shine.
- **What if I enter 100% or more?** The script will let you know and won’t resize the image – because sometimes 100% is just enough!

## 👩‍💻 Author

Lovingly crafted by [Hanka Robovska](https://github.com/hrosicka) 👩‍🔬

## 📄 License

MIT – feel free to use, modify, and share as your heart desires! 😉

---

*Shrink wisely. Every byte counts!* 🧮✨
