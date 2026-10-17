SELECT * FROM services ORDER BY id;

SELECT name, status
FROM services
ORDER BY id;

SELECT *
FROM services
WHERE status = 'running';

SELECT s.id, s.name, st.name AS type, s.status
FROM services AS s
JOIN service_types AS st ON st.id = s.type_id
ORDER BY s.id;

INSERT INTO services (name, type_id, status)
SELECT 'Backup Service', id, 'stopped'
FROM service_types
WHERE name = 'application';

UPDATE services
SET status = 'running'
WHERE name = 'Backup Service';

SELECT s.id, s.name, st.name AS type, s.status
FROM services AS s
JOIN service_types AS st ON st.id = s.type_id
WHERE s.name = 'Backup Service';

DELETE FROM services
WHERE name = 'Backup Service';
