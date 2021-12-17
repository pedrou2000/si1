CREATE INDEX idx_orders_status ON orders(status);

ANALYZE VERBOSE orders;

EXPLAIN
select count(*)
from orders
where status is null;

EXPLAIN
select count(*)
from orders
where status ='Shipped';

EXPLAIN
select count(*)
from orders
where status ='Paid';

EXPLAIN
select count(*)
from orders
where status ='Processed';