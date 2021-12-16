CREATE INDEX idx_orders_status ON orders(status);

EXPLAIN
select count(*)
from orders
where status is null;

EXPLAIN
select count(*)
from orders
where status ='Shipped';

select count(*)
from orders
where status ='Paid';

select count(*)
from orders
where status ='Processed';