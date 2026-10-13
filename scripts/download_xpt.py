import requests
import re
from urllib.parse import urljoin, urlparse, parse_qs
from html import unescape
from rich import print as rprint
from rich.console import Console
import datetime
import os
import sys

# Lucas Kearns
# 5 Oct 2026

# Scrape NHANES data from website to avoid gratuitous downloading of each xpt file


###########################################################
## Define variables and objects used downstream in the code
###########################################################

console = Console()

# Logging date for file generation
date = datetime.datetime.now()
str_date = date.strftime("%Y-%m-%d")

nhanes_url = "https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx"
params = {"Cycle": "2021-2023"}

output_file_path = "/Users/lucaskearns/personal_projects/nhanes/data"

######################################################
## Parse parent url, extract cycle specific data links
######################################################


console.rule("Querying Parent URL", style="white")
console.print(nhanes_url, justify="center")
console.print(params, justify="center")

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
console.rule("Scraping identified the following links", style="white")
console.print(abs_curr_links, justify="center")

#################################################################
## Iterate through absolute data links and identify xpt file urls
#################################################################

xpt_urls = {}

console.print("\nScraping identified links\n--------------------", justify="center")
for link in abs_curr_links:
    console.print(f"Querying {link}", justify="center")

    link_response = requests.get(link)
    data_text = link_response.text

    xpt_links = re.findall(r"a href=.+\.xpt.+", data_text)
    relative_xpt_links = re.findall(r'"([^"]+)"', "".join(xpt_links))
    abs_xpt_links = [urljoin(nhanes_url, unescape(link)) for link in relative_xpt_links]

    xpt_urls[link] = abs_xpt_links

console.print("Located xpt files: ", justify="center")
console.print(xpt_urls, justify="center")

#############################
## Save each xpt file to disk
#############################


generated_dir = os.path.join(
    output_file_path, f"nhanes_{params['Cycle']}_date_{str_date}"
)

if not os.path.exists(generated_dir):
    os.mkdir(generated_dir)


for link in xpt_urls.keys():
    console.rule(f"Downloading xpt files from {link}", style="blue")

    url_params = parse_qs(urlparse(link).query)

    comp_fname = (
        f"{generated_dir}/{url_params['Cycle'][0]}_{url_params['Component'][0]}"
    )

    xpt_files = xpt_urls[link]

    if len(xpt_files) != 0:
        if not os.path.exists(comp_fname):
            os.mkdir(comp_fname)

        for f in xpt_files:
            xpt_response = requests.get(f)
            xpt_out_name = f"{comp_fname}/{f.split('/')[-1]}"

            console.print(f"--\nDownloading from {f}\nWriting to: {xpt_out_name}")
            with open(xpt_out_name, "wb") as open_f:
                open_f.write(xpt_response.content)
