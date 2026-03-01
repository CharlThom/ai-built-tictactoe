-- Migration: Initial TicTacToe Schema
-- Created: 2024-01-01
-- Description: Creates Game, Board, and Player tables with indexes and constraints

BEGIN;

-- Create Game table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL CHECK (status IN ('in_progress', 'completed')),
    winner VARCHAR(10) CHECK (winner IN ('player1', 'player2', 'draw') OR winner IS NULL),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on game status for filtering active games
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_games_created_at ON games(created_at);

-- Create Board table
CREATE TABLE IF NOT EXISTS boards (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL UNIQUE,
    cell_states JSONB NOT NULL DEFAULT '[null,null,null,null,null,null,null,null,null]',
    current_turn VARCHAR(10) NOT NULL CHECK (current_turn IN ('player1', 'player2')),
    CONSTRAINT fk_board_game FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

-- Create index on game_id for board lookups
CREATE INDEX idx_boards_game_id ON boards(game_id);

-- Create Player table
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    player_number INTEGER NOT NULL CHECK (player_number IN (1, 2)),
    symbol CHAR(1) NOT NULL CHECK (symbol IN ('X', 'O')),
    CONSTRAINT fk_player_game FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    CONSTRAINT unique_player_per_game UNIQUE (game_id, player_number)
);

-- Create index on game_id for player lookups
CREATE INDEX idx_players_game_id ON players(game_id);

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for games table
CREATE TRIGGER update_games_updated_at
    BEFORE UPDATE ON games
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;