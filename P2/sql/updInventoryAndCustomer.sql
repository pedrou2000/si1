/* UPDATE orders table. When a new customer is added to
   the database, a new order for him is created. */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerNewCustomer()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerNewCustomer$
BEGIN
 INSERT INTO orders(orderdate, customerid, netamount, tax, totalamount, status)
 VALUES (CURRENT_DATE, NEW.customerid, 0, 0, 0, NULL);
RETURN NEW;
END;
$tr_updInventoryAndCustomerNewCustomer$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerNewCustomer
AFTER INSERT ON customers
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerNewCustomer();

/* UPDATE inventory table. When an order is completed, the inventory must be modified. */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerInventoryUpdate()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerInventoryUpdate$
BEGIN
	UPDATE inventory
	SET stock = stock - orderdetail.quantity
	FROM orderdetail
	WHERE NEW.status = 'Paid' AND inventory.prod_id = orderdetail.prod_id
		AND orderdetail.orderid = NEW.orderid;

RETURN NEW;
END;
$tr_updInventoryAndCustomerInventoryUpdate$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerInventoryUpdate
AFTER UPDATE ON orders
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerInventoryUpdate();

/* CREATE ALERT when stock is 0 */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerAlerts()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerAlerts$
BEGIN
	INSERT INTO alerts(prod_id, date)
	SELECT inventory.prod_id, CURRENT_DATE
	FROM inventory
	WHERE inventory.stock = 0 AND inventory.prod_id = NEW.prod_id;
RETURN NEW;
END;
$tr_updInventoryAndCustomerAlerts$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerAlerts
AFTER UPDATE ON inventory
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerAlerts();

/* FIDELITY points addition */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerFidelity()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerFidelity$
BEGIN
  UPDATE customers
  SET loyalty = loyalty + (NEW.totalamount * 5)
  WHERE customers.customerid = NEW.customerid AND NEW.status = 'Paid';
RETURN NEW;
END;
$tr_updInventoryAndCustomerFidelity$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerFidelity
AFTER UPDATE ON orders
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerFidelity();

/* BALANCE reduction after buying */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerReduceBalance()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerReduceBalance$
BEGIN
  UPDATE customers
  SET balance = balance - NEW.totalamount
  WHERE customers.customerid = NEW.customerid AND NEW.status = 'Paid';
RETURN NEW;
END;
$tr_updInventoryAndCustomerReduceBalance$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerReduceBalance
AFTER UPDATE ON orders
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerReduceBalance();
