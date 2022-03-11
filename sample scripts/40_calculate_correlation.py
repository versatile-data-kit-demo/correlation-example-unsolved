# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import numpy as np
import logging
import os
import pathlib
import scipy.stats
import matplotlib.pyplot as plt
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)
# Make the current directory the same as the job directory
os.chdir(pathlib.Path(__file__).parent.absolute())


def run(job_input: IJobInput):
    """
    Calculate the weekly correlation between "no scent" Yankee candle reviews and COVID cases in the US.
    Save the weekly correlations in a table in the DB.
    """

    log.info(f"Starting job step {__name__}")

    # Create/retrieve the data job property storing latest ingested date for weekly_correlation table.
    # If the property does not exist, set it to "2020-01-01" (first ingested date).
    props = job_input.get_all_properties()
    if "last_date_correlation" in props:
        pass
    else:
        props["last_date_correlation"] = '2020-01-01'

    # Read the candle review data and transform to df
    reviews = job_input.( # <- !!! BEFORE THE ( ENTER THE APPROPRIATE JOB_INPUT METHOD FOR EXECUTING SQL STATEMENTS FROM PYTHON SCRIPTS !!!
        f"""
        SELECT date, num_no_scent_reviews 
        FROM !!! ENTER HERE THE NAME OF THE TABLE WE POPULATED IN SCRIPT "30_transform_amazon_reviews.py" !!!
        WHERE date > '{props["last_date_correlation"]}'
        """
    )
    reviews_df = pd.DataFrame(reviews, columns=['date', 'num_no_scent_reviews'])

    # Read the covid data and transform to df
    covid = job_input.( # <- !!! BEFORE THE ( ENTER THE APPROPRIATE JOB_INPUT METHOD FOR EXECUTING SQL STATEMENTS FROM PYTHON SCRIPTS !!!
        f"""
        SELECT * 
        FROM !!! ENTER HERE THE NAME OF THE TABLE WE POPULATED IN SCRIPT "10_ingest_covid_data.py" !!!
        WHERE obs_date > '{props["last_date_correlation"]}'
        """
    )
    covid_df = pd.DataFrame(covid, columns=['date', 'number_of_covid_cases'])

    # Merge the two dataframes and fill missing values with 0. Use right join since reviews_df doesn't contain all dates
    df_merged = reviews_df.merge(covid_df, on=['date'], how='right').fillna(0)

    # If any data is returned, do some transformations and calculate weekly stats
    if len(df_merged) > 0:
        # Calculate new covid cases per day (current numbers are cumulative)
        df_merged['date'] = pd.to_datetime(df_merged['date'], format='%Y-%m-%d')
        df_merged['number_of_covid_cases_daily'] = df_merged['number_of_covid_cases'].diff(periods=-1).fillna(0)

        # Aggregate data on weekly level
        df_merged_weekly = df_merged.copy()
        # The next step is necessary so that weekly calculations look 7 days ahead instead of backwards
        # (i.e. on Monday report the numbers for the period Monday-Sunday of the same week)
        df_merged_weekly['date'] = pd.to_datetime(df_merged_weekly['date']) - pd.to_timedelta(6, unit='d')
        # Aggregate on week-start level
        df_merged_weekly = df_merged_weekly.resample('W-MON', on='date').sum().reset_index()
        df_merged_weekly = df_merged_weekly.rename(columns={'number_of_covid_cases_daily': 'number_of_covid_cases_weekly'})\
                                           .drop(columns=["number_of_covid_cases"])
        # Sort df values by date
        df_merged_weekly = df_merged_weekly.sort_values('date', ascending=True).reset_index(drop=True)

        # Check if the last ingested week is contained in df_merged_weekly. If yes, remove it.
        df_merged_weekly = df_merged_weekly[df_merged_weekly['date'] > props["last_date_correlation"]]

        # Calculate correlation coefficients for each week in the df_merged_weekly table
        corr_coeff = [np.nan]
        for i in range(1, len(df_merged_weekly)):
            corr_coeff.append(df_merged_weekly['num_no_scent_reviews'][:i]
                              .corr(df_merged_weekly['number_of_covid_cases_weekly'][:i]))
        # Add them as a column in the df
        df_merged_weekly['correlation_coeff'] = corr_coeff

        # Original date format: "2022-02-06T00:00:00". Transform into "2022-02-06"
        df_merged_weekly['date'] = df_merged_weekly['date'].dt. # <- !!! ENTER HERE THE PANDAS DATETIME METHOD THAT HANDLES DATETIME FORMAT TRANSFORMATIONS !!!

        # Ingest the weekly data and correlation coefficients into a new table using VDK's job_input method
        job_input.send_tabular_data_for_ingestion(
            rows=df_merged_weekly.values,
            column_names=df_merged_weekly.columns.to_list(),
            destination_table= # <- !!! ENTER HERE THE NAME OF THE TABLE WE CREATED IN SCRIPT "04_create_weekly_correlation.sql" !!!
        )
        # Reset the last_date property value to the latest date in the covid source db table
        props["last_date_correlation"] = max(df_merged_weekly['date'])
        job_input.set_all_properties(props)
        log.info(f"Success! {len(df_merged_weekly)} rows were inserted.")
    else:
        log.info("No new records to ingest.")
