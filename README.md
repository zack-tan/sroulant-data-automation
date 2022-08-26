# Automated data collection through Web Scraping and Airtable Integration

This project was done in conjunction with [Santropol Roulant](https://santropolroulant.org/) and features 2 scripts that scrape data from [Sous-Chef](https://github.com/savoirfairelinux/sous-chef), the Roulant's proprietary Web Platform, cleans and transforms it, then writes to an Airtable database.

Each script is written to be interactive and user-friendly, featuring several prompts with error handling. These have been compiled and distributed as .exe files through the use of the *pyinstaller* library.

### [scrape_and_write.py](https://github.com/zack-tan/sroulant-data-automation/blob/main/scrape_and_write.py)

This script scrapes meal order data from Sous-Chef then writes it into Airtable.

### [airtable_aggregate_update.py](https://github.com/zack-tan/sroulant-data-automation/blob/main/airtable_aggregate_update.py) 

This script refreshes client-level aggregated meal order data (YTD), working in tandem with an Airtable Automation to do so. <br>

High-level steps taken include:
- Ensuring client names tally across all tables within Airtable
- Refreshing lookup fields between client- and month-level aggregate tables

<br>
All scripts include detailed comments that explain execution logic.

<br>

## Steps to use

Simply run *scrape_and_write.py* followed by *airtable_aggregate_update.py*. Each script features prompts that explain each step of the process to users. 

<hr>

### Other information
- The *pyinstaller* library was used to compile scripts into a .exe file.