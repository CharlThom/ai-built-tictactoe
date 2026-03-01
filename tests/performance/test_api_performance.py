import pytest
import asyncio
import aiohttp
from load_test import TicTacToeLoadTester


class TestAPIPerformance:
    """Performance test suite for TicTacToe API endpoints"""
    
    @pytest.fixture
    def tester(self):
        """Create load tester instance"""
        return TicTacToeLoadTester(base_url="http://localhost:3000/api")
    
    @pytest.mark.asyncio
    async def test_create_game_performance(self, tester):
        """Test game creation endpoint performance under load"""
        results = await tester.stress_test_endpoint("create_game", 100)
        analysis = tester.analyze_results(results)
        
        stats = analysis["create_game"]
        assert stats["avg_response_time"] < 0.05, "Average response time should be under 50ms"
        assert stats["p95_response_time"] < 0.1, "P95 response time should be under 100ms"
        assert stats["success_rate"] == 100, "All requests should succeed"
    
    @pytest.mark.asyncio
    async def test_move_validation_performance(self, tester):
        """Test move validation endpoint performance"""
        results = await tester.stress_test_endpoint("validate_move", 500)
        analysis = tester.analyze_results(results)
        
        stats = analysis["validate_move"]
        assert stats["avg_response_time"] < 0.03, "Average response time should be under 30ms"
        assert stats["p99_response_time"] < 0.1, "P99 response time should be under 100ms"
        assert stats["max_response_time"] < 0.2, "Max response time should be under 200ms"
    
    @pytest.mark.asyncio
    async def test_game_state_retrieval_performance(self, tester):
        """Test game state endpoint performance under high load"""
        results = await tester.stress_test_endpoint("get_game_state", 1000)
        analysis = tester.analyze_results(results)
        
        stats = analysis["get_game_state"]
        assert stats["avg_response_time"] < 0.04, "Average response time should be under 40ms"
        assert stats["median_response_time"] < 0.03, "Median response time should be under 30ms"
        assert stats["success_rate"] == 100, "All requests should succeed"
    
    @pytest.mark.asyncio
    async def test_concurrent_games_load(self, tester):
        """Test system performance with concurrent games"""
        results = await tester.run_concurrent_games(25)
        analysis = tester.analyze_results(results)
        
        # Verify all endpoints perform well under concurrent load
        for endpoint, stats in analysis.items():
            assert stats["success_rate"] >= 99, f"{endpoint} should have at least 99% success rate"
            assert stats["p95_response_time"] < 0.15, f"{endpoint} p95 should be under 150ms"
    
    @pytest.mark.asyncio
    async def test_full_game_flow_performance(self, tester):
        """Test performance of complete game flow"""
        async with aiohttp.ClientSession() as session:
            results = await tester.simulate_full_game(session)
        
        analysis = tester.analyze_results(results)
        
        # Ensure make_move endpoint is performant
        if "make_move" in analysis:
            move_stats = analysis["make_move"]
            assert move_stats["avg_response_time"] < 0.05, "Move execution should be fast"
            assert all(r["status"] == 200 for r in results if r["endpoint"] == "make_move"), "All moves should succeed"
    
    @pytest.mark.asyncio
    async def test_invalid_move_validation_performance(self, tester):
        """Test performance of invalid move validation"""
        async with aiohttp.ClientSession() as session:
            # Create game and make a move
            create_result = await tester.create_game(session)
            game_id = create_result["game_id"]
            await tester.make_move(session, game_id, 0, "X")
            
            # Test validation of already occupied position
            results = []
            for _ in range(100):
                result = await tester.validate_move(session, game_id, 0)
                results.append(result)
        
        analysis = tester.analyze_results(results)
        stats = analysis["validate_move"]
        
        assert stats["avg_response_time"] < 0.03, "Invalid move validation should be fast"
        assert stats["success_rate"] == 100, "Validation requests should succeed"
    
    @pytest.mark.asyncio
    async def test_rapid_sequential_moves(self, tester):
        """Test performance of rapid sequential moves in a single game"""
        async with aiohttp.ClientSession() as session:
            create_result = await tester.create_game(session)
            game_id = create_result["game_id"]
            
            results = []
            moves = [(0, "X"), (1, "O"), (2, "X"), (3, "O"), (4, "X")]
            
            for position, player in moves:
                result = await tester.make_move(session, game_id, position, player)
                results.append(result)
        
        analysis = tester.analyze_results(results)
        stats = analysis["make_move"]
        
        assert stats["max_response_time"] < 0.1, "Even rapid moves should complete quickly"
        assert all(r["valid"] for r in results), "All moves should be valid"
    
    @pytest.mark.asyncio
    async def test_throughput_capacity(self, tester):
        """Test overall system throughput capacity"""
        import time
        
        start_time = time.time()
        results = await tester.run_concurrent_games(100)
        total_time = time.time() - start_time
        
        total_requests = len(results)
        throughput = total_requests / total_time
        
        assert throughput > 50, f"System should handle at least 50 req/sec, got {throughput:.2f}"
        
        analysis = tester.analyze_results(results)
        overall_success = sum(stats["total_requests"] * stats["success_rate"] / 100 
                             for stats in analysis.values())
        
        assert overall_success / total_requests >= 0.99, "Overall success rate should be 99%+"