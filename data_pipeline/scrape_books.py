import os
import sqlite3
import requests
import pandas as pd
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
GBP_TO_INR = 105.50

DB_FILE = "books.db"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------------------------------
# Task 1: Scrape book data
# -------------------------------------------------

def get_soup(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def scrape_books(pages=5):
    books = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}catalogue/page-{page}.html"

        print(f"Scraping page {page}: {url}")

        soup = get_soup(url)
        products = soup.select("article.product_pod")

        for product in products:
            title = product.h3.a["title"]

            price = product.select_one(
                ".price_color"
            ).get_text(strip=True)

            rating_classes = product.select_one(
                ".star-rating"
            )["class"]

            star_rating = rating_classes[1]

            availability = product.select_one(
                ".availability"
            ).get_text(strip=True)

            relative_link = product.h3.a["href"]

            detail_url = (
                BASE_URL
                + "catalogue/"
                + relative_link
            )

            detail_soup = get_soup(detail_url)

            breadcrumb_links = detail_soup.select(
                "ul.breadcrumb li a"
            )

            category = breadcrumb_links[-1].get_text(
                strip=True
            )

            books.append({
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category
            })

    return pd.DataFrame(books)


# -------------------------------------------------
# Task 2 and Task 3: Clean and convert data
# -------------------------------------------------

def clean_data(df):
    cleaned = df.copy()

    # Extract numeric part of price
    cleaned["price_gbp"] = (
        cleaned["price"]
        .astype(str)
        .str.extract(
            r"(\d+(?:\.\d+)?)",
            expand=False
        )
    )

    cleaned["price_gbp"] = pd.to_numeric(
        cleaned["price_gbp"],
        errors="coerce"
    )

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    cleaned["rating"] = cleaned[
        "star_rating"
    ].map(rating_map)

    cleaned["in_stock"] = (
        cleaned["availability"]
        .astype(str)
        .str.contains(
            "In stock",
            case=False,
            na=False
        )
    )

    # Median imputation for numeric parsing problems
    if cleaned["price_gbp"].isna().any():
        median_price = cleaned[
            "price_gbp"
        ].median()

        cleaned["price_gbp"] = cleaned[
            "price_gbp"
        ].fillna(median_price)

    if cleaned["rating"].isna().any():
        median_rating = cleaned[
            "rating"
        ].median()

        cleaned["rating"] = cleaned[
            "rating"
        ].fillna(median_rating)

    cleaned["rating"] = cleaned[
        "rating"
    ].astype(int)

    cleaned["in_stock"] = cleaned[
        "in_stock"
    ].astype(bool)

    # Required fixed project conversion rate
    cleaned["price_inr"] = (
        cleaned["price_gbp"]
        * GBP_TO_INR
    ).round(2)

    cleaned = cleaned[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ]

    return cleaned


# -------------------------------------------------
# Task 4: Create normalized SQLite database
# -------------------------------------------------

