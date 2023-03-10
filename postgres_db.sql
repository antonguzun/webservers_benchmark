DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    user_id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username text NOT NULL,
    email text,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    is_archived bool DEFAULT FALSE NOT NULL
);

INSERT INTO
    users (username, email, created_at, updated_at)
SELECT
    'user' || i || '_' || substr(md5(random() :: text), 0, 6),
    substr(md5(random() :: text), 0, 14) || '@gmail.com',
    NOW(),
    NOW()
FROM
    generate_series(1, 10000) AS s(i);