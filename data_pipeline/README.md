# Module 1: Data Pipeline

## Overview

This module builds an end-to-end data pipeline using book catalogue data from Books to Scrape. The goal is to collect raw product-style data, clean and transform it, store it in a normalized relational database, and analyze it using both SQL and pandas.

The pipeline runs automatically from a single Python script.

## Data Source

The data is collected from **Books to Scrape**, a public website designed for web scraping practice.

I used the first five pages of the complete book catalogue.

The final run collected:

* **100 books**
* **29 categories**

This exceeds the project requirement of at least 60 books across at least 3 categories.

For every book, the scraper collects:

* Title
* Price
* Star rating
* Availability
* Category

The scraping process uses Python's `requests` library to retrieve the pages and `BeautifulSoup` to parse the HTML.

## Project Structure

```text
data_pipeline/
├── README.md
├── requirements.txt
├── scrape_books.py
├── books.db
└── outputs/
    ├── raw_books.csv
    ├── cleaned_books.csv
    ├── query_1.csv
    ├── query_1.sql
    ├── query_2.csv
    ├── query_2.sql
    ├── query_3.csv
    ├── query_3.sql
    ├── query_4.csv
    ├── query_4.sql
    ├── query_5.csv
    ├── query_5.sql
    ├── sql_join_output.csv
    ├── pandas_merge_output.csv
    └── join_comparison.csv
```

## Data Cleaning

The scraped values are converted into appropriate data types before being stored.

### Price

The currency symbol is removed from the original price value and the numeric value is converted to a floating-point column named `price_gbp`.

### Rating

The original star ratings are text values:

`One`, `Two`, `Three`, `Four`, and `Five`.

These are mapped to integer values from 1 to 5 and stored in the `rating` column.

### Availability

The availability text is converted into a Boolean column named `in_stock`.

* `True` means the book is in stock.
* `False` means the book is not in stock.

### Handling Invalid Values

Numeric fields are converted using safe parsing so that an unexpected value does not cause the complete pipeline to fail.

If a numeric value cannot be parsed, median imputation is used when a valid median is available. This approach keeps an isolated malformed value from stopping the pipeline while still producing valid numeric data.

After cleaning, the final run contained no missing values in the required fields.

## GBP to INR Conversion

The assignment defines a fixed conversion rate of:

**1 GBP = 105.50 INR**

This is a project-defined baseline rate and is not intended to represent a live or historical exchange rate.

The INR price is calculated as:

```text
price_inr = price_gbp × 105.50
```

The result is rounded to two decimal places.

No external currency API is required for this conversion.

## SQLite Database

The cleaned data is stored in a SQLite database named:

```text
books.db
```

I used two related tables to create a normalized database structure.

### Categories Table

The `categories` table contains:

| Column          | Purpose              |
| --------------- | -------------------- |
| `category_id`   | Primary key          |
| `category_name` | Unique category name |

### Books Table

The `books` table contains:

| Column        | Purpose                              |
| ------------- | ------------------------------------ |
| `book_id`     | Primary key                          |
| `title`       | Book title                           |
| `price_gbp`   | Price in GBP                         |
| `price_inr`   | Converted price in INR               |
| `rating`      | Integer rating from 1 to 5           |
| `in_stock`    | Availability value                   |
| `category_id` | Foreign key referencing `categories` |

Separating categories into their own table avoids repeatedly storing category names and creates a clear primary-key/foreign-key relationship.

## SQL Queries

Five SQL queries are executed against the SQLite database.

Together, the queries demonstrate:

* `SELECT`
* `WHERE`
* `ORDER BY`
* `LIMIT`
* `DISTINCT`
* `BETWEEN`
* `IN`
* `JOIN`

Each SQL statement is saved as a `.sql` file and its corresponding result is saved as a `.csv` file in the `outputs` directory.

The queries cover examples such as:

* Finding highly rated books and ordering them by price
* Listing distinct categories
* Finding books within a specific GBP price range
* Finding books with ratings of 4 or 5
* Joining books with their corresponding categories

## Pandas Validation

SQL query results are also loaded into pandas using `pd.read_sql()`.

The database JOIN is independently reproduced using `pd.merge()` on the in-memory books and categories DataFrames.

Both results are sorted into the same order and compared.

The final run produced:

```text
Do SQL JOIN and pandas merge match?
True
```

This confirms that the SQL JOIN and pandas merge produced equivalent results.

## Requirements

The module requires Python 3 and the following packages:

```text
requests
beautifulsoup4
pandas
```

Install them with:

```bash
pip install -r requirements.txt
```

## How to Run

From the root project directory, move into the data pipeline folder:

```bash
cd data_pipeline
```

Run:

```bash
python scrape_books.py
```

The script automatically:

1. Scrapes the first five catalogue pages.
2. Saves the raw scraped dataset.
3. Cleans the required fields.
4. Converts GBP prices to INR.
5. Creates the normalized SQLite database.
6. Inserts categories and books into the database.
7. Executes five SQL queries.
8. Saves each SQL query and its output.
9. Reads query results using `pd.read_sql()`.
10. Reproduces the JOIN using `pd.merge()`.
11. Compares the SQL JOIN and pandas merge results.

## Final Pipeline Result

The successful pipeline run produced:

```text
Books: 100
Categories: 29
GBP to INR rate: 105.50
SQL JOIN and pandas merge match: True
```

## Design Decisions

I chose to scrape the first five pages of the full catalogue instead of limiting the scraper to three categories. This produced 100 books across 29 categories and provided a broader dataset for the database and SQL analysis.

SQLite was selected because it provides a lightweight relational database that works directly with Python without requiring a separate database server.

Categories are stored separately from books and linked using `category_id`. This reduces repeated category information and provides the required normalized primary-key/foreign-key structure.

The GBP-to-INR conversion uses the assignment's fixed rate of **1 GBP = 105.50 INR**, which makes the output reproducible and avoids depending on a live currency service.
