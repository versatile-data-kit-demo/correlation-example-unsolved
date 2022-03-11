# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import logging
import datefinder
from datetime import datetime
import time
import webscrape
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Scrape bad Amazon Reviews for one of the most popular Yankee candles on Amazon
    and ingest them into a cloud Trino database.
    """

    log.info(f"Starting job step {__name__}")

    # Create/retrieve the data job property storing latest ingested date for yankee_candle_reviews table.
    # If the property does not exist, set it to "2020-01-01" (around the start of the pandemic).
    props = job_input.get_all_properties()
    if "last_date_amazon" in props:
        pass
    else:
        # <- !!! INITIALIZE THE "last_date_amazon" PROPERTY TO '2020-01-01' !!!

    # Initialize variables
    i = 1
    rev_result = []
    date_result = []
    # Date to start iterating from = current date (in the format "2020-01-01")
    date = datetime.now().strftime("%Y-%m-%d")

    # Go through the review pages and scrape reviews
    while date > props["last_date_amazon"]:
        log.info(f'Rendering page {i}...')
        # Parameterize the URL to iterate over the pages
        url = f"https://www.amazon.com/Yankee-Candle-Large-Balsam-Cedar/product-reviews/B000JDGC78/ref=cm_cr_arp_d_\
            viewopt_srt?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber={i}&sortBy=recent"

        # Get HTML code into a BeautifulSoup object
        soup = webscrape.html_code(url)
        # Get the reviews and dates for the current page
        rev_page = webscrape.cus_rev(soup)
        date_page = webscrape.rev_date(soup)[2:]

        # Append reviews text into a list removing the empty reviews
        for j in rev_page:
            if j.strip() == "" or j.strip() == "The media could not be loaded.":
                pass
            else:
                rev_result.append(j.strip())
        log.info(len(rev_result))

        # Append review dates into a list by extracting the date from text
        for d in date_page:
            if d.strip() == "":
                pass
            else:
                # Initially, dates are in the format "Reviewed in the United States on February 14, 2022"
                # datefinder package extracts the date from the text and converts it to datetime object
                date_match = datefinder.find_dates(d)
                for date in date_match:
                    # Convert to string
                    date = date.strftime("%Y-%m-%d")
                    date_result.append(date)
        log.info(len(date_result))

        # In each page, check whether there are more dates than reviews (empty reviews with photo only) and remove them
        while len(rev_result) < len(date_result):
            date_result.pop(-1)

        # Go to the next page
        i += 1

    # Create a pandas dataframe with the review text and dates
    df = pd.DataFrame(zip(date_result, rev_result), columns=['Date', 'Review'])
    # Since the while loop above always executes at least once (current timestamp > last ingested review), the first review
    # page will always be scraped, so delete the already ingested records manually from the df using the DJ property
    df = df[df['Date'] > props["last_date_amazon"]]
    # Remove emojis from the Review column since they are not utf-8 compliant and break ingestion
    for i in range(0, len(df)):
        # Go through each review and clean it if needed
        df.loc[i, 'Review'] = webscrape.remove_emoji(df.loc[i, 'Review'])
    log.info(f"Shape of the review dataset: {df.shape}")

    # Ingest the dataframe into a SQLite database using VDK's job_input method (if any results are fetched)
    if len(df) > 0:
        job_input.send_tabular_data_for_ingestion(
            rows=, # <- !!! ENTER HERE THE VALUES THAT WILL BE INSERTED INTO THE ROWS OF THE TABLE !!!
            column_names=, # <- !!! ENTER HERE THE COLUMNS NAMES USING THE SAME COLUMN NAMES AS IN THE REVIEWS DATA FRAME !!!
            destination_table= # <- !!! ENTER HERE THE NAME OF THE TABLE WE CREATED IN SCRIPT "02_create_yankee_candle_reviews.sql" !!!
        )
        # Reset the last_date property value to the latest date in the amazon source db table
        props["last_date_amazon"] = max(df['Date'])
        job_input.set_all_properties(props)

    log.info(f"Success! {len(df)} rows were inserted in raw yankee candle reviews table.")
    # Delay execution for 10 seconds so that records are ingested into the DB before going to the next script
    time.sleep(10)
