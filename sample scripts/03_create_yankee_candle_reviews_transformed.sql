-- Create a table that will store the transformed Amazon reviews table with 3 columns:
-- date, number of total negative reviews and number of negative reviews indicating "no scent".
-- Table naming convention: prefix + _ + yankee_candle_reviews_transformed 


CREATE TABLE IF NOT EXISTS /*!!! ENTER THE NAME OF THE TABLE HERE !!!*/ (
    date VARCHAR,
    num_negative_reviews INTEGER,
    num_no_scent_reviews INTEGER
)
