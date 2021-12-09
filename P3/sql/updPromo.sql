/* Create column promo in customers */
ALTER TABLE customers
ADD promo FLOAT DEFAULT(0);

/* Create trigger to use the promo column */

CREATE OR REPLACE FUNCTION tr_apply_promo()
RETURNS TRIGGER 
AS $tr_apply_promo$ 
DECLARE
    orderids integer[];
    orderidd integer;
    prod_ids integer[];
    prod_idd integer;
    pricee decimal;

BEGIN
    /* Obtengo los ids de los carritos (order con status = NULL) 
        asociados al customer con cutomerid NEW.customerid */
    orderids := array(
        SELECT orderid FROM orders 
        WHERE orders.customerid = NEW.customerid and orders.status is NULL
    );

    /* Actualizo cada uno de ellos */
    FOREACH orderidd IN ARRAY orderids
    LOOP 
        /* Para producir el deadlock hacemos un UPDATE artificial */     
        UPDATE orders
        SET netamount = netamount;

        PERFORM pg_sleep(30);

        /* Obtengo los ids de los productos asociados al order con orderid orderidd */
        prod_ids := array(
            SELECT prod_id FROM orderdetail 
            WHERE orderdetail.orderid = orderidd
        );
        
        /* Actualizo el precio de cada orderdetail usando el precio del producto
            en la tabla products y usando el descuento NEW.promo */
        FOREACH prod_idd IN ARRAY prod_ids
        LOOP 
            pricee := (
                SELECT price FROM products 
                WHERE products.prod_id = prod_idd
            );

            UPDATE orderdetail
            SET price = pricee * (1.0 - NEW.promo/100.0)
            WHERE orderid = orderidd and prod_id = prod_idd;
        END LOOP;

        /* Actualizo el precio del carrito total, tabla orders */
        pricee := (
            SELECT sum(price*quantity) FROM orderdetail 
            WHERE orderdetail.orderid = orderidd
        );

        UPDATE orders
        SET netamount = pricee
        WHERE orders.orderid = orderidd;

        UPDATE orders
        SET totalamount = ROUND(netamount  * (1.0 + tax/100.0), 2)
        WHERE orders.orderid = orderidd;
        
    END LOOP;

    RETURN NEW;
END;
$tr_apply_promo$ LANGUAGE 'plpgsql';


CREATE TRIGGER apply_promo_discount_orders
AFTER UPDATE ON customers
FOR EACH ROW 
EXECUTE PROCEDURE tr_apply_promo();

