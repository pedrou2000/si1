
CREATE TABLE new_table
AS (SELECT * FROM (SELECT imdb_actors.actorname AS actorname, imdb_actors.actorid AS actorid, table3.times AS times, imdb_movies.year AS year, imdb_movies.movietitle AS movietitle, table3.genre AS genre, imdb_directors.directorname AS directorname
					         FROM imdb_movies JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid,
						            (SELECT table2.actorid AS actorid, table2.genre AS genre, table2.times AS times
						             FROM (SELECT table1.actorid AS actorid, table1.genre AS genre, COUNT(table1.actorname) AS times
			  				               FROM (SELECT imdb_actors.actorid AS actorid, imdb_movies.movieid AS movie_id, imdb_movies.movietitle AS title, imdb_movies.year AS year, imdb_moviegenres.genre AS genre, imdb_actors.actorname AS actorname, imdb_directors.directorname AS directorname
				    			                   FROM imdb_movies JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid) AS table1
			  				               GROUP BY (table1.actorid, table1.genre)) AS table2
	     				           WHERE table2.times >= 4 AND table2.genre = 'Horror'
	     				           ORDER BY table2.times DESC) as table3
					        WHERE imdb_actors.actorid = table3.actorid
					        ORDER BY table3.times DESC) AS table4);

SELECT new_table.actorname AS Actor, new_table.times AS Num, new_table.year AS Debut, new_table.movietitle AS Film, new_table.directorname AS Director
FROM new_table INNER JOIN (SELECT actorid, MIN(year) MinYear
                           FROM new_table
                           GROUP BY actorid) AS table4
               ON table4.actorid = new_table.actorid
WHERE table4.MinYear = new_table.year;

DROP TABLE new_table;
