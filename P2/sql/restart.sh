export PGPASSWORD='alumnodb'
dropdb -U alumnodb si1
createdb -U alumnodb si1
gunzip -c dump_v1.4.sql.gz | psql -U alumnodb si1
psql -U alumnodb si1 < actualiza.sql
psql -U alumnodb si1 < setOrderAmount.sql
psql -U alumnodb si1 < setPrice.sql
psql -U alumnodb si1 < getTopSales.sql
psql -U alumnodb si1 < getTopActors.sql
psql -U alumnodb si1 < updOrders.sql
psql -U alumnodb si1 < updInventoryAndCustomer.sql
