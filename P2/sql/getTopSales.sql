CREATE OR REPLACE FUNCTION getTopSales(year1 INT, year2 INT, OUT Year INT, OUT Film varchar(255), OUT sales bigint) 
RETURNS SETOF RECORD
AS $$
DECLARE
    i integer;
BEGIN
    FOR i IN year1..year2
    LOOP
            RETURN QUERY
            SELECT
                  cast(i as INT) as Year,
                  cast(imdb_movies.movietitle as varchar(255)) as Film,
                  cast(SUM(orderdetail.quantity) as bigint) as sales
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
FROM getTopSales(2017, 2020)
ORDER BY sales DESC;
