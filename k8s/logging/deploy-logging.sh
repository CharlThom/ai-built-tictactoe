#!/bin/bash
set -e

echo "Setting up logging infrastructure for TicTacToe application..."

# Add Grafana Helm repository
echo "Adding Grafana Helm repository..."
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create logging namespace
echo "Creating logging namespace..."
kubectl create namespace logging --dry-run=client -o yaml | kubectl apply -f -

# Install Loki stack (Loki + Promtail + Grafana)
echo "Installing Loki stack..."
helm upgrade --install loki grafana/loki-stack \
  --namespace logging \
  --values loki-stack-values.yaml \
  --wait

# Create ConfigMap for additional log parsing rules
echo "Creating log parsing configuration..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: tictactoe-log-config
  namespace: default
  labels:
    app: tictactoe
data:
  log-format: |
    {
      "level": "info",
      "format": "json",
      "output": "stdout"
    }
EOF

# Create ServiceMonitor for Loki metrics (if Prometheus Operator is installed)
echo "Creating ServiceMonitor for Loki..."
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: loki
  namespace: logging
  labels:
    app: loki
spec:
  selector:
    matchLabels:
      app: loki
  endpoints:
  - port: http-metrics
    interval: 30s
    path: /metrics
EOF

# Create PrometheusRule for log-based alerts
echo "Creating log-based alerts..."
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: tictactoe-log-alerts
  namespace: logging
  labels:
    app: tictactoe
spec:
  groups:
  - name: tictactoe.logs
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        sum(rate({namespace="default", app="tictactoe"} |= "ERROR" [5m])) > 10
      for: 5m
      labels:
        severity: warning
        component: tictactoe
      annotations:
        summary: "High error rate in TicTacToe application"
        description: "TicTacToe application is logging more than 10 errors per second for 5 minutes"
    - alert: ApplicationCrashLoop
      expr: |
        sum(rate({namespace="default", app="tictactoe"} |= "panic" or |= "fatal" [5m])) > 0
      for: 2m
      labels:
        severity: critical
        component: tictactoe
      annotations:
        summary: "TicTacToe application crash detected"
        description: "TicTacToe application is experiencing crashes or fatal errors"
    - alert: NoLogsReceived
      expr: |
        absent_over_time({namespace="default", app="tictactoe"}[10m])
      for: 10m
      labels:
        severity: warning
        component: tictactoe
      annotations:
        summary: "No logs received from TicTacToe application"
        description: "No logs have been received from TicTacToe application for 10 minutes"
EOF

echo ""
echo "Logging infrastructure deployed successfully!"
echo ""
echo "Access Grafana:"
echo "  kubectl port-forward -n logging svc/loki-grafana 3000:80"
echo "  URL: http://localhost:3000"
echo "  Username: admin"
echo "  Password: changeme123"
echo ""
echo "Query logs with LogCLI:"
echo "  kubectl port-forward -n logging svc/loki 3100:3100"
echo "  logcli query '{namespace=\"default\", app=\"tictactoe\"}' --addr=http://localhost:3100"
echo ""
echo "View logs in Grafana Explore:"
echo "  Use query: {namespace=\"default\", app=\"tictactoe\"}"
echo ""