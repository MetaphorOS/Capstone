SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM Batch_info) 
        THEN (SELECT batch_number || ', ' || tomato FROM Batch_info WHERE batch_number = (SELECT MAX(batch_number) FROM Batch_info))
        ELSE 'No data available'
    END AS result;