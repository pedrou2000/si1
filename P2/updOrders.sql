/* triggers that update the orders table */
/* INSERT trigger */
CREATE OR REPLACE FUNCTION tr_updOrdersInsert()
RETURNS TRIGGER
AS $tr_updOrdersInsert$
BEGIN
UPDATE orders
	SET netamount = netamount + NEW.price,
		totalamount = (netamount + NEW.price) + ROUND(((netamount + NEW.price) * tax)/100, 2)
	WHERE orderid = NEW.orderid;
RETURN NEW;
END;
$tr_updOrdersInsert$
LANGUAGE 'plpgsql';

CREATE TRIGGER updOrdersInsert
BEFORE INSERT ON orderdetail
FOR EACH ROW EXECUTE
PROCEDURE tr_updOrdersInsert();
