-- Table: kaizen
CREATE TABLE kaizen (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  action TEXT NOT NULL,
  date DATE NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT FALSE
);

-- Index pour optimiser les requêtes par user_id et date
CREATE INDEX idx_kaizen_user_date ON kaizen (user_id, date);

-- Table: zazen_sessions
CREATE TABLE zazen_sessions (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  duration INT NOT NULL, -- Durée en secondes
  triggered_by TEXT -- Ex: "iris", "user"
);

-- Index pour optimiser les requêtes par user_id et timestamp
CREATE INDEX idx_zazen_user_timestamp ON zazen_sessions (user_id, timestamp);
