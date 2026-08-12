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