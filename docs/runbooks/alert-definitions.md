# TicTacToe Alert Definitions

This document defines all alerts configured for the TicTacToe application, their thresholds, severity levels, and expected response times.

## Alert Severity Levels

| Severity | Response Time | Description | Notification |
|----------|---------------|-------------|-------------|
| **P1 (Critical)** | 15 minutes | Service down, major functionality broken | PagerDuty + Phone + Slack |
| **P2 (High)** | 30 minutes | Degraded performance, partial outage | PagerDuty + Slack |
| **P3 (Medium)** | 2 hours | Minor issues, potential problems | Slack only |
| **P4 (Low)** | Next business day | Informational, trending issues | Email |

---

## Application Alerts

### TicTacToeServiceDown
**Severity**: P1 (Critical)  
**Condition**: No healthy pods available for 2 minutes  
**PromQL**:
promql
sum(up{job="tictactoe", namespace="tictactoe"}) == 0

**Threshold**: 0 healthy instances for 2m  
**Action**: Follow "Service Unavailable / All Pods Down" runbook  
**Escalation**: Immediate to L2 if not resolved in 15 minutes

---

### TicTacToeHighErrorRate
**Severity**: P1 (Critical)  
**Condition**: Error rate > 5% for 5 minutes  
**PromQL**:
promql
(sum(rate(http_requests_total{namespace="tictactoe",status=~"5.."}[5m])) / 
sum(rate(http_requests_total{namespace="tictactoe"}[5m]))) * 100 > 5

**Threshold**: >5% error rate for 5m  
**Action**: Follow "High Error Rate" runbook  
**Escalation**: Escalate to development team if application bug suspected

---

### TicTacToeHighLatency
**Severity**: P2 (High)  
**Condition**: P95 latency > 1000ms for 5 minutes  
**PromQL**:
promql
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket{namespace="tictactoe"}[5m])) by (le)
) > 1

**Threshold**: P95 > 1s for 5m  
**Action**: Check CPU/memory usage, database performance, and pod count  
**Escalation**: Escalate if latency continues to increase

---

### TicTacToePodCrashLooping
**Severity**: P2 (High)  
**Condition**: Pod restarted more than 3 times in 10 minutes  
**PromQL**:
promql
rate(kube_pod_container_status_restarts_total{namespace="tictactoe"}[10m]) > 0.3

**Threshold**: >3 restarts in 10m  
**Action**: Follow "Pod CrashLoopBackOff" runbook  
**Escalation**: Check if bad deployment, consider rollback

---

### TicTacToePodHighCPU
**Severity**: P2 (High)  
**Condition**: CPU usage > 80% for 10 minutes  
**PromQL**:
promql
sum(rate(container_cpu_usage_seconds_total{namespace="tictactoe",pod=~"tictactoe-.*"}[5m])) by (pod) /
sum(container_spec_cpu_quota{namespace="tictactoe",pod=~"tictactoe-.*"}/container_spec_cpu_period{namespace="tictactoe",pod=~"tictactoe-.*"}) by (pod) * 100 > 80

**Threshold**: >80% CPU for 10m  
**Action**: Verify HPA is scaling, check for inefficient code  
**Escalation**: Consider increasing CPU limits or optimizing code

---

### TicTacToePodHighMemory
**Severity**: P2 (High)  
**Condition**: Memory usage > 85% of limit for 5 minutes  
**PromQL**:
promql
sum(container_memory_usage_bytes{namespace="tictactoe",pod=~"tictactoe-.*"}) by (pod) /
sum(container_spec_memory_limit_bytes{namespace="tictactoe",pod=~"tictactoe-.*"}) by (pod) * 100 > 85

**Threshold**: >85% memory for 5m  
**Action**: Check for memory leaks, consider increasing limits  
**Escalation**: Immediate if pods are being OOMKilled

---

### TicTacToePodOOMKilled
**Severity**: P1 (Critical)  
**Condition**: Pod killed due to out of memory  
**PromQL**:
promql
sum(increase(kube_pod_container_status_terminated_reason{namespace="tictactoe",reason="OOMKilled"}[5m])) > 0

**Threshold**: Any OOMKilled event  
**Action**: Immediately increase memory limits, investigate memory leak  
**Escalation**: Engage development team for memory profiling

---

### TicTacToeDBConnectionFailure
**Severity**: P1 (Critical)  
**Condition**: Database connection errors > 10 in 5 minutes  
**PromQL**:
promql
sum(increase(database_connection_errors_total{namespace="tictactoe"}[5m])) > 10

**Threshold**: >10 connection errors in 5m  
**Action**: Follow "Database Connection Failures" runbook  
**Escalation**: Engage database team immediately

---

## Infrastructure Alerts

### TicTacToeHPAMaxedOut
**Severity**: P3 (Medium)  
**Condition**: HPA at maximum replica count for 15 minutes  
**PromQL**:
promql
kube_horizontalpodautoscaler_status_current_replicas{namespace="tictactoe"} ==
kube_horizontalpodautoscaler_spec_max_replicas{namespace="tictactoe"}

