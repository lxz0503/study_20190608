SELECT 
    a.score AS Score, COUNT(DISTINCT b.score) AS Rank
FROM
    scores a
        JOIN
    scores b
WHERE
    b.score >= a.score
GROUP BY a.id
ORDER BY a.score DESC