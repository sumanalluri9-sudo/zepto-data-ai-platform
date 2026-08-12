SELECT
                title,
                price_gbp,
                rating
            FROM books
            WHERE rating >= 4
            ORDER BY price_gbp DESC
            LIMIT 10;