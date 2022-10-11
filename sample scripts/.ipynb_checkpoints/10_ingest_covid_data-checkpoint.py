# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import requests
import pandas as pd
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)


def run(job_input: IJobInput):
    """
    Collect COVID-19 historical data for number of cases per day in the US since the start of the pandemic through
    an API call. Ingest this data into a table in a cloud Trino database.
    """

    log.info(f"Starting job step {__name__}")

    # Create/retrieve the data job property storing latest ingested date for covid_cases_usa_daily table.
    # If the property does not exist, set it to "2020-01-01" (around the start of the pandemic).
    props = job_input. # <- !!! ENTER HERE THE VDK'S JOB_INPUT FUNCTION THAT GETS ALL JOB PROPERTIES !!!
    if "last_date_covid" in props:
        pass
    else:
        props["last_date_covid"] = '2020-01-01'

    # Initialize URL
    url = "https://covid-api.mmediagroup.fr/v1/history?country=US&status=confirmed"

    # Make a GET request to the COVID-19 API
    response = requests. # <- !!! MAKE A GET REQUEST TO THE ABOVE URL USING THE APPROPRIATE METHOD OF THE REQUESTS PACKAGE !!!
    # Check if the request was successful
    response.raise_for_status()

    dates_cases = response.json()['All']['dates']
    # Reformat the dictionary
    dates_cases_dict = {'obs_date': [], 'number_of_cases': []}

    for key, value in dates_cases.items():
        dates_cases_dict['obs_date'].append(key)
        dates_cases_dict['number_of_cases'].append(value)

    # Convert the dictionary into a DF
    df_covid = pd.DataFrame.from_dict(dates_cases_dict)
    # Keep only the dates which are not present in the table already (based on last_date_covid property)
    df_covid = df_covid[df_covid['obs_date'] > props["last_date_covid"]]

    # Ingest the dictionary into a SQLite database using VDK's job_input method (if any results are fetched)
    if len(df_covid) > 0:
        job_input.send_tabular_data_for_ingestion(
            rows=df_covid.values,
            column_names=df_covid.columns.to_list(),
            destination_table="" # <- !!! ENTER BETWEEN THE QUOTATION MARKS THE NAME OF THE TABLE CREATED IN SCRIPT 01_create_covid_cases_usa_daily.sql) !!!
        )
        # Reset the last_date property value to the latest date in the covid source db table
        props["last_date_covid"] = max(df_covid['obs_date'])
        job_input.set_all_properties(props)

    log.info(f"Success! {len(df_covid)} rows were inserted in the daily covid cases table.")
