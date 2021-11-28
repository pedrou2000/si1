CREATE OR REPLACE FUNCTION getCiudadesDistintas(yearMonth varchar(6))
RETURNS TABLE (total_distinct_cities bigint)
AS
$$
BEGIN
RETURN QUERY
    SELECT count(DISTINCT(country)) AS total_distinct_cities
    FROM customers
    WHERE customerid IN (SELECT customerid
                         FROM orders 
                         WHERE extract(MONTH FROM orderdate)=CAST(SUBSTRING(yearMonth, 5, 6) AS int) and extract(YEAR FROM orderdate)=CAST(SUBSTRING(yearMonth, 1, 4) AS int))
                         AND creditcardtype='VISA';
END;
$$
LANGUAGE 'plpgsql' STABLE;

SELECT *
FROM getCiudadesDistintas('202102');

/*Before touching the database, the query takes approx. 65-100 ms.
  After the following instructions (in which we delete the index "customers_pkey" in customers) 
  it takes 400-500 ms.

    ALTER TABLE orders
    DROP CONSTRAINT orders_customerid_fkey;

    ALTER TABLE customers
    DROP CONSTRAINT customers_pkey;
*/