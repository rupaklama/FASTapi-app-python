-- SQLite
INSERT INTO todos (id, title, description, priority, completed)
VALUES (
   2, 'Walk the dog', 'Take Fido for a walk in the park', 2, 0
);

-- SQLite
SELECT id, title, description, priority, completed
FROM todos
where id = 1
