CREATE OR REPLACE FUNCTION getTopActors(genre varchar(128), OUT Actor varchar(128), OUT Num bigint, OUT Debut text, OUT Film varchar(255), OUT Id integer, OUT Director varchar(128))
RETURNS SETOF RECORD AS
$$
BEGIN
RETURN QUERY
  WITH initial_data AS
  	(SELECT imdb_actors.actorname, imdb_actors.actorid, imdb_movies.movieid, imdb_movies.movietitle, imdb_movies.year, imdb_genres.genre
  	FROM imdb_movies JOIN imdb_genremovies ON imdb_movies.movieid = imdb_genremovies.movieid
             JOIN imdb_genres ON imdb_genremovies.genreid = imdb_genres.genreid AND imdb_genres.genre = $1
  					 JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid
  					 JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid),
   four_count_filter AS
  	 (SELECT initial_data.*, actor_count.count
  	 FROM initial_data JOIN (SELECT actorid, COUNT(*)
  							FROM initial_data
  							GROUP BY actorid
  							HAVING COUNT(*) >= 4
  							) AS actor_count ON actor_count.actorid = initial_data.actorid)
  SELECT four_count_filter.actorname AS Actor, four_count_filter.count AS Num, four_count_filter.year AS Debut, four_count_filter.movietitle AS Film, four_count_filter.movieid AS Id, imdb_directors.directorname AS Director
  FROM four_count_filter JOIN (SELECT actorid, MIN(year) AS min_year
  									 FROM four_count_filter
  									 GROUP BY actorid) AS min_year_q
  								ON min_year_q.actorid = four_count_filter.actorid AND min_year_q.min_year = four_count_filter.year
  					   JOIN imdb_directormovies ON imdb_directormovies.movieid = four_count_filter.movieid
  					   JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid
  ORDER BY count DESC;
END;
$$
LANGUAGE 'plpgsql' STABLE;

SELECT *
FROM getTopActors('Fantasy');

/*
CREATE OR REPLACE FUNCTION getTopActors(film_genre char)
RETURNS TABLE (Actor varchar(128), Num bigint, Debut text, Film varchar(255), Director varchar(128)) AS
$$
BEGIN
RETURN QUERY
  SELECT new_table.actorname AS Actor, new_table.times AS Num, new_table.year AS Debut, new_table.movietitle AS Film, new_table.directorname AS Director
  FROM (SELECT imdb_actors.actorname AS actorname, imdb_actors.actorid AS actorid, table3.times AS times, imdb_movies.year AS year, imdb_movies.movietitle AS movietitle, table3.genre AS genre, imdb_directors.directorname AS directorname
                    FROM imdb_movies JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid,
                         (SELECT table2.actorid AS actorid, table2.genre AS genre, table2.times AS times
                          FROM (SELECT table1.actorid AS actorid, table1.genre AS genre, COUNT(table1.actorname) AS times
                                FROM (SELECT imdb_actors.actorid AS actorid, imdb_movies.movieid AS movie_id, imdb_movies.movietitle AS title, imdb_movies.year AS year, imdb_moviegenres.genre AS genre, imdb_actors.actorname AS actorname, imdb_directors.directorname AS directorname
                                      FROM imdb_movies JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid) AS table1
                                GROUP BY (table1.actorid, table1.genre)) AS table2
                          WHERE table2.times >= 4 AND table2.genre = film_genre
                          ORDER BY table2.times DESC) AS table3
                   WHERE imdb_actors.actorid = table3.actorid
                   ORDER BY table3.times DESC) AS new_table INNER JOIN (SELECT actorid, MIN(year) MinYear
                             FROM (SELECT imdb_actors.actorname AS actorname, imdb_actors.actorid AS actorid, table3.times AS times, imdb_movies.year AS year, imdb_movies.movietitle AS movietitle, table3.genre AS genre, imdb_directors.directorname AS directorname
                             					         FROM imdb_movies JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid,
                             						            (SELECT table2.actorid AS actorid, table2.genre AS genre, table2.times AS times
                             						             FROM (SELECT table1.actorid AS actorid, table1.genre AS genre, COUNT(table1.actorname) AS times
                             			  				               FROM (SELECT imdb_actors.actorid AS actorid, imdb_movies.movieid AS movie_id, imdb_movies.movietitle AS title, imdb_movies.year AS year, imdb_moviegenres.genre AS genre, imdb_actors.actorname AS actorname, imdb_directors.directorname AS directorname
                             				    			                   FROM imdb_movies JOIN imdb_moviegenres ON imdb_movies.movieid = imdb_moviegenres.movieid JOIN imdb_actormovies ON imdb_actormovies.movieid = imdb_movies.movieid JOIN imdb_actors ON imdb_actormovies.actorid = imdb_actors.actorid JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid JOIN imdb_directors ON imdb_directors.directorid = imdb_directormovies.directorid) AS table1
                             			  				               GROUP BY (table1.actorid, table1.genre)) AS table2
                             	     				           WHERE table2.times >= 4 AND table2.genre = film_genre
                             	     				           ORDER BY table2.times DESC) AS table3
                             					        WHERE imdb_actors.actorid = table3.actorid
                             					        ORDER BY table3.times DESC) AS table5
                             GROUP BY actorid) AS table4
                 ON table4.actorid = new_table.actorid
  WHERE table4.MinYear = new_table.year;

END;
$$
LANGUAGE 'plpgsql' STABLE;
*/
