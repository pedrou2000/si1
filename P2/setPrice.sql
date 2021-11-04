/* completes the 'price' column of the 'orderdetail' table,
taking into account that the actual price is the one in 'products' table */
UPDATE orderdetail
SET price = products.price*quantity
FROM products
WHERE products.prod_id = orderdetail.prod_id;
