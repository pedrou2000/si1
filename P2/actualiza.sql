
/* order foreign key to orderdetail table */
ALTER TABLE orderdetail ADD CONSTRAINT FK_orderdetail_ord FOREIGN KEY (orderid) REFERENCES orders (orderid) ON DELETE CASCADE;

/* product foreign key to inventory table */
ALTER TABLE inventory ADD CONSTRAINT FK_inv_prod FOREIGN KEY (prod_id) REFERENCES products (prod_id) ON DELETE CASCADE;

/* prod_id foreign key to orderdetail table */
ALTER TABLE orderdetail ADD CONSTRAINT FK_orderdetail_prod FOREIGN KEY (prod_id) REFERENCES products (prod_id) ON DELETE SET NULL;

/* actor_id foreign key to actormovie table */
ALTER TABLE imdb_actormovies ADD CONSTRAINT FK_actormovie_actor FOREIGN KEY (actorid) REFERENCES imdb_actors (actorid) ON DELETE CASCADE;

/* movie_id foreign key to actormovie table */
ALTER TABLE imdb_actormovies ADD CONSTRAINT FK_actormovie_movie FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid) ON DELETE CASCADE;

/* customer_id foreign key to orders table */
ALTER TABLE orders ADD CONSTRAINT FK_order_customer FOREIGN KEY (customerid) REFERENCES customers (customerid) ON DELETE CASCADE;
