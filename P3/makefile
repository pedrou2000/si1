export PGDATABASE := si1_p3
export PGPASSWORD = alumnodb
export DUMPFILE := dump_v1.5-P3.sql.gz
PSQL = psql

restart: drop_db create_db populate mongo
run:
	python3 -m app

export_pass:
	export PGPASSWORD='alumnodb'

drop_db:
	@echo Deleting Database
	dropdb -U $(PGPASSWORD) $(PGDATABASE)

create_db:
	@echo Creating Database
	createdb -U $(PGPASSWORD) $(PGDATABASE)

populate:
	@echo Populating database
	gunzip -c $(DUMPFILE) | $(PSQL)  -U $(PGPASSWORD) $(PGDATABASE)

distinct_cities:
	@echo Creating function
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < sql/ciudadesDistintas.sql

updPromo:
	@echo Creating function
	$(PSQL) -U $(PGPASSWORD) $(PGDATABASE) < sql/updPromo.sql

autocommitFalse:
	@echo Creating function
	\set AUTOCOMMIT off | $(PSQL) -U $(PGPASSWORD) $(PGDATABASE)

mongo:
	python3 app/createMongoDBFromPostgreSQLDB.py