# Scraper_App

Welcome to **Scraper_App**, a powerful web scraping tool designed to extract valuable information from academic journals. This application is built with Python and utilizes the Selenium framework for web automation.

## Features

1. **Web Automation**: Navigate through journal pages, accept cookies, and log in seamlessly.
2. **Data Extraction**: Retrieve details like paper title, DOI, publication date, author details, and more.
3. **Image & Table Extraction**: Extract captions and links for images and tables present in the articles.
4. **Gender Prediction**: Predict the gender of authors based on their first names.
5. **File Handling**: Download images from articles and save them in a structured directory.
6. **Data Storage**: Store the scraped data in an Excel file for easy access and analysis.

## How to Use

1. **Setup**:
   - Install the required packages using `pip install -r requirements.txt`.
   - Ensure you have ChromeDriver installed and set in your system's PATH.

2. **Running the Scraper**:
   - Execute the `run.py` script to start the web scraper.

3. **Output**:
   - The scraped data will be saved in `data/output.xlsx`.
   - Downloaded images from articles will be stored in the `data/Photos` directory.

## Dependencies

- `requests`
- `selenium`
- `openpyxl`
- `pandas`
- `undetected_chromedriver`
- `urllib3`

## Contributing

Feel free to fork this repository, make changes, and submit pull requests. Any contributions, whether big or small, are greatly appreciated!
