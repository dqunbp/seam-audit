ALTER TABLE jobs ADD COLUMN source_image_id INTEGER REFERENCES images(id);
