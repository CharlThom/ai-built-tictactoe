from datetime import datetime
from src.database import db
import bcrypt

class User:
    def __init__(self, id, username, email, password_hash, created_at=None, 
                 games_played=0, games_won=0, games_lost=0, games_drawn=0):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.games_played = games_played
        self.games_won = games_won
        self.games_lost = games_lost
        self.games_drawn = games_drawn
    
    @staticmethod
    def get_by_id(user_id):
        """Retrieve user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = db.fetch_one(query, (user_id,))
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                password_hash=result['password_hash'],
                created_at=result.get('created_at'),
                games_played=result.get('games_played', 0),
                games_won=result.get('games_won', 0),
                games_lost=result.get('games_lost', 0),
                games_drawn=result.get('games_drawn', 0)
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        """Retrieve user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = db.fetch_one(query, (username,))
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                password_hash=result['password_hash'],
                created_at=result.get('created_at'),
                games_played=result.get('games_played', 0),
                games_won=result.get('games_won', 0),
                games_lost=result.get('games_lost', 0),
                games_drawn=result.get('games_drawn', 0)
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        """Retrieve user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        result = db.fetch_one(query, (email,))
        if result:
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                password_hash=result['password_hash'],
                created_at=result.get('created_at'),
                games_played=result.get('games_played', 0),
                games_won=result.get('games_won', 0),
                games_lost=result.get('games_lost', 0),
                games_drawn=result.get('games_drawn', 0)
            )
        return None
    
    def update(self, **kwargs):
        """Update user fields"""
        allowed_fields = ['username', 'email']
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
                setattr(self, field, value)
        
        if update_fields:
            values.append(self.id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            db.execute(query, tuple(values))
    
    def verify_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))