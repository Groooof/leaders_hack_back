CREATE TYPE role AS ENUM ('moderator', 'marker', 'undefined');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    role role DEFAULT 'undefined',
    is_superuser BOOLEAN DEFAULT FALSE,
    surname TEXT NOT NULL,
    name TEXT NOT NULL,
    patronymic TEXT
);

CREATE TABLE refresh_tokens (
    user_id INT NOT NULL,
    token UUID PRIMARY KEY,
    expires TIMESTAMP NOT NULL
);


INSERT INTO credentials (login, hashed_password, role, is_superuser, surname, name, patronymic)
VALUES
    ('purplemice', # pas: qwerty
    '61bd157b1250609998e641ce85b390d57f220548deeac8e8f825b417f106d6c4a6eb533baa624a8a555d03e1d7a98f3a80cf9df6f4d84f1173d636368be307e81f3e2fbad286029254b9fe47fa72c418',
    None,
    True,
    'Брюс',
    'Всемогущий'),
    ('tolik_135', # pas: 123
    'fe418524b619910011be8c00e2fdc8c416b6f5662d18e40b24d4b126d8ee850c55445b61e046c551667bfd218c6f3cbcf3806a8d2fc472f4d4104b3298a80a42de6d3d55a71ef02312993839fc7a71c9',
    'moderator',
    False,
    'Анатолий',
    'Модератор',
    'Васильевич'
    ),
    ('andr', # pas: 123
    'fe418524b619910011be8c00e2fdc8c416b6f5662d18e40b24d4b126d8ee850c55445b61e046c551667bfd218c6f3cbcf3806a8d2fc472f4d4104b3298a80a42de6d3d55a71ef02312993839fc7a71c9',
    'marker',
    False,
    'Андрей',
    'Разметчик №1',
    'Иванович'
    ),
    ('1anechka1', # pas: 123
    'fe418524b619910011be8c00e2fdc8c416b6f5662d18e40b24d4b126d8ee850c55445b61e046c551667bfd218c6f3cbcf3806a8d2fc472f4d4104b3298a80a42de6d3d55a71ef02312993839fc7a71c9',
    'marker',
    False,
    'Анна',
    'Разметчик №2',
    'Петровна')
