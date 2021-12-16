/* Para crear nuestros propios índices primero eliminamos los existentes por defecto en la BD */
/* 1. Eliminamos el índice sobre la clave primaria de customers */
ALTER TABLE orders
DROP CONSTRAINT orders_customerid_fkey;

ALTER TABLE customers
DROP CONSTRAINT customers_pkey;

/* 2. Eliminamos el índice sobre la clave primaria de orders */
ALTER TABLE orderdetail
DROP CONSTRAINT orderdetail_orderid_fkey;

ALTER TABLE orders
DROP CONSTRAINT orders_pkey;

/* 3. Creamos nuestros propios índices */

CREATE INDEX order_index
ON orders (extract(year FROM orderdate), extract(month FROM orderdate));

CREATE INDEX customer_index
ON customers (creditcardtype);


/* FUNCTION */
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

/* 
  Before touching the database, the query takes approx. 65-100 ms.
  -After the following instructions (in which we delete the index "customers_pkey" in customers) 
  it takes 400-500 ms.

    ALTER TABLE orders
    DROP CONSTRAINT orders_customerid_fkey;

    ALTER TABLE customers
    DROP CONSTRAINT customers_pkey;

  -Dropping the index "orders_pkey" of the table orders (with the following commands):

    ALTER TABLE orderdetail
    DROP CONSTRAINT orderdetail_orderid_fkey;

    ALTER TABLE orders
    DROP CONSTRAINT orders_pkey;
  
  it does not affect the efficiency of the query.

  -But we have found some indexes that, indeed, improves the query´s performance.
   1. CREATE INDEX order_index
      ON orders (extract(year FROM orderdate));

      Now the function takes between 50-65 ms to complete

   2. CREATE INDEX order_index
      ON orders (extract(month FROM orderdate));

      Now the function takes between 50-60 ms to complete
    
   3. CREATE INDEX order_index
      ON orders (extract(year FROM orderdate), extract(month FROM orderdate));

      Now the function takes between 45-50 ms to complete
  
   4. CREATE INDEX order_index_1
      ON orders (extract(year FROM orderdate));
	  
	    CREATE INDEX order_index_2
      ON orders (extract(month FROM orderdate));

      Now the function takes between 45-50 ms to complete

   5. CREATE INDEX order_index
      ON orders (extract(year FROM orderdate), extract(month FROM orderdate));
	  
	    CREATE INDEX customer_index
      ON customers (creditcardtype);

      Now the function takes between 40-45 ms to complete
*/