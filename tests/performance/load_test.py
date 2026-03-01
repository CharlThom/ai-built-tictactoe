import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json


class TicTacToeLoadTester:
    """Load and performance testing for TicTacToe backend API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:3000/api"):
        self.base_url = base_url
        self.results = []
        
    async def create_game(self, session: aiohttp.ClientSession) -> Dict:
        """Create a new game and measure response time"""
        start = time.time()
        async with session.post(f"{self.base_url}/games") as response:
            duration = time.time() - start
            data = await response.json()
            return {
                "endpoint": "create_game",
                "status": response.status,
                "duration": duration,
                "game_id": data.get("gameId")
            }
    
    async def make_move(self, session: aiohttp.ClientSession, game_id: str, position: int, player: str) -> Dict:
        """Make a move and measure response time"""
        start = time.time()
        payload = {"position": position, "player": player}
        async with session.post(f"{self.base_url}/games/{game_id}/move", json=payload) as response:
            duration = time.time() - start
            data = await response.json()
            return {
                "endpoint": "make_move",
                "status": response.status,
                "duration": duration,
                "valid": data.get("valid", False)
            }
    
    async def get_game_state(self, session: aiohttp.ClientSession, game_id: str) -> Dict:
        """Get game state and measure response time"""
        start = time.time()
        async with session.get(f"{self.base_url}/games/{game_id}") as response:
            duration = time.time() - start
            data = await response.json()
            return {
                "endpoint": "get_game_state",
                "status": response.status,
                "duration": duration,
                "state": data.get("state")
            }
    
    async def validate_move(self, session: aiohttp.ClientSession, game_id: str, position: int) -> Dict:
        """Validate move without executing and measure response time"""
        start = time.time()
        async with session.get(f"{self.base_url}/games/{game_id}/validate/{position}") as response:
            duration = time.time() - start
            data = await response.json()
            return {
                "endpoint": "validate_move",
                "status": response.status,
                "duration": duration,
                "valid": data.get("valid", False)
            }
    
    async def simulate_full_game(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Simulate a complete game with multiple moves"""
        results = []
        
        # Create game
        create_result = await self.create_game(session)
        results.append(create_result)
        game_id = create_result["game_id"]
        
        # Simulate game moves (X wins diagonal)
        moves = [
            (0, "X"), (1, "O"), (4, "X"), 
            (2, "O"), (8, "X")  # X wins
        ]
        
        for position, player in moves:
            # Validate move
            validate_result = await self.validate_move(session, game_id, position)
            results.append(validate_result)
            
            # Make move
            move_result = await self.make_move(session, game_id, position, player)
            results.append(move_result)
            
            # Get game state
            state_result = await self.get_game_state(session, game_id)
            results.append(state_result)
        
        return results
    
    async def run_concurrent_games(self, num_games: int) -> List[Dict]:
        """Run multiple games concurrently to test load"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.simulate_full_game(session) for _ in range(num_games)]
            results = await asyncio.gather(*tasks)
            return [item for sublist in results for item in sublist]
    
    async def stress_test_endpoint(self, endpoint_name: str, num_requests: int) -> List[Dict]:
        """Stress test a specific endpoint with concurrent requests"""
        async with aiohttp.ClientSession() as session:
            # Create a game first
            create_result = await self.create_game(session)
            game_id = create_result["game_id"]
            
            if endpoint_name == "get_game_state":
                tasks = [self.get_game_state(session, game_id) for _ in range(num_requests)]
            elif endpoint_name == "validate_move":
                tasks = [self.validate_move(session, game_id, 0) for _ in range(num_requests)]
            else:
                tasks = [self.create_game(session) for _ in range(num_requests)]
            
            results = await asyncio.gather(*tasks)
            return results
    
    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze performance test results"""
        endpoint_stats = {}
        
        for result in results:
            endpoint = result["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"durations": [], "statuses": []}
            
            endpoint_stats[endpoint]["durations"].append(result["duration"])
            endpoint_stats[endpoint]["statuses"].append(result["status"])
        
        analysis = {}
        for endpoint, stats in endpoint_stats.items():
            durations = stats["durations"]
            analysis[endpoint] = {
                "total_requests": len(durations),
                "avg_response_time": statistics.mean(durations),
                "min_response_time": min(durations),
                "max_response_time": max(durations),
                "median_response_time": statistics.median(durations),
                "p95_response_time": self.percentile(durations, 95),
                "p99_response_time": self.percentile(durations, 99),
                "success_rate": sum(1 for s in stats["statuses"] if s == 200) / len(stats["statuses"]) * 100
            }
        
        return analysis
    
    @staticmethod
    def percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def run_load_test_suite(self):
        """Execute comprehensive load test suite"""
        print("Starting TicTacToe Load and Performance Tests...\n")
        
        # Test 1: Concurrent games
        print("Test 1: Running 50 concurrent games...")
        results_concurrent = await self.run_concurrent_games(50)
        analysis_concurrent = self.analyze_results(results_concurrent)
        print(json.dumps(analysis_concurrent, indent=2))
        
        # Test 2: Stress test game state endpoint
        print("\nTest 2: Stress testing game state endpoint (1000 requests)...")
        results_state = await self.stress_test_endpoint("get_game_state", 1000)
        analysis_state = self.analyze_results(results_state)
        print(json.dumps(analysis_state, indent=2))
        
        # Test 3: Stress test move validation
        print("\nTest 3: Stress testing move validation (1000 requests)...")
        results_validate = await self.stress_test_endpoint("validate_move", 1000)
        analysis_validate = self.analyze_results(results_validate)
        print(json.dumps(analysis_validate, indent=2))
        
        # Performance assertions
        self.assert_performance_requirements(analysis_concurrent)
        
        print("\n✓ All load and performance tests completed!")
    
    def assert_performance_requirements(self, analysis: Dict):
        """Assert performance requirements are met"""
        for endpoint, stats in analysis.items():
            # Response time should be under 100ms for p95
            assert stats["p95_response_time"] < 0.1, f"{endpoint} p95 response time exceeds 100ms"
            
            # Success rate should be 100%
            assert stats["success_rate"] == 100, f"{endpoint} success rate is below 100%"
            
            print(f"✓ {endpoint}: p95={stats['p95_response_time']*1000:.2f}ms, success_rate={stats['success_rate']}%")


if __name__ == "__main__":
    tester = TicTacToeLoadTester()
    asyncio.run(tester.run_load_test_suite())