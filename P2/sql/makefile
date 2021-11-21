export PGDATABASE := si1
export PGPASSWORD = 'alumnodb'
export DUMPFILE := dump_v1.4.sql.gz
PSQL = psql

all: drop_db create_db populate update_db

drop_db:
	@echo Deleting Database
	dropdb -U $(PGPASSWORD) $(PGDATABASE)

create_db:
	@echo Creating Database
	createdb -U $(PGPASSWORD) $(PGDATABASE)

populate:
	@echo Populating database
	gunzip -c $(DUMPFILE) | $(PSQL)  -U $(PGPASSWORD) $(PGDATABASE)

update_db:
	@echo Updating Database
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < setOrderAmount.sql
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < setPrice.sql
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < actualiza.sql
	@echo Creating the triggers
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < updOrders.sql
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < updInventoryAndCustomer.sql
	@echo Executing getTopSales function
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < getTopSales.sql
	@echo Executing getTopActors function
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < getTopActors.sql
	
getTopSales:
	@echo Executing getTopSales function
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < getTopSales.sql

getTopActors:
	@echo Executing getTopActors function
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < getTopActors.sql
