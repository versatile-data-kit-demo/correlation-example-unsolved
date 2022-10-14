/* Create a table that will store the weekly aggreagted data and correlation coefficients.
-- Table naming convention: prefix + _ + weekly_correlation 

 
CREATE TABLE IF NOT EXISTS /*!!! ENTER THE NAME OF THE TABLE HERE !!!*/ (
    date VARCHAR,
    num_no_scent_reviews INTEGER,
    number_of_covid_cases_weekly INTEGER,
    correlation_coeff REAL
)
