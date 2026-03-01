#!/bin/bash
set -e

# Production Deployment Script for TicTacToe
# This script deploys the application to production Kubernetes cluster and verifies health

NAMESPACE="tictactoe-prod"
APP_NAME="tictactoe"
DEPLOYMENT_TIMEOUT="300s"

echo "=== Starting TicTacToe Production Deployment ==="

# Verify kubectl context
CURRENT_CONTEXT=$(kubectl config current-context)
echo "Current context: $CURRENT_CONTEXT"
read -p "Deploy to this cluster? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 1
fi

# Create namespace if it doesn't exist
echo "Ensuring namespace exists..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
kubectl apply -f k8s/service.yaml -n $NAMESPACE
kubectl apply -f k8s/hpa.yaml -n $NAMESPACE
kubectl apply -f k8s/ingress.yaml -n $NAMESPACE
kubectl apply -f k8s/servicemonitor.yaml -n $NAMESPACE

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/$APP_NAME -n $NAMESPACE --timeout=$DEPLOYMENT_TIMEOUT

# Verify pods are running
echo "Verifying pods..."
POD_COUNT=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME --field-selector=status.phase=Running --no-headers | wc -l)
if [ $POD_COUNT -eq 0 ]; then
    echo "ERROR: No running pods found"
    kubectl get pods -n $NAMESPACE -l app=$APP_NAME
    exit 1
fi
echo "Running pods: $POD_COUNT"

# Check pod health
echo "Checking pod health status..."
kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o json | jq -r '.items[] | "\(.metadata.name): Ready=\(.status.conditions[] | select(.type=="Ready") | .status)"'

# Verify readiness probes
echo "Verifying readiness probes..."
READY_PODS=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o json | jq '[.items[] | select(.status.conditions[] | select(.type=="Ready" and .status=="True"))] | length')
echo "Ready pods: $READY_PODS/$POD_COUNT"

if [ $READY_PODS -eq 0 ]; then
    echo "ERROR: No pods are ready"
    kubectl describe pods -n $NAMESPACE -l app=$APP_NAME
    exit 1
fi

# Test health endpoint
echo "Testing health endpoints..."
POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=$APP_NAME -o jsonpath='{.items[0].metadata.name}')
HEALTH_CHECK=$(kubectl exec -n $NAMESPACE $POD_NAME -- wget -q -O- http://localhost:8080/health 2>/dev/null || echo "FAILED")
if [[ $HEALTH_CHECK == *"healthy"* ]] || [[ $HEALTH_CHECK == *"ok"* ]]; then
    echo "✓ Health check passed: $HEALTH_CHECK"
else
    echo "⚠ Health check response: $HEALTH_CHECK"
fi

# Verify service endpoints
echo "Verifying service endpoints..."
kubectl get endpoints $APP_NAME -n $NAMESPACE

# Check HPA status
echo "Checking HPA status..."
kubectl get hpa -n $NAMESPACE

# Verify Prometheus ServiceMonitor
echo "Verifying ServiceMonitor..."
kubectl get servicemonitor -n $NAMESPACE 2>/dev/null || echo "ServiceMonitor CRD not found (ensure Prometheus Operator is installed)"

# Display ingress information
echo "Ingress information:"
kubectl get ingress -n $NAMESPACE

echo ""
echo "=== Deployment Summary ==="
echo "Namespace: $NAMESPACE"
echo "Deployment: $(kubectl get deployment $APP_NAME -n $NAMESPACE -o jsonpath='{.status.availableReplicas}')/$(kubectl get deployment $APP_NAME -n $NAMESPACE -o jsonpath='{.spec.replicas}') replicas available"
echo "Service: $(kubectl get svc $APP_NAME -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')"
echo "Ingress: $(kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo 'Not configured')"
echo ""
echo "✓ Production deployment completed successfully!"
echo ""
echo "Useful commands:"
echo "  Watch pods: kubectl get pods -n $NAMESPACE -l app=$APP_NAME -w"
echo "  View logs: kubectl logs -n $NAMESPACE -l app=$APP_NAME --tail=100 -f"
echo "  Scale: kubectl scale deployment/$APP_NAME -n $NAMESPACE --replicas=N"
