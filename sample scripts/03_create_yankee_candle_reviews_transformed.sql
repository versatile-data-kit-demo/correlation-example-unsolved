-- Create a table that will store the transformed Amazon reviews table with 3 columns:
-- date, number of total negative reviews and number of negative reviews indicating "no scent"

CREATE TABLE IF NOT EXISTS /*!!! ENTER THE NAME OF THE TABLE HERE !!!*/ (
    date VARCHAR,
    num_negative_reviews INTEGER,
    num_no_scent_reviews INTEGER
)