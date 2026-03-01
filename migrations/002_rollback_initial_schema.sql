-- Migration Rollback: Initial TicTacToe Schema
-- Description: Drops all tables, indexes, triggers, and functions created in 001_initial_schema.sql

BEGIN;

-- Drop triggers
DROP TRIGGER IF EXISTS update_games_updated_at ON games;

-- Drop trigger function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables (cascade will handle foreign key constraints)
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS boards CASCADE;
DROP TABLE IF EXISTS games CASCADE;

-- Indexes are automatically dropped with their tables

COMMIT;