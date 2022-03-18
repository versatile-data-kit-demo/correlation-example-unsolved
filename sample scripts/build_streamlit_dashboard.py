import os
import pandas as pd
import pathlib
import streamlit as st
from trino import dbapi
from trino import constants
from trino.auth import BasicAuthentication
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.stats

# Page title and description
st.title('Correlation analysis: COVID-19 cases in the US and Yankee candle reviews indicating "no scent"')
st.write('The dashboard shows the relationship between weekly COVID cases in the US and bad US Amazon reviews '
         'containing the words "smell", "fragrance" or "scent" for one of the most popular [Yankee candles on Amazon]'
         '(https://www.amazon.com/Yankee-Candle-Large-Balsam-Cedar/dp/B000JDGC78/ref=cm_cr_arp_d_product_top?ie=UTF8).')

# Sub-header
st.header('Number of weekly COVID cases and "no scent" reviews over time')

# Make the current directory the same as the job directory
os.chdir(pathlib.Path(__file__).parent.absolute())

# Create a connection to the Trino DB
auth = None
conn = dbapi.connect(
    host=os.environ.get("VDK_TRINO_HOST"),
    port=int(os.environ.get("VDK_TRINO_PORT")),
    user="user",
    auth=auth,
    catalog=os.environ.get("VDK_TRINO_CATALOG", 'mysql'),
    schema=os.environ.get("VDK_TRINO_SCHEMA", "default"),
    http_scheme=constants.HTTP,
    verify=False,
    request_timeout=600,
)
# Fetch data
df = pd.read_sql_query(
    f"SELECT * FROM ...", conn # <- !!! REPLACE THE ... WITH THE NAME OF THE TABLE WE POPULATED IN SCRIPT "40_calculate_correlation.py" !!!
)
# Transform into datetime Series
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Plot # COVID cases vs no-scent complaints over time
fig, ax = plt.subplots(figsize=(12, 6))
ax2 = ax.twinx()
ax.set_title('No scent Yankee candle reviews and COVID cases')
ax.plot(df['date'], df['num_no_scent_reviews'], color='green')
ax2.plot(df['date'], df['number_of_covid_cases_weekly'], color='red')
ax.set_ylabel('# "No scent" reviews')
ax2.set_ylabel('# Covid cases weekly (in mln)')
ax.legend(['no scent reviews'])
ax2.legend(['weekly covid cases'], loc='upper center')
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1,13)))
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(
    mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
plt.tight_layout()
st.pyplot(fig=plt)

# Sub-header
st.header('Weekly correlation between "no scent" reviews and covid cases')

# Current period correlation
corr_coeff = pd.to_numeric(df[df['date']==max(df['date'])]['correlation_coeff'], errors='coerce')
st.metric("The current correlation coefficient is:", corr_coeff)

# Plot the correlation coefficients over time
st.write('Correlation coefficient over time:')
df = df.rename(columns={'date': 'index'}).set_index('index')
df['correlation_coeff'] = df['correlation_coeff'].astype(float)
st.line_chart(data=df[['correlation_coeff']].fillna(0))
# Show data in a table
st.write('Underlying data:')
df = df.reset_index().rename(columns={'index': 'week'}).sort_values('week', ascending=False)
# Convert date to string
df['week'] = df['week'].dt.strftime('%Y-%m-%d')
# Visualize in the dashboard
st.dataframe(df[['week', 'correlation_coeff']])
