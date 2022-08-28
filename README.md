# Streamlining data collection & update processes 

This project was done in conjunction with [Santropol Roulant](https://santropolroulant.org/) and helps improve the data collection process through automation via web scraping and integration with Airtable.

It features 2 scripts that scrape data from [Sous-Chef](https://github.com/savoirfairelinux/sous-chef), the Roulant's proprietary Web Platform, cleans and transforms it, then writes to an Airtable database.

Each script is written to be interactive and user-friendly, featuring several prompts with error handling. These have been compiled and distributed as .exe files through the use of the [pyinstaller](https://pyinstaller.org/en/stable/) library.

## Codefiles

### [scrape_and_write.py](https://github.com/zack-tan/sroulant-data-automation/blob/main/scrape_and_write.py)

This script scrapes meal order data (at month-level) from Sous-Chef then writes the same into the corresponding Airtable table.

### [airtable_aggregate_update.py](https://github.com/zack-tan/sroulant-data-automation/blob/main/airtable_aggregate_update.py) 

This script refreshes client-level aggregated meal order data (YTD) within Airtable, working in tandem with [Automations](https://support.airtable.com/docs/automations-overview) to do so. 

High-level steps taken include:
- Ensuring client names tally across all tables within Airtable
- Refreshing lookup fields between client- and month-level aggregate tables

*All scripts include comments within the code that explain execution logic in detail.*

## How to use

1. Both these scripts have been provided as executable files (.exe) along with a config file. Please store these in the same folder.
2. Before running either script, open the config file and check to ensure all credentials and database/table names are correct.
3. To populate Airtable with meal data (month-level), run *scrape_and_write.py/exe* and follow the prompts. 
4. To refresh the client-level meal data table, run *airtable_aggregate_update.py/exe*. Both these scripts are usually run together in this sequence of steps.

*Each script features detailed prompts & error handling that explain each step of the process. If you need another copy of the config file or for either script to be re-compiled, feel free to contact [me](https://bit.ly/linkedin-zacktan).*

<hr>

This repository was made open source upon request of and with permission from Santropol Roulant.