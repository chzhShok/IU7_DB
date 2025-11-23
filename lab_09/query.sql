-- cinema/top_movies.sql
-- топ-10 самых просматриваемых фильмов
SELECT 
    m.movie_id,
    m.title,
    COUNT(vh.view_id) AS total_views,
    AVG(vh.viewed_percentage) AS avg_completion
FROM cinema.viewing_history vh
JOIN cinema.movies m ON vh.movie_id = m.movie_id
GROUP BY m.movie_id, m.title
ORDER BY total_views DESC
LIMIT 10;
