/* triggers that update the orders table */
/* INSERT trigger */
CREATE OR REPLACE FUNCTION tr_updOrdersInsert()
RETURNS TRIGGER
AS $tr_updOrdersInsert$
BEGIN
UPDATE orders
	SET netamount = netamount + (NEW.price * NEW.quantity),
			totalamount = (netamount + (NEW.price * NEW.quantity)) + ROUND(((netamount + (NEW.price * NEW.quantity)) * tax)/100, 2)
	WHERE orderid = NEW.orderid;
RETURN NEW;
END;
$tr_updOrdersInsert$
LANGUAGE 'plpgsql';

CREATE TRIGGER updOrdersInsert
AFTER INSERT ON orderdetail
FOR EACH ROW EXECUTE
PROCEDURE tr_updOrdersInsert();

/* UPDATE trigger */
CREATE OR REPLACE FUNCTION tr_updOrdersUpdate()
RETURNS TRIGGER
AS $tr_updOrdersUpdate$
BEGIN
UPDATE orders
	SET netamount = (NEW.price * NEW.quantity) + netamount - (OLD.price * OLD.quantity),
			totalamount = ((NEW.price * NEW.quantity) + netamount - (OLD.price * OLD.quantity)) + ROUND((((NEW.price * NEW.quantity) + netamount - (OLD.price * OLD.quantity)) * tax)/100, 2)
	WHERE orderid = NEW.orderid;
RETURN NEW;
END;
$tr_updOrdersUpdate$
LANGUAGE 'plpgsql';

CREATE TRIGGER updOrdersUpdate
AFTER UPDATE ON orderdetail
FOR EACH ROW EXECUTE
PROCEDURE tr_updOrdersUpdate();

/* DELETE trigger */
CREATE OR REPLACE FUNCTION tr_updOrdersDelete()
RETURNS TRIGGER
AS $tr_updOrdersDelete$
BEGIN
UPDATE orders
	SET netamount = netamount - (OLD.price * OLD.quantity),
			totalamount = (netamount - (OLD.price * OLD.quantity)) + ROUND(((netamount - (OLD.price * OLD.quantity)) * tax)/100, 2)
	WHERE orderid = OLD.orderid;
RETURN NEW;
END;
$tr_updOrdersDelete$
LANGUAGE 'plpgsql';

CREATE TRIGGER updOrdersDelete
AFTER DELETE ON orderdetail
FOR EACH ROW EXECUTE
PROCEDURE tr_updOrdersDelete();