**Threshold**: At max replicas for 15m  
**Action**: Review if max replicas should be increased  
**Escalation**: Consider capacity planning

---

### TicTacToeHPAScalingDisabled
**Severity**: P3 (Medium)  
**Condition**: HPA unable to scale (missing metrics)  
**PromQL**:
promql
kube_horizontalpodautoscaler_status_condition{namespace="tictactoe",condition="ScalingActive",status="false"} == 1

**Threshold**: Scaling disabled for 10m  
**Action**: Check metrics-server and HPA configuration  
**Escalation**: May impact ability to handle traffic spikes

---

### TicTacToeLowPodCount
**Severity**: P2 (High)  
**Condition**: Less than 2 pods running for 5 minutes  
**PromQL**:
promql
sum(kube_pod_status_phase{namespace="tictactoe",phase="Running"}) < 2

**Threshold**: <2 running pods for 5m  
**Action**: Check deployment status, investigate why pods aren't running  
**Escalation**: Risk of service disruption

---

### TicTacToeIngressDown
**Severity**: P1 (Critical)  
**Condition**: Ingress returning 503 errors  
**PromQL**:
promql
sum(rate(nginx_ingress_controller_requests{namespace="tictactoe",status="503"}[5m])) > 10

**Threshold**: >10 req/s of 503 errors for 5m  
**Action**: Check ingress controller, backend service, and pod health  
**Escalation**: Immediate if complete outage

---

### TicTacToeCertExpiring
**Severity**: P3 (Medium)  
**Condition**: SSL certificate expires in less than 30 days  
**PromQL**:
promql
(certmanager_certificate_expiration_timestamp_seconds{namespace="tictactoe"} - time()) / 86400 < 30

**Threshold**: <30 days until expiration  
**Action**: Verify cert-manager is working, force renewal if needed  
**Escalation**: P2 if <7 days, P1 if <2 days

---

## Resource Alerts

### TicTacToeNamespaceQuotaExceeded
**Severity**: P2 (High)  
**Condition**: Namespace resource quota exceeded  
**PromQL**:
promql
kube_resourcequota{namespace="tictactoe",type="used"} / 
kube_resourcequota{namespace="tictactoe",type="hard"} > 0.9

**Threshold**: >90% of quota used  
**Action**: Review resource usage, request quota increase if needed  
**Escalation**: May prevent scaling or new deployments

---

### TicTacToePVCAlmostFull
**Severity**: P3 (Medium)  
**Condition**: Persistent volume claim >85% full  
**PromQL**:
promql
kubelet_volume_stats_used_bytes{namespace="tictactoe"} / 
kubelet_volume_stats_capacity_bytes{namespace="tictactoe"} * 100 > 85

**Threshold**: >85% disk usage  
**Action**: Clean up old data or expand volume  
**Escalation**: P2 if >95%, P1 if full

---

## Monitoring System Alerts

### TicTacToeMetricsDown
**Severity**: P3 (Medium)  
**Condition**: Prometheus unable to scrape metrics for 5 minutes  
**PromQL**:
promql
up{job="tictactoe",namespace="tictactoe"} == 0

**Threshold**: Scrape failing for 5m  
**Action**: Check ServiceMonitor, pod metrics endpoint, network policies  
**Escalation**: Impacts observability

---

### TicTacToeNoMetricsData
**Severity**: P4 (Low)  
**Condition**: No metrics data received for 10 minutes  
**PromQL**:
promql
absent(up{job="tictactoe",namespace="tictactoe"})

**Threshold**: No data for 10m  
**Action**: Verify Prometheus configuration and ServiceMonitor  
**Escalation**: Check if monitoring stack is healthy

---

## Alert Configuration Example

yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: tictactoe-alerts
  namespace: tictactoe
spec:
  groups:
  - name: tictactoe.rules
    interval: 30s
    rules:
    - alert: TicTacToeServiceDown
      expr: sum(up{job="tictactoe", namespace="tictactoe"}) == 0
      for: 2m
      labels:
        severity: critical
        team: devops
      annotations:
        summary: "TicTacToe service is completely down"
        description: "No healthy pods available for TicTacToe service"
        runbook_url: "https://runbooks.company.com/tictactoe#service-down"


## Alert Testing

Regularly test alerts to ensure they fire correctly:

bash
# Test by scaling down to 0
kubectl scale deployment tictactoe -n tictactoe --replicas=0

# Test CPU alert by generating load
kubectl run -it --rm load-generator --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://tictactoe-service.tictactoe.svc.cluster.local; done"

# Verify alert in Prometheus
curl 'http://prometheus:9090/api/v1/alerts'


## Alert Tuning

Review and adjust alert thresholds quarterly based on:
- False positive rate
- Actual incident patterns
- Application performance baselines
- Business requirements

## Notification Channels

- **PagerDuty**: P1 and P2 alerts
- **Slack #tictactoe-alerts**: All alerts
- **Email**: P3 and P4 alerts
- **Status Page**: Automated updates for P1 alerts