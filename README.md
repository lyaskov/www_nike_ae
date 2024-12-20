# Nike Product Scraper

## Description
This project is a web scraping script designed to extract data from the [Nike.ae](https://www.nike.ae) website. The script collects product information, including name, price, images, description, and specifications. The results are saved in a CSV file.

## Key Features
- Extracts product information (name, price, images, description, sizes, categories).
- Supports multithreading for faster data collection.
- Saves results in a timestamped CSV file.

## Installation

### Requirements
- Python 3.8+
- Installed libraries:
  - `requests`
  - `beautifulsoup4`
  - `lxml`

### Installing Dependencies
Install the required dependencies with the following command:
```bash
pip install -r requirements.txt
```

Create a `requirements.txt` file and add the following:
```
requests
beautifulsoup4
lxml
```

## Usage

### Running the Script
1. Run the script:
```bash
python scraper.py
```
2. Upon completion, data will be exported to a CSV file named `output_<timestamp>.csv`.

### Configuration
- To change the starting page, update the `start_url` variable.
- Set the number of threads in the `num_threads` variable.

## Project Structure
```
/
├── scraper.py           # Main script for web scraping
├── scrape.py            # Module with data processing functions
├── requirements.txt     # Project dependencies
└── output_*.csv         # Results (generated automatically)
```

## Sample Data
Example of extracted data:
```json
{
  "name": "Jordan Women's Tank",
  "price": "AED 200",
  "sale_price": "AED 180",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "description": "Short product description.",
  "available_sizes": ["S", "M", "L"],
  "brand": "Nike",
  "category": "Women's Clothing"
}
```

## Notes
- The project includes error handling and logging for debugging purposes.
- Ensure compliance with the website's terms of use when performing web scraping.