def create_database(df):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "PRAGMA foreign_keys = ON"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS books"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS categories"
    )

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    categories = sorted(
        df["category"].dropna().unique()
    )

    for category in categories:
        cursor.execute(
            """
            INSERT INTO categories (
                category_name
            )
            VALUES (?)
            """,
            (category,)
        )

    conn.commit()

    category_df = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories
        """,
        conn
    )

    category_map = dict(
        zip(
            category_df["category_name"],
            category_df["category_id"]
        )
    )

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO books (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(row["in_stock"]),
                category_map[row["category"]]
            )
        )

    conn.commit()

    return conn, category_df


# -------------------------------------------------
# Task 5: Run required SQL queries
# -------------------------------------------------

def run_queries(conn):
    queries = {
        "query_1": """
            SELECT
                title,
                price_gbp,
                rating
            FROM books
            WHERE rating >= 4
            ORDER BY price_gbp DESC
            LIMIT 10;
        """,

        "query_2": """
            SELECT DISTINCT
                category_name
            FROM categories
            ORDER BY category_name;
        """,

        "query_3": """
            SELECT
                title,
                price_gbp
            FROM books
            WHERE price_gbp BETWEEN 20 AND 40
            ORDER BY price_gbp ASC;
        """,

        "query_4": """
            SELECT
                title,
                rating
            FROM books
            WHERE rating IN (4, 5)
            ORDER BY
                rating DESC,
                title ASC
            LIMIT 15;
        """,

        "query_5": """
            SELECT
                b.book_id,
                b.title,
                b.price_gbp,
                b.price_inr,
                b.rating,
                b.in_stock,
                c.category_name
            FROM books AS b
            JOIN categories AS c
                ON b.category_id = c.category_id
            ORDER BY
                c.category_name ASC,
                b.rating DESC,
                b.price_gbp DESC,
                b.title ASC;
        """
    }

    results = {}

    for name, query in queries.items():
        print("\n" + "=" * 60)
        print(name.upper())
        print("=" * 60)

        print(query)

        result = pd.read_sql(
            query,
            conn
        )

        print(result)

        result.to_csv(
            f"{OUTPUT_DIR}/{name}.csv",
            index=False
        )

        results[name] = result

        with open(
            f"{OUTPUT_DIR}/{name}.sql",
            "w",
            encoding="utf-8"
        ) as file:
            file.write(query.strip())

    return queries, results


# -------------------------------------------------
# Task 6: pandas read_sql
# -------------------------------------------------

def read_sql_examples(conn, queries):
    first_query_df = pd.read_sql(
        queries["query_1"],
        conn
    )

    join_query_df = pd.read_sql(
        queries["query_5"],
        conn
    )

    print("\nQuery 1 using pd.read_sql:")
    print(first_query_df)

    print("\nJoin query using pd.read_sql:")
    print(join_query_df)

    return first_query_df, join_query_df


# -------------------------------------------------
# Task 6: Reproduce JOIN using pandas merge
# -------------------------------------------------

def pandas_merge_example(cleaned_df, category_df):
    merged_df = pd.merge(
        cleaned_df,
        category_df,
        left_on="category",
        right_on="category_name",
        how="inner"
    )

    merged_df = merged_df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name"
        ]
    ].copy()

    merged_df = merged_df.sort_values(
        by=[
            "category_name",
            "rating",
            "price_gbp",
            "title"
        ],
        ascending=[
            True,
            False,
            False,
            True
        ]
    ).reset_index(drop=True)

    return merged_df


# -------------------------------------------------
# Compare SQL JOIN and pandas merge
# -------------------------------------------------

def compare_results(sql_join, pandas_join):
    sql_result = sql_join[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category_name"
        ]
    ].copy()

    sql_result["in_stock"] = sql_result[
        "in_stock"
    ].astype(bool)

    sql_result = sql_result.sort_values(
        by=[
            "category_name",
            "rating",
            "price_gbp",
            "title"
        ],
        ascending=[
            True,
            False,
            False,
            True
        ]
    ).reset_index(drop=True)

    pandas_result = pandas_join.copy().reset_index(
        drop=True
    )

    match = sql_result.equals(
        pandas_result
    )

    print("\nSQL JOIN output:")
    print(sql_result)

    print("\nPandas merge output:")
    print(pandas_result)

    print(
        "\nDo SQL JOIN and pandas merge match?"
    )
    print(match)

    sql_result.to_csv(
        f"{OUTPUT_DIR}/sql_join_output.csv",
        index=False
    )

    pandas_result.to_csv(
        f"{OUTPUT_DIR}/pandas_merge_output.csv",
        index=False
    )

    comparison_df = pd.DataFrame({
        "comparison": [
            "SQL JOIN vs pandas merge"
        ],
        "match": [match]
    })

    comparison_df.to_csv(
        f"{OUTPUT_DIR}/join_comparison.csv",
        index=False
    )


# -------------------------------------------------
# Main pipeline
# -------------------------------------------------

def main():
    print("\nSTEP 1: SCRAPING")
    print("=" * 60)

    raw_df = scrape_books(
        pages=5
    )

    print(
        f"\nBooks scraped: {len(raw_df)}"
    )

    print(
        f"Categories: "
        f"{raw_df['category'].nunique()}"
    )

    print("\nRaw data sample:")
    print(raw_df.head())

    raw_df.to_csv(
        f"{OUTPUT_DIR}/raw_books.csv",
        index=False
    )

    print(
        "\nRaw data saved to "
        "outputs/raw_books.csv"
    )


    print("\nSTEP 2: CLEANING")
    print("=" * 60)

    cleaned_df = clean_data(
        raw_df
    )

    print("\nCleaned data sample:")
    print(cleaned_df.head())

    print("\nData types:")
    print(cleaned_df.dtypes)

    print("\nMissing values:")
    print(cleaned_df.isnull().sum())


    print("\nSTEP 3: GBP TO INR")
    print("=" * 60)

    print(
        f"Fixed conversion rate: "
        f"1 GBP = {GBP_TO_INR:.2f} INR"
    )

    print("\nSample conversion:")
    print(
        cleaned_df[
            [
                "title",
                "price_gbp",
                "price_inr"
            ]
        ].head()
    )

    cleaned_df.to_csv(
        f"{OUTPUT_DIR}/cleaned_books.csv",
        index=False
    )

    print(
        "\nCleaned data saved to "
        "outputs/cleaned_books.csv"
    )


    print("\nSTEP 4: SQLITE DATABASE")
    print("=" * 60)

    conn, category_df = create_database(
        cleaned_df
    )

    print(
        f"Database created: {DB_FILE}"
    )


    print("\nSTEP 5: SQL QUERIES")
    print("=" * 60)

    queries, results = run_queries(
        conn
    )


    print("\nSTEP 6: PANDAS")
    print("=" * 60)

    first_query_df, sql_join = (
        read_sql_examples(
            conn,
            queries
        )
    )

    pandas_join = pandas_merge_example(
        cleaned_df,
        category_df
    )

    compare_results(
        sql_join,
        pandas_join
    )


    print("\nPIPELINE COMPLETE")
    print("=" * 60)

    print(
        f"Books: {len(cleaned_df)}"
    )

    print(
        f"Categories: "
        f"{cleaned_df['category'].nunique()}"
    )

    print(
        f"GBP to INR rate: "
        f"{GBP_TO_INR:.2f}"
    )

    conn.close()


if __name__ == "__main__":
    main()