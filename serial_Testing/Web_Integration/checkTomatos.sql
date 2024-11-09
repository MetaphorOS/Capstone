SELECT 
    b.batch_number,
    b.tomato AS total_tomatoes,
    COALESCE(r.tomato, 0) AS ripe_tomatoes,
    COALESCE(u.tomato, 0) AS unripe_tomatoes,
    COALESCE(t.tomato, 0) AS twilight_zone_tomatoes
FROM 
    Batch_info b
LEFT JOIN 
    Ripe r ON b.batch_number = r.batch_number
LEFT JOIN 
    Unripe u ON b.batch_number = u.batch_number
LEFT JOIN 
    Twilight_zone t ON b.batch_number = t.batch_number;