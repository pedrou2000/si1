/* completes the 'price' column of the 'orderdetail' table,
taking into account that the actual price is the one in 'products' table */
/* First we add an auxiliary column */
ALTER TABLE orderdetail
ADD individual_price numeric;

/* We update the auxiliary column with the values from the product table */
UPDATE orderdetail
SET individual_price = products.price
FROM products
WHERE products.prod_id = orderdetail.prod_id;

/* We update the column price (the one we were asked to update) */
UPDATE orderdetail
SET price=individual_price*quantity;*/

/* We eliminate the auxiliar column previously created */
ALTER TABLE orderdetail DROP COLUMN individual_price;
