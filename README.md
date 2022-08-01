# Web Scraping and Airtable Integration (Write and Update)

This project was done in conjunction with [Santropol Roulant](https://santropolroulant.org/) and features 2 executable scripts that scrape data from [Sous-Chef](https://github.com/savoirfairelinux/sous-chef), the Roulant's proprietary Web Platform, then writes to its corresponding database hosted on Airtable.

Each script features detailed comments that explain execution logic.

<br>

### [scrape_and_write.py](https://github.com/zack-tan/sroulant-data-automation/blob/main/scrape_and_write.py)

This script scrapes data from Sous-Chef, then writes the same into Airtable (with the corresponding month label).

### [airtable_aggregate_update.py](https://github.com/zack-tan/sroulant-data-automation/blob/main/airtable_aggregate_update.py) 

This script refreshes client-level aggregated meal data (YTD), working in tandem with an Airtable Automation to do so. Detailed comments are present in the script - high-level steps taken include:
- Ensuring all client names are present in aggregate table
- Refreshing lookup fields between client- and month-level aggregate tables

<br>

## Steps to use

Simply run *scrape_and_write.py* followed by *airtable_aggregate_update.py*. Each script features prompts that explain each step of the process to users. 

<br><hr>

### Other information
- The *pyinstaller* library was used to compile scripts into a .exe file.