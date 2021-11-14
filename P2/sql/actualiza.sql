/* product foreign key to inventory table */
ALTER TABLE inventory ADD CONSTRAINT FK_inv_prod FOREIGN KEY (prod_id) REFERENCES products (prod_id) ON DELETE CASCADE;
/*ALTER TABLE inventory ADD PRIMARY KEY (prod_id);*/

/* customer_id foreign key to orders table */
ALTER TABLE orders ADD CONSTRAINT FK_order_customer FOREIGN KEY (customerid) REFERENCES customers (customerid) ON DELETE CASCADE;

/* prod_id foreign key to orderdetail table */
ALTER TABLE orderdetail ADD CONSTRAINT FK_orderdetail_prod FOREIGN KEY (prod_id) REFERENCES products (prod_id) ON DELETE SET NULL;

/* order foreign key to orderdetail table */
ALTER TABLE orderdetail ADD CONSTRAINT FK_orderdetail_ord FOREIGN KEY (orderid) REFERENCES orders (orderid) ON DELETE CASCADE;

/* eliminate duplicated rows in orderdetail */
/* we first find the rows in orderdetail that has the same (orderid, prod_id) and we GROUP them. Then we create an auxiliary table
    that has one row per (orderid, prod_id) that were duplicated in the orderdetail table. Each row in the new table will have
    as quantity the sum of the quantities from the duplicated rows, and as price the average of the prices from the duplicated rows */
SELECT DISTINCT orderid, prod_id, AVG(price) AS price, SUM(quantity) AS quantity
INTO duplicate_table
FROM orderdetail
GROUP BY (orderid, prod_id)
HAVING COUNT((orderid, prod_id)) > 1;

/* from the original table, we delete ALL the rows that has the same (orderid, prod_id) as any of the rows in the new table */
DELETE FROM orderdetail
WHERE (orderid, prod_id)
IN (SELECT orderid, prod_id FROM duplicate_table);

/* finally we add to orderdetail the rows of the new table we created. This way we will only have one row from the originally duplicated rows,
  with the sum of its quantities */
INSERT INTO orderdetail
SELECT *
FROM duplicate_table;

/* eliminate the auxiliary table */
DROP TABLE duplicate_table;

/* double primary key in orderdetail */
ALTER TABLE orderdetail ADD PRIMARY KEY (orderid, prod_id);

/* actor_id foreign key to actormovie table */
ALTER TABLE imdb_actormovies ADD CONSTRAINT FK_actormovie_actor FOREIGN KEY (actorid) REFERENCES imdb_actors (actorid) ON DELETE CASCADE;

/* movie_id foreign key to actormovie table */
ALTER TABLE imdb_actormovies ADD CONSTRAINT FK_actormovie_movie FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid) ON DELETE CASCADE;

/* double primary key in imdb_actormovies */
ALTER TABLE imdb_actormovies ADD CONSTRAINT imdb_actormovies_pkey PRIMARY KEY (movieid, actorid);

/* delete numpartitipation from primary key tuple */
ALTER TABLE imdb_directormovies DROP CONSTRAINT imdb_directormovies_pkey;
ALTER TABLE imdb_directormovies ADD CONSTRAINT imdb_directormovies_pkey PRIMARY KEY (directorid, movieid);


/* alert table */
CREATE TABLE alerts();
ALTER TABLE alerts ADD prod_id int;
ALTER TABLE alerts ADD PRIMARY KEY (prod_id);
ALTER TABLE alerts ADD CONSTRAINT FK_alert_inventory FOREIGN KEY (prod_id) REFERENCES inventory (prod_id) ON DELETE CASCADE;
ALTER TABLE alerts ADD date timestamp;

/* Add ‘loyalty’ to ‘customers’ table, with 0 default value */
ALTER TABLE customers ADD loyalty int NOT NULL CONSTRAINT loyalty_col DEFAULT (0);
/* Add balance to ‘customers’ table, with 0 default value */
ALTER TABLE customers ADD balance int NOT NULL CONSTRAINT balance_col DEFAULT (0);

/* function setCustomersBalance(IN initialBalance bigint); */
CREATE PROCEDURE setCustomersBalance (IN maxBalance bigint)
LANGUAGE plpgsql
as $$
BEGIN
	UPDATE customers SET balance = floor(random() * (maxBalance + 1))::int;
END $$;

/* call the procedure with N = 100 */
CALL setCustomersBalance(100);

/* call the procedure */
CALL setOrderAmount();


/* create imdb_countries, imdb_genres, imdb_languages tables */
/* imdb_countrymovies */
CREATE TABLE imdb_countries
AS
	SELECT country
	FROM imdb_moviecountries
	GROUP BY country
	ORDER BY country;

ALTER TABLE imdb_countries ADD COLUMN countryid SERIAL NOT NULL PRIMARY KEY;

/* Add a column for storing customer's points */
ALTER TABLE customers ADD COLUMN points int NOT NULL DEFAULT(0);

CREATE TABLE imdb_countrymovies();
ALTER TABLE imdb_countrymovies ADD countryid int;
ALTER TABLE imdb_countrymovies ADD movieid int;
ALTER TABLE imdb_countrymovies ADD CONSTRAINT FK_countrymovies_country FOREIGN KEY (countryid) REFERENCES imdb_countries (countryid) ON DELETE CASCADE;
ALTER TABLE imdb_countrymovies ADD CONSTRAINT FK_countrymovies_movie FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid) ON DELETE CASCADE;
ALTER TABLE imdb_countrymovies ADD CONSTRAINT imdb_countrymovies_pkey PRIMARY KEY (movieid, countryid);
INSERT INTO imdb_countrymovies (movieid, countryid)
SELECT imdb_movies.movieid, imdb_countries.countryid
				FROM imdb_countries JOIN imdb_moviecountries ON imdb_countries.country = imdb_moviecountries.country
														JOIN imdb_movies ON imdb_movies.movieid = imdb_moviecountries.movieid;
DROP TABLE imdb_moviecountries;

/* imdb_genremovies */
CREATE TABLE imdb_genres
AS
	SELECT genre
	FROM imdb_moviegenres
	GROUP BY genre
	ORDER BY genre;

ALTER TABLE imdb_genres ADD COLUMN genreid SERIAL NOT NULL PRIMARY KEY;

CREATE TABLE imdb_genremovies();
ALTER TABLE imdb_genremovies ADD genreid int;
ALTER TABLE imdb_genremovies ADD movieid int;
ALTER TABLE imdb_genremovies ADD CONSTRAINT FK_genremovies_country FOREIGN KEY (genreid) REFERENCES imdb_genres (genreid) ON DELETE CASCADE;
ALTER TABLE imdb_genremovies ADD CONSTRAINT FK_genremovies_movie FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid) ON DELETE CASCADE;
ALTER TABLE imdb_genremovies ADD CONSTRAINT imdb_genremovies_pkey PRIMARY KEY (movieid, genreid);
INSERT INTO imdb_genremovies (movieid, genreid)
SELECT imdb_movies.movieid, imdb_genres.genreid
				FROM imdb_genres JOIN imdb_moviegenres ON imdb_genres.genre = imdb_moviegenres.genre
												 JOIN imdb_movies ON imdb_movies.movieid = imdb_moviegenres.movieid;
DROP TABLE imdb_moviegenres;

/* imdb_languagemovies */
CREATE TABLE imdb_languages
AS
	SELECT language, extrainformation
	FROM imdb_movielanguages
	GROUP BY (language, extrainformation)
	ORDER BY language;

ALTER TABLE imdb_languages ADD COLUMN languageid SERIAL NOT NULL PRIMARY KEY;

CREATE TABLE imdb_languagemovies();
ALTER TABLE imdb_languagemovies ADD languageid int;
ALTER TABLE imdb_languagemovies ADD movieid int;
ALTER TABLE imdb_languagemovies ADD CONSTRAINT FK_languagemovies_language FOREIGN KEY (languageid) REFERENCES imdb_languages (languageid) ON DELETE CASCADE;
ALTER TABLE imdb_languagemovies ADD CONSTRAINT FK_languagemovies_movie FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid) ON DELETE CASCADE;
ALTER TABLE imdb_languagemovies ADD CONSTRAINT imdb_languagemovies_pkey PRIMARY KEY (movieid, languageid);
INSERT INTO imdb_languagemovies (movieid, languageid)
SELECT imdb_movies.movieid, imdb_languages.languageid
				FROM imdb_languages JOIN imdb_movielanguages ON imdb_languages.language = imdb_movielanguages.language
												 JOIN imdb_movies ON imdb_movies.movieid = imdb_movielanguages.movieid;
DROP TABLE imdb_movielanguages;
