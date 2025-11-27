# Real Estate Market Trends Scraper

## Overview
This project was developed to automate the extraction of weekly market data for the Western Australia (Perth) real estate market. The client required a historical dataset spanning **4 years (2020-2024)**, extracted from unstructured HTML weekly reports.

## The Challenge
The source website had inconsistent HTML structures and varying text patterns over the 4-year period. A simple HTML parser would fail. The solution required a robust **Regex-based** extraction logic to identify data points regardless of the surrounding text format.

## Features
- **Automated Pagination:** Crawls through 4+ years of weekly archives automatically.
- **Robust Pattern Matching:** Uses advanced **Regular Expressions (Regex)** to catch variations in report phrasing (e.g., "reporting X transactions" vs "X transactions reported").
- **Data structuring:** Converts raw unstructured text into a clean, analyzed **Pandas DataFrame**.
- **Export:** Delivers the final output in CSV/Excel format ready for financial modeling.

## Technologies
- **Python 3.x**
- **BeautifulSoup4** (HTML Parsing)
- **Pandas** (Data Manipulation)
- **Regex** (Pattern Recognition)

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
Run the scraper:
   ```bash
   python scraper.py
   ```
Output will be saved to data.csv.
