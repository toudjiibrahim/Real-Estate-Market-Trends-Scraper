import os
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import time
import re


# --------Configuration--------
BASE_URL = "https://reiwa.com.au"
# the end point for the search results with pagination
MAIN_ENDPOINT : str = "/the-wa-market/resources/?terms=Perth+Market+Snapshot+for+the+week+ending&types=news&sortBy=date-desc&page="

DATA_FILE : str = "data.csv"
COL_NAMES : list[str] = ["Week Ending", "Sales Transactions", "Stock for Sale", "Properties for Rent", "Properties Leased", "Source"]

# initialized global dataframe
data : pd.DataFrame = pd.DataFrame(columns=COL_NAMES)


def get_snapshot_data_points(url:str, week_ending:str):
    """
    Fetches a specific weekly report page and extracts key data points using Regex.
    Handles variations in HTML structure and text phrasing.
    """
    global data
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[Error] Could not fetch page: {url}")
            return

        soup = BeautifulSoup(response.content, "lxml")
        print(f"Processing report: {week_ending} ")
        
        # Locate the main content container
        main_container = soup.find("div",{"class":"o-wysiwyg"})
        if not main_container:
            print(f" - No content div found for {week_ending}")
            return
        
        content = main_container.text

        # --- Regex Pattern Matching ---
        # The site changes phrasing over years, so we use fallback patterns.

        # 1. Sales Transactions
        sales_transactions = re.search(r"REIWA members reporting ([\d,\. ]+) transactions",content)
        if not sales_transactions:
            #Fallback pattern
            sales_transactions = re.search(r"reporting\s*([\d,\. ]+)\s*transactions",content, re.DOTALL)

        # 2. Stock for Sale
        stock_for_sale = re.search(r"There were ([\d,\. ]+) properties for sale in Perth",content)
        if not stock_for_sale:
            stock_for_sale = re.search(r"([\d,\. ]+)\s*properties\s*for\s*sale\s*in\s*Perth",content, re.DOTALL)

        # 3. Properties for Rent
        properties_for_rent = re.search(r" REIWA members reported there were ([\d,\. ]+) properties for rent in Perth",content)
        if not properties_for_rent:
            properties_for_rent = re.search(r"([\d,\. ]+)\s*properties\s*for\s*rent\s*in\s*Perth",content, re.DOTALL)
        
        # 4. Properties Leased
        properties_leased = re.search(r"REIWA members reported ([\d,\. ]+) properties leased",content)
        if not properties_leased:
            properties_leased = re.search(r"([\d,\. ]+)\s*properties\s*leased",content, re.DOTALL)
        
        # Structure the data row
        data_row : dict = {
            "Week Ending": week_ending, 
            "Sales Transactions": sales_transactions.group(1).replace(",","").strip() if sales_transactions else None, 
            "Stock for Sale": stock_for_sale.group(1).replace(",","").strip() if stock_for_sale else None, 
            "Properties for Rent": properties_for_rent.group(1).replace(",","").strip() if properties_for_rent else None, 
            "Properties Leased": properties_leased.group(1).replace(",","").strip() if properties_leased else None, 
            "Source":url
        }


        # Append to main dataset
        data = pd.concat([data, pd.DataFrame([data_row])], ignore_index=True)

        
        # Print confirmation        
        print(f" - Extracted: {data_row['Sales Transactions']} transactions")


    except Exception as e:
        print(f"Error occurred processing {week_ending}:\n{e}")

def start_scraper():
    """
    Main execution loop. Handles pagination of the archive pages.
    """
    global data
    page_number = 1
    print("---- Scraper started ----")
    try:
        while True:
            # Construct the pagination url
            target_url = BASE_URL+MAIN_ENDPOINT+str(page_number)
            print(f"\n--- Fetching Archive Page {page_number} ---")

            main_page = requests.get(target_url)
            soup = BeautifulSoup(main_page.content,"lxml")

            # Find the list of report cards
            market_snapshots = soup.find("ul", {"class":"l-rhythm"})

            if not market_snapshots:
                print(f"No more results found at page {page_number}. Stopping.")
                break

            items = market_snapshots.findAll("li",recursive = False)
            print(f"found : {len(items)} items on this page")

            valid_reports_count = 0

            for m_snapshot in items:
                header = m_snapshot.find("header")
                if not header:
                    continue

                link_element = header.find("a")
                if link_element:
                    # Extract date from title to verify it's a market snapshot
                    week_ending_match = re.search(r"week ending (\d{1,2} [A-Za-z]+ \d{4})",link_element.text)
                    
                    if week_ending_match:
                        week_ending = week_ending_match.group(1)
                        report_url = f"{BASE_URL}{link_element.get("href")}"

                        # Trigger the extraction for this specific report
                        get_snapshot_data_points(report_url, week_ending)
                        valid_reports_count += 1

            if valid_reports_count == 0:
                print("No valid 'Market Snapshot' reports found on this page. Continuing...")
            
            page_number +=1
            time.sleep(2) # Respectfull delay to avoid IP ban
            
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        # Save data even if the script errors out or stops
        if not data.empty:
            data.to_csv(DATA_FILE, index=False)
            print(f"\nSUCCESS: Data saved to {DATA_FILE} with {len(data)} records.")
        else:
            print("\nFinished. No data extracted.")




if __name__ == "__main__":
    start_scraper()
