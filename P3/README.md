PRÁCTICA 3 SI1


Autores:
-Pareja 5 (grupo 1402): Pedro Urbina Rodríguez y César Ramírez Martínez


Organización del material entregado:

-Directorio "app": (almacena todos los archivos relacionados con la página web)

	-createMongoDBFromPostgreSQLDB.py: archivo que crea de manera automática la base de datos documental en mongoDB, de la que se extraerá la información necesaria para configurar la web "topUK".

	-database.py: archivo encargado de crear las transacciones que se ejecutarán desde la web "borraCiudad".

	-routes.py: archivo encargado de presentar los datos obtenidos de los archivos.

	"createMongoDBFromPostgreSQLDB.py" y "database.py" en sus respectivos archivos html.

	-Directorio "templates": con los archivos html necesarios para la visulización de las páginas web solicitadas.

-Directorio "sql": (almacena todos los archivos relacionados con la base de datos sql)

	-ciudadesDistintas.sql: archivo que contiene la definición de la función solicitada en el apartado E, así como las sentencias necesarias para crear el índice que mejor rendimiento obtiene para la ejecución de esta función.

	-countStatus.sql: archivo que contiene las consultas del Anexo 2 y las sentencias necesarias para crear el índice y el ANALYZE.

	-updPromo.sql: archivo que continene el trigger encargado de crear una nueva columna promo en la tabla cutomers. Gracias a este trigger y junto con la transacciones ejecutadas en el archivo database.py conseguiremos explicar muchos de los conceptos requeridos por esta práctica.

-makefile: (archivo para ejecutar todos los archivos y funcionalidades de la práctica):

	COMANDOS:

	-make/make restart: comando que DEBE ejecutarse al descargar la práctica para establecer y configurar la base de datos SQL y todo lo relacionado con mongoDB.

	-make run: comando para correr la aplicación y poder acceder a las páginas de "topUK" y "borraCiudad".

	-make distinct_cities: comando para crear la función solicitada en el apartado E, así como el índice que mejor rendimiento obtiene para la ejecución de esta función.

	-make drop_db: comando para destruir la base de datos.

	-make create_db: comando para crear la base de datos.

	-make populate: comando para poblar la base de datos.

	-make updPromo: comando para crear el trigger solicitado en el apartado.

	-make mongo: comando para ejecutar el archivo que crea la base de datos documental.

-Memoria Práctica 3.pdf: (archivo que contiene todas las discusiones sobre los ejercicios y decisiones tomadas para la realización de la práctica)


INSTRUCCIONES PARA EJECUTAR LA PRÁCTICA:

1. Ejecutar el comando "make" o "make restart".
2. Ejecutar el comando "make run" para acceder a las páginas web solicitadas por la práctica.
3. Ejecutar el comando "make distinct_cities" para crear la función solicitada en el apartado E junto con el índice que mejor rendimiento obtiene.
