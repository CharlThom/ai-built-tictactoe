from flask import Blueprint, request, jsonify, g
from src.middleware.subscription_middleware import (
    require_premium,
    check_game_limit_middleware,
    SubscriptionMiddleware
)
from src.middleware.auth_middleware import require_auth
from src.models.game import Game, GameMode
from src.models.user import User
from datetime import datetime

game_bp = Blueprint('games', __name__, url_prefix='/api/games')

@game_bp.route('', methods=['POST'])
@require_auth
@check_game_limit_middleware
def create_game():
    """Create a new game with subscription-based limits"""
    data = request.get_json()
    user_id = g.user.id
    
    game_mode = data.get('mode', GameMode.STANDARD)
    
    # Premium-only game modes
    premium_modes = [GameMode.TOURNAMENT, GameMode.RANKED, GameMode.CUSTOM]
    
    if game_mode in premium_modes:
        if not SubscriptionMiddleware.has_premium_access(user_id):
            return jsonify({
                'error': 'Premium subscription required for this game mode',
                'code': 'PREMIUM_MODE',
                'mode': game_mode
            }), 403
    
    # Create game
    game = Game(
        user_id=user_id,
        mode=game_mode,
        board_state='         ',  # Empty 3x3 board
        current_player='X',
        status='active'
    )
    game.save()
    
    return jsonify({
        'success': True,
        'game': game.to_dict(),
        'subscription_info': g.game_limit_info
    }), 201

@game_bp.route('/tournament', methods=['POST'])
@require_auth
@require_premium
def create_tournament():
    """Create tournament game - premium feature only"""
    data = request.get_json()
    user_id = g.user.id
    
    tournament_name = data.get('name', 'Unnamed Tournament')
    max_players = data.get('max_players', 8)
    
    game = Game(
        user_id=user_id,
        mode=GameMode.TOURNAMENT,
        board_state='         ',
        current_player='X',
        status='waiting',
        metadata={
            'tournament_name': tournament_name,
            'max_players': max_players,
            'players': [user_id]
        }
    )
    game.save()
    
    return jsonify({
        'success': True,
        'tournament': game.to_dict()
    }), 201

@game_bp.route('/stats/advanced', methods=['GET'])
@require_auth
@require_premium
def get_advanced_stats():
    """Get advanced game statistics - premium feature"""
    user_id = g.user.id
    
    games = Game.query.filter_by(user_id=user_id).all()
    
    stats = {
        'total_games': len(games),
        'wins': len([g for g in games if g.winner_id == user_id]),
        'losses': len([g for g in games if g.winner_id and g.winner_id != user_id]),
        'draws': len([g for g in games if g.status == 'draw']),
        'win_rate': 0,
        'average_moves': 0,
        'favorite_opening': None,
        'performance_by_mode': {}
    }
    
    if stats['total_games'] > 0:
        stats['win_rate'] = round((stats['wins'] / stats['total_games']) * 100, 2)
    
    return jsonify({
        'success': True,
        'stats': stats
    }), 200

@game_bp.route('/subscription-status', methods=['GET'])
@require_auth
def get_subscription_status():
    """Get current user's subscription status and game limits"""
    user_id = g.user.id
    
    has_premium = SubscriptionMiddleware.has_premium_access(user_id)
    limit_info = SubscriptionMiddleware.check_game_limit(user_id)
    subscription = SubscriptionMiddleware.get_user_subscription(user_id)
    
    return jsonify({
        'success': True,
        'has_premium': has_premium,
        'tier': subscription.tier if subscription else 'free',
        'games_remaining': limit_info['games_remaining'],
        'subscription_expires': subscription.current_period_end.isoformat() if subscription else None,
        'features': {
            'unlimited_games': has_premium,
            'tournament_mode': has_premium,
            'ranked_mode': has_premium,
            'advanced_stats': has_premium,
            'ad_free': has_premium
        }
    }), 200