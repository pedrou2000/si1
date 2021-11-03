/* product foreign key to inventory table */
ALTER TABLE inventory ADD CONSTRAINT FK_inv_prod FOREIGN KEY (prod_id) REFERENCES products (prod_id) ON DELETE CASCADE;
/*ALTER TABLE inventory ADD PRIMARY KEY (prod_id);*/

/* customer_id foreign key to orders table */
ALTER TABLE orders ADD CONSTRAINT FK_order_customer FOREIGN KEY (customerid) REFERENCES customers (customerid) ON DELETE CASCADE;

/* prod_id foreign key to orderdetail table */
ALTER TABLE orderdetail ADD CONSTRAINT FK_orderdetail_prod FOREIGN KEY (prod_id) REFERENCES products (prod_id) ON DELETE SET NULL;

/* order foreign key to orderdetail table */
ALTER TABLE orderdetail ADD CONSTRAINT FK_orderdetail_ord FOREIGN KEY (orderid) REFERENCES orders (orderid) ON DELETE CASCADE;

/* eliminate duplicated rows in orderdetail */
/* we first find the rows in orderdetail that has the same (orderid, prod_id) and we GROUP them. Then we create an auxiliary table
    that has one row per (orderid, prod_id) that were duplicated in the orderdetail table. Each row in the new table will have
    as quantity the sum of the quantities from the duplicated rows, and as price the average of the prices from the duplicated rows */
SELECT DISTINCT orderid, prod_id, AVG(price) AS price, SUM(quantity) AS quantity
INTO duplicate_table
FROM orderdetail
GROUP BY (orderid, prod_id)
HAVING COUNT((orderid, prod_id)) > 1;

/* from the original table, we delete ALL the rows that has the same (orderid, prod_id) as any of the rows in the new table */
DELETE FROM orderdetail
WHERE (orderid, prod_id)
IN (SELECT orderid, prod_id FROM duplicate_table);

/* finally we add to orderdetail the rows of the new table we created. This way we will only have one row from the originally duplicated rows,
  with the sum of its quantities */
INSERT INTO orderdetail
SELECT *
FROM duplicate_table;

/* eliminate the auxiliary table */
DROP TABLE duplicate_table;

/* double primary key in orderdetail */
ALTER TABLE orderdetail ADD PRIMARY KEY (orderid, prod_id);

/* actor_id foreign key to actormovie table */
ALTER TABLE imdb_actormovies ADD CONSTRAINT FK_actormovie_actor FOREIGN KEY (actorid) REFERENCES imdb_actors (actorid) ON DELETE CASCADE;

/* movie_id foreign key to actormovie table */
ALTER TABLE imdb_actormovies ADD CONSTRAINT FK_actormovie_movie FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid) ON DELETE CASCADE;

/* alert table */
CREATE TABLE alerts();
ALTER TABLE alerts ADD prod_id int;
ALTER TABLE alerts ADD PRIMARY KEY (prod_id);
ALTER TABLE alerts ADD CONSTRAINT FK_alert_inventory FOREIGN KEY (prod_id) REFERENCES inventory (prod_id) ON DELETE CASCADE;
ALTER TABLE alerts ADD date timestamp;

/* Add ‘loyalty’ to ‘customers’ table, with 0 default value */
ALTER TABLE customers ADD loyalty int NOT NULL CONSTRAINT loyalty_col DEFAULT (0);
/* Add balance to ‘customers’ table, with 0 default value */
ALTER TABLE customers ADD balance int NOT NULL CONSTRAINT balance_col DEFAULT (0);

/* function setCustomersBalance(IN initialBalance bigint); */
CREATE PROCEDURE setCustomersBalance (IN maxBalance bigint)
LANGUAGE plpgsql
as $$
BEGIN
	UPDATE customers SET balance = floor(random() * (maxBalance + 1))::int;
END $$;

/* call the procedure with N = 100 */
CALL setCustomersBalance(100);
