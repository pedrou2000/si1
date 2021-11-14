actualice las tablas ‘orders’ e 'inventory' ???


/* CREATE ALERT when stock is 0 */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerAlerts()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerAlerts$
BEGIN
INSERT INTO alerts
VALUES (prod_id, CURRENT_DATE)
FROM inventory
WHERE inventory.stock = 0;
RETURN NEW;
END;
$tr_updInventoryAndCustomerAlerts$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerAlerts
AFTER INSERT ON orders
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerAlerts();

/* FIDELITY points addition */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerFidelity()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerFidelity$
BEGIN
UPDATE customers
SET loyalty = loyalty + (NEW.totalamount * 0.05)
WHERE customers.customerid = NEW.customerid;
RETURN NEW;
END;
$tr_updInventoryAndCustomerFidelity$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerFidelity
AFTER INSERT ON orders
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerFidelity();

/* BALANCE reduction after buying */
CREATE OR REPLACE FUNCTION tr_updInventoryAndCustomerReduceBalance()
RETURNS TRIGGER
AS $tr_updInventoryAndCustomerReduceBalance$
BEGIN
UPDATE customers
SET balance = balance - NEW.totalamount
WHERE customers.customerid = NEW.customerid;
RETURN NEW;
END;
$tr_updInventoryAndCustomerReduceBalance$
LANGUAGE 'plpgsql';

CREATE TRIGGER updInventoryAndCustomerReduceBalance
AFTER INSERT ON orders
FOR EACH ROW EXECUTE
PROCEDURE tr_updInventoryAndCustomerReduceBalance();
