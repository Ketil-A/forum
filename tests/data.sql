INSERT INTO user (username, password, email)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 'test@test.no'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', 'test2@test.no');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

INSERT INTO profile (user_id, firstname, lastname, bio)
VALUES
  ('0', 'testfirst', 'testlast', 'some text');

INSERT INTO comment (post_id, body, author_id, created)
VALUES
  (1, 'test' || x'0a' || 'testcommentbody', 1, '2018-01-01 00:00:00');