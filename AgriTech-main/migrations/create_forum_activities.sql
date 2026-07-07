-- Migration: create questions, answers, activities tables

CREATE TABLE IF NOT EXISTS questions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  tags TEXT,
  status VARCHAR(32) DEFAULT 'open',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS answers (
  id SERIAL PRIMARY KEY,
  question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(id),
  body TEXT NOT NULL,
  upvotes INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS activities (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  farm_id INTEGER,
  crop_id INTEGER,
  activity_type VARCHAR(32),
  activity_date DATE,
  notes TEXT,
  attachments JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
