CREATE TYPE role AS ENUM ('moderator', 'marker', 'undefined');

CREATE TABLE credentials (
    id SERIAL PRIMARY KEY,
    login TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    role role DEFAULT 'undefined',
    is_superuser BOOLEAN DEFAULT FALSE
);

CREATE TABLE refresh_tokens (
    user_id INT NOT NULL,
    token UUID PRIMARY KEY,
    expires TIMESTAMP NOT NULL
);


INSERT INTO credentials (login, hashed_password, is_superuser)
VALUES
    ('purplemice', 
    '61bd157b1250609998e641ce85b390d57f220548deeac8e8f825b417f106d6c4a6eb533baa624a8a555d03e1d7a98f3a80cf9df6f4d84f1173d636368be307e81f3e2fbad286029254b9fe47fa72c418',
    True);
