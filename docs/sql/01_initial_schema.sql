CREATE TABLE service_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    description VARCHAR(255)
);

CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type_id INTEGER REFERENCES service_types(id),
    status VARCHAR(20)
);

INSERT INTO service_types (name, description)
VALUES
    ('application', 'Прикладной сервис'),
    ('database', 'Сервис хранения данных'),
    ('monitoring', 'Сервис мониторинга'),
    ('storage', 'Сервис хранения файлов');

INSERT INTO services (name, type_id, status)
VALUES
    ('Web Service', 1, 'running'),
    ('Database Service', 2, 'running'),
    ('Monitoring Service', 3, 'maintenance');
