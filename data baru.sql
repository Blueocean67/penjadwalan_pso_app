DELETE FROM guru;
DELETE FROM sqlite_sequence WHERE name='guru';
CREATE TABLE IF NOT EXISTS guru (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_guru TEXT NOT NULL,
    mapel_id INTEGER NOT NULL,
    max_jam INTEGER DEFAULT 20,
    UNIQUE(nama_guru, mapel_id)
);
INSERT INTO guru (nama_guru, mapel_id, max_jam) VALUES
('Evi Handayani S.Pd', 1, 4),
('Annisa S.Pd', 2, 3),
('Budi Santoso', 3, 3),
('Citra Lestari', 4, 5),
('Dewi Anggraini', 5, 3),
('Fajar Pratama', 6, 2),
('Gita Wulandari', 7, 2),
('Hendra Kurniawan', 8, 4),
('Indra Lesmana', 9, 2),
('Joko Susilo', 10, 2);
