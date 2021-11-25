export PGDATABASE := si1_p3
export PGPASSWORD = alumnodb
export DUMPFILE := dump_v1.5-P3.sql.gz
PSQL = psql

all: drop_db create_db populate update_db

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

