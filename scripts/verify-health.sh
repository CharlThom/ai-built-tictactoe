#!/bin/bash
set -e

# Health Verification Script for TicTacToe Production
# Performs continuous health monitoring and validation

NAMESPACE="tictactoe-prod"
APP_NAME="tictactoe"
CHECK_INTERVAL=5
MAX_CHECKS=12

echo "=== TicTacToe Health Verification ==="

# Function to check pod health
check_pod_health() {
    local ready_count=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o json | \
        jq '[.items[] | select(.status.conditions[] | select(.type=="Ready" and .status=="True"))] | length')
    local total_count=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME --no-headers 2>/dev/null | wc -l)
    echo "$ready_count/$total_count"
}

# Function to test application endpoint
test_app_endpoint() {
    local pod_name=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -z "$pod_name" ]; then
        echo "ERROR"
        return 1
    fi
    
    local response=$(kubectl exec -n $NAMESPACE $pod_name -- wget -q -O- --timeout=5 http://localhost:8080/health 2>/dev/null || echo "FAILED")
    echo "$response"
}

# Function to check metrics endpoint
check_metrics() {
    local pod_name=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -z "$pod_name" ]; then
        return 1
    fi
    
    kubectl exec -n $NAMESPACE $pod_name -- wget -q -O- --timeout=5 http://localhost:8080/metrics 2>/dev/null | head -n 5
}

# Function to check resource usage
check_resources() {
    kubectl top pods -n $NAMESPACE -l app=$APP_NAME 2>/dev/null || echo "Metrics server not available"
}

echo ""
echo "Starting health checks (will run $MAX_CHECKS times with ${CHECK_INTERVAL}s interval)..."
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for i in $(seq 1 $MAX_CHECKS); do
    echo "[Check $i/$MAX_CHECKS] $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Check deployment status
    DEPLOYMENT_STATUS=$(kubectl get deployment $APP_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null)
    echo "  Deployment Available: $DEPLOYMENT_STATUS"
    
    # Check pod health
    POD_HEALTH=$(check_pod_health)
    echo "  Ready Pods: $POD_HEALTH"
    
    # Test health endpoint
    HEALTH_RESPONSE=$(test_app_endpoint)
    if [[ $HEALTH_RESPONSE == *"healthy"* ]] || [[ $HEALTH_RESPONSE == *"ok"* ]] || [[ $HEALTH_RESPONSE == *"status"* ]]; then
        echo "  Health Endpoint: ✓ OK"
        ((SUCCESS_COUNT++))
    else
        echo "  Health Endpoint: ✗ FAILED ($HEALTH_RESPONSE)"
        ((FAIL_COUNT++))
    fi
    
    # Check service endpoints
    ENDPOINT_COUNT=$(kubectl get endpoints $APP_NAME -n $NAMESPACE -o json 2>/dev/null | jq '.subsets[0].addresses | length' 2>/dev/null || echo 0)
    echo "  Service Endpoints: $ENDPOINT_COUNT"
    
    # Check HPA
    HPA_STATUS=$(kubectl get hpa -n $NAMESPACE -o jsonpath='{.items[0].status.currentReplicas}' 2>/dev/null || echo "N/A")
    echo "  HPA Current Replicas: $HPA_STATUS"
    
    echo ""
    
    if [ $i -lt $MAX_CHECKS ]; then
        sleep $CHECK_INTERVAL
    fi
done

echo "=== Health Check Summary ==="
echo "Successful checks: $SUCCESS_COUNT/$MAX_CHECKS"
echo "Failed checks: $FAIL_COUNT/$MAX_CHECKS"
echo ""

# Final detailed status
echo "=== Current Status ==="
echo "Pods:"
kubectl get pods -n $NAMESPACE -l app=$APP_NAME
echo ""
echo "Deployment:"
kubectl get deployment $APP_NAME -n $NAMESPACE
echo ""
echo "Service:"
kubectl get svc $APP_NAME -n $NAMESPACE
echo ""
echo "HPA:"
kubectl get hpa -n $NAMESPACE
echo ""

# Check metrics endpoint
echo "Metrics Sample:"
check_metrics | head -n 10
echo ""

# Resource usage
echo "Resource Usage:"
check_resources
echo ""

# Determine overall health
if [ $SUCCESS_COUNT -ge $((MAX_CHECKS * 80 / 100)) ]; then
    echo "✓ Overall Health: HEALTHY (${SUCCESS_COUNT}/${MAX_CHECKS} checks passed)"
    exit 0
else
    echo "✗ Overall Health: UNHEALTHY (${SUCCESS_COUNT}/${MAX_CHECKS} checks passed)"
    echo ""
    echo "Recent pod events:"
    kubectl get events -n $NAMESPACE --field-selector involvedObject.kind=Pod --sort-by='.lastTimestamp' | tail -n 10
    exit 1
fi
