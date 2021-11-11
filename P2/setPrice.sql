/* completes the 'price' column of the 'orderdetail' table,
taking into account that the actual price is the one in 'products' table and it increases by a 2% each year */
UPDATE orderdetail
SET price = table1.price
FROM (SELECT ROUND((products.price / (1 + (EXTRACT(YEAR FROM CURRENT_DATE) - (EXTRACT(YEAR FROM orders.orderdate))) * 0.02)), 2)*orderdetail.quantity AS price, orderdetail.orderid AS orderid, orderdetail.prod_id AS prod_id
	    FROM orderdetail JOIN orders ON orders.orderid = orderdetail.orderid JOIN products ON products.prod_id = orderdetail.prod_id) AS table1
WHERE orderdetail.orderid = table1.orderid AND orderdetail.prod_id = table1.prod_id;
