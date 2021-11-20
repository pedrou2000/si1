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
