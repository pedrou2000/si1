/*
ALTER TABLE imdb_movies ADD total_sales int;

// To modify the year's column of the films that has as year 1998-1999 
UPDATE imdb_movies
SET year = '1998'
WHERE year = '1998-1999';

UPDATE imdb_movies
SET total_sales = table1.total_sales
FROM (SELECT imdb_movies.movieid AS movieid, SUM(inventory.sales) AS total_sales, imdb_movies.year AS release_year
      FROM imdb_movies JOIN products ON products.movieid = imdb_movies.movieid JOIN inventory ON products.prod_id = inventory.prod_id
      GROUP BY imdb_movies.movieid) AS table1
WHERE imdb_movies.movieid = table1.movieid;


SELECT imdb_movies.movietitle, imdb_movies.year, imdb_movies.total_sales
FROM imdb_movies JOIN (SELECT imdb_movies.year AS year_2, MAX(imdb_movies.total_sales) AS max_total_sales
                      FROM imdb_movies
                      GROUP BY imdb_movies.year) AS table2
ON imdb_movies.total_sales = table2.max_total_sales AND imdb_movies.year = table2.year_2
WHERE (CAST(imdb_movies.year AS int)) > 2000 AND (CAST(imdb_movies.year AS int)) < 2005
ORDER BY imdb_movies.total_sales DESC;

ALTER TABLE imdb_movies DROP COLUMN total_sales;
*/




CREATE OR REPLACE FUNCTION foo_2() 
RETURNS TABLE(
      id INT,
      sales INT, 
      yesr INT 
)
AS $$
DECLARE
    i integer;
BEGIN
    FOR i IN 2015..2018
    LOOP
            RETURN QUERY
            SELECT cast(imdb_movies.movieid as integer) as id, 
                  cast(SUM(orderdetail.quantity) as integer) as sales,
                  i as year
            FROM orders, orderdetail, products, imdb_movies
            WHERE EXTRACT(year from orderdate) = i and 
                  orders.orderid = orderdetail.orderid and
                  products.prod_id = orderdetail.prod_id and 
                  products.movieid = imdb_movies.movieid

            GROUP BY imdb_movies.movieid
            ORDER BY sales DESC 
            LIMIT 1;
    END LOOP;
END $$
LANGUAGE plpgsql;

SELECT * 
FROM foo_2()
ORDER BY sales DESC;