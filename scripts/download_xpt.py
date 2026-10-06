import requests
import re
from urllib.parse import urljoin
from html import unescape
from rich import print as rprint
import datetime

# Lucas Kearns
# 5 Oct 2026

# Scrape NHANES data from website to avoid gratuitous downloading of each xpt file


# Logging date for file generation
date = datetime.datetime.now()
str_date = date.strftime("%Y-%M-%d")


############################################################
## Parse Initial response, extract cycle specific data links
############################################################

nhanes_url = "https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx"
params = {"Cycle": "2021-2023"}

nhanes_response = requests.get(nhanes_url, params=params)
if nhanes_response.status_code != 200:
    raise Exception(
        f"Server returned a response with status code {nhanes_response.status_code}"
    )
nhanes_cycle_text = nhanes_response.text


data_pages = re.findall(r"a href=.+datapage\.aspx.+", nhanes_cycle_text)
current_data_pages = [link for link in data_pages if params["Cycle"] in link]
unq_current_data_pages = set(current_data_pages)
relative_curr_links = re.findall(r'"([^"]+)"', "".join(unq_current_data_pages))


abs_curr_links = [urljoin(nhanes_url, unescape(link)) for link in relative_curr_links]
print("Scraper identified the following links")
rprint(abs_curr_links)

#################################################################
## Iterate through absolute data links and identify xpt file urls
#################################################################

for link in abs_curr_links:
    print(f"Scraping {link}")

    link_response = requests.get()

    break


#############################
## Save each xpt file to disk
#############################
