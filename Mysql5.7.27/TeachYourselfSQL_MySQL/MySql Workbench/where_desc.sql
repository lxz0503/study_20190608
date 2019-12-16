SELECT 
    vend_id,
    vend_name,
    vend_address,
    vend_city,
    vend_country AS country
FROM
    tysql.vendors
WHERE
    vend_state IS NOT NULL
        OR vend_country = 'USA'
ORDER BY vend_city DESC;