DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(256) NOT NULL,
    email VARCHAR(256),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_archived bool DEFAULT FALSE NOT NULL
);  

DROP PROCEDURE IF EXISTS InsertRand;
delimiter //
CREATE PROCEDURE IF NOT EXISTS InsertRand(IN NumRows INT)
    BEGIN
        DECLARE i INT;
        SET i = 1;
        START TRANSACTION;
        WHILE i <= NumRows DO
            INSERT INTO users (username, email, created_at, updated_at) VALUES (
                CONCAT('user', i,  '_', substr(md5(RAND()), 2, 5)),
                CONCAT(substr(md5(RAND()), 1, 13), '@gmail.com'),
                NOW(),
                NOW());
            SET i = i + 1;
        END WHILE;
        COMMIT;
    END//

CALL InsertRand(10000);
