from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import time

# Game metrics
games_started_total = Counter(
    'tictactoe_games_started_total',
    'Total number of games started'
)

games_completed_total = Counter(
    'tictactoe_games_completed_total',
    'Total number of games completed',
    ['result']  # win, draw, abandoned
)

moves_total = Counter(
    'tictactoe_moves_total',
    'Total number of moves made'
)

game_duration_seconds = Histogram(
    'tictactoe_game_duration_seconds',
    'Duration of completed games in seconds',
    buckets=[10, 30, 60, 120, 300, 600]
)

active_games = Gauge(
    'tictactoe_active_games',
    'Number of currently active games'
)

# HTTP metrics
http_requests_total = Counter(
    'tictactoe_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'tictactoe_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Application health
app_info = Gauge(
    'tictactoe_app_info',
    'Application information',
    ['version', 'environment']
)

def metrics_endpoint():
    """Prometheus metrics endpoint handler"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def track_request(method, endpoint, status, duration):
    """Track HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

def init_metrics(app_version='1.0.0', environment='production'):
    """Initialize application metrics"""
    app_info.labels(version=app_version, environment=environment).set(1)