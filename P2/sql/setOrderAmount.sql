/* function setOrderAmount(); */
CREATE PROCEDURE setOrderAmount ()
LANGUAGE plpgsql
as $$
BEGIN
	/* complete the 'netamount' column */
	UPDATE orders
	SET netamount = sub_q.sum_prices
	FROM
    (
    SELECT SUM(price*quantity) AS sum_prices, orderdetail.orderid
    FROM orderdetail
    GROUP BY orderdetail.orderid
    ) AS sub_q
	WHERE sub_q.orderid = orders.orderid;

	/* complete the 'totalamount' column */
	UPDATE orders
	SET totalamount = ROUND(netamount + (tax * netamount)/100, 2);

END $$;
