/* Create a table that will store the weekly aggreagted data and correlation coefficients.
Table naming convention: weekly_correlation_YOURNAME where replace "YOURNAME" with your name.

Construct the CREATE TABLE statement by yourself with the following columns and data types:
 - date with type VARCHAR
 - num_no_scent_reviews with type INTEGER: this will contain the number of "no scent" reviews for the week
 - number_of_covid_cases_weekly with type INTEGER: this will contain the number of weekly covid cases
 - correlation_coeff with type REAL: this will contain the correlation coefficients for the given week */
 
CREATE TABLE IF NOT EXISTS /*!!! ENTER THE NAME OF THE TABLE HERE !!!*/ (
    date VARCHAR,
    num_no_scent_reviews INTEGER,
    number_of_covid_cases_weekly INTEGER,
    correlation_coeff REAL
)
