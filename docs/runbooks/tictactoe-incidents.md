# TicTacToe Production Runbook

## On-Call Procedures

### Escalation Path
1. **L1**: On-call DevOps Engineer (Primary)
2. **L2**: Senior DevOps Engineer
3. **L3**: Platform Lead + Development Team Lead

### On-Call Responsibilities
- Respond to alerts within 15 minutes
- Acknowledge incidents in PagerDuty/alerting system
- Follow runbook procedures
- Document all actions taken
- Create post-incident reports for P1/P2 incidents

### Communication Channels
- **Slack**: #tictactoe-incidents
- **PagerDuty**: TicTacToe service
- **Status Page**: status.tictactoe.com

---

## Common Incidents

### 1. High Pod CPU Usage (>80%)

**Alert**: `TicTacToePodHighCPU`

**Symptoms**:
- Slow response times
- Increased latency
- HPA scaling up pods

**Investigation**:
bash
# Check current CPU usage
kubectl top pods -n tictactoe -l app=tictactoe

# Check HPA status
kubectl get hpa -n tictactoe

# View pod logs for errors
kubectl logs -n tictactoe -l app=tictactoe --tail=100

# Check Prometheus metrics
curl http://prometheus:9090/api/v1/query?query=rate(container_cpu_usage_seconds_total{namespace="tictactoe"}[5m])


**Resolution**:
1. Verify HPA is scaling (should auto-resolve if configured correctly)
2. If HPA maxed out, manually scale:
   bash
   kubectl scale deployment tictactoe -n tictactoe --replicas=10
   
3. Check for inefficient code or memory leaks in recent deployments
4. Consider increasing CPU limits if sustained high usage

**Prevention**:
- Review and optimize application code
- Adjust HPA thresholds
- Increase resource limits in deployment manifest

---

### 2. Pod CrashLoopBackOff

**Alert**: `TicTacToePodCrashLooping`

**Symptoms**:
- Pods continuously restarting
- Service degradation or unavailability
- Error logs in pod events

**Investigation**:
bash
# Check pod status
kubectl get pods -n tictactoe

# Describe failing pod
kubectl describe pod <pod-name> -n tictactoe

# Check logs from crashed container
kubectl logs <pod-name> -n tictactoe --previous

# Check events
kubectl get events -n tictactoe --sort-by='.lastTimestamp'


**Resolution**:
1. **Config issue**: Verify ConfigMaps and Secrets are present
   bash
   kubectl get configmap,secret -n tictactoe
   
2. **Database connection**: Check database connectivity and credentials
3. **Resource limits**: Increase memory/CPU if OOMKilled
4. **Bad deployment**: Rollback to previous version
   bash
   kubectl rollout undo deployment/tictactoe -n tictactoe
   kubectl rollout status deployment/tictactoe -n tictactoe
   

**Prevention**:
- Implement readiness/liveness probes correctly
- Test deployments in staging first
- Use init containers for dependency checks

---

### 3. High Error Rate (5xx Responses)

**Alert**: `TicTacToeHighErrorRate`

**Symptoms**:
- Increased 500/502/503 errors
- User complaints
- Degraded service availability

**Investigation**:
bash
# Check application logs
kubectl logs -n tictactoe -l app=tictactoe --tail=200 | grep -i error

# Check ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=100

# Query Prometheus for error rate
curl 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5..",namespace="tictactoe"}[5m])'

# Check service endpoints
kubectl get endpoints -n tictactoe


**Resolution**:
1. **Backend unavailable**: Check if pods are ready
   bash
   kubectl get pods -n tictactoe -o wide
   
2. **Database issues**: Verify database connectivity
   bash
   kubectl exec -it <pod-name> -n tictactoe -- nc -zv <db-host> <db-port>
   
3. **Resource exhaustion**: Check if pods are OOMing or CPU throttled
4. **Recent deployment**: Rollback if errors started after deployment
5. **External dependency**: Check status of external APIs/services

**Prevention**:
- Implement circuit breakers
- Add retry logic with exponential backoff
- Monitor external dependencies
- Implement proper error handling

---

### 4. Service Unavailable / All Pods Down

**Alert**: `TicTacToeServiceDown`

**Symptoms**:
- Complete service outage
- No healthy pods
- 503 errors from ingress

**Investigation**:
bash
# Check deployment status
kubectl get deployment,pods -n tictactoe

# Check replica set
kubectl get rs -n tictactoe

# Check node status
kubectl get nodes

# Check namespace events
kubectl get events -n tictactoe --sort-by='.lastTimestamp' | tail -20


**Resolution**:
1. **Image pull failure**: Verify image exists and credentials are valid
   bash
   kubectl describe pod <pod-name> -n tictactoe | grep -A 5 "Events:"
   
2. **Node issues**: Check if nodes are ready and have capacity
3. **Resource quota**: Check namespace resource quotas
   bash
   kubectl describe resourcequota -n tictactoe
   
4. **Manual scale**: Force recreation of pods
   bash
   kubectl rollout restart deployment/tictactoe -n tictactoe
   
5. **Emergency**: Deploy previous known-good version

**Prevention**:
- Use multiple replicas (minimum 3)
- Implement pod disruption budgets
- Use pod anti-affinity for node distribution
- Regular disaster recovery drills

---

### 5. High Memory Usage / OOMKilled

**Alert**: `TicTacToePodOOMKilled`

**Symptoms**:
- Pods being killed by OOM
- Frequent restarts
- Memory usage at limit

**Investigation**:
bash
# Check memory usage
kubectl top pods -n tictactoe

# Check pod events for OOMKilled
kubectl describe pod <pod-name> -n tictactoe | grep -i oom

# Check resource limits
kubectl get deployment tictactoe -n tictactoe -o yaml | grep -A 5 resources

# Check for memory leaks in metrics
curl 'http://prometheus:9090/api/v1/query?query=container_memory_usage_bytes{namespace="tictactoe"}'


**Resolution**:
1. **Immediate**: Increase memory limits
   bash
   kubectl set resources deployment tictactoe -n tictactoe --limits=memory=1Gi
   
2. **Investigate**: Check for memory leaks in application
3. **Optimize**: Review application memory usage patterns
4. **Scale**: Increase replicas to distribute load

**Prevention**:
- Profile application memory usage
- Implement proper garbage collection
- Set appropriate memory limits with headroom
- Monitor memory trends over time

---

### 6. Ingress/SSL Certificate Issues

**Alert**: `TicTacToeIngressDown` or `TicTacToeCertExpiring`

**Symptoms**:
- SSL certificate errors
- Unable to reach service via domain
- Certificate expiration warnings

**Investigation**:
bash
# Check ingress status
kubectl get ingress -n tictactoe
kubectl describe ingress tictactoe -n tictactoe

# Check certificate
kubectl get certificate -n tictactoe
kubectl describe certificate tictactoe-tls -n tictactoe

# Test SSL
openssl s_client -connect tictactoe.example.com:443 -servername tictactoe.example.com

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager


**Resolution**:
1. **Certificate expired**: Force renewal
   bash
   kubectl delete certificate tictactoe-tls -n tictactoe
   # cert-manager will recreate automatically
   
2. **Ingress misconfigured**: Verify ingress annotations and rules
3. **DNS issues**: Verify DNS records point to ingress IP
   bash
   nslookup tictactoe.example.com
   kubectl get ingress -n tictactoe -o wide
   
4. **cert-manager issues**: Restart cert-manager if needed

**Prevention**:
- Monitor certificate expiration (alert 30 days before)
- Use automated certificate renewal (cert-manager)
- Test certificate renewal process regularly

---

### 7. Database Connection Failures

**Alert**: `TicTacToeDBConnectionFailure`

**Symptoms**:
- Application errors about database connectivity
- Timeouts on database operations
- Connection pool exhaustion

**Investigation**:
bash
# Check application logs
kubectl logs -n tictactoe -l app=tictactoe | grep -i "database\|connection"

# Test database connectivity from pod
kubectl exec -it <pod-name> -n tictactoe -- sh
# Inside pod:
telnet <db-host> <db-port>

# Check database credentials secret
kubectl get secret tictactoe-db-secret -n tictactoe -o yaml

# Check network policies
kubectl get networkpolicy -n tictactoe


**Resolution**:
1. **Database down**: Check database service status
2. **Credentials rotated**: Update secret with new credentials
   bash
   kubectl create secret generic tictactoe-db-secret \
     --from-literal=username=<user> \
     --from-literal=password=<pass> \
     --dry-run=client -o yaml | kubectl apply -f -
   kubectl rollout restart deployment/tictactoe -n tictactoe
   
3. **Network policy**: Verify network policies allow database traffic
4. **Connection pool**: Restart pods to reset connection pools

**Prevention**:
- Implement connection retry logic
- Monitor database health separately
- Use connection pooling with proper limits
- Set up database read replicas for redundancy

---

## Post-Incident Procedures

1. **Document the incident**:
   - Timeline of events
   - Actions taken
   - Root cause
   - Resolution

2. **Update status page**: Mark incident as resolved

3. **Create post-mortem** (for P1/P2):
   - What happened
   - Impact assessment
   - Root cause analysis
   - Action items to prevent recurrence

4. **Update runbook**: Add new learnings

5. **Schedule post-mortem review**: Within 48 hours for P1, 1 week for P2

---

## Useful Commands Reference

bash
# Quick health check
kubectl get pods,svc,ingress -n tictactoe

# Watch pod status
kubectl get pods -n tictactoe -w

# Get all logs from deployment
kubectl logs -n tictactoe -l app=tictactoe --all-containers=true

# Port forward to pod for debugging
kubectl port-forward -n tictactoe <pod-name> 8080:8080

# Execute command in pod
kubectl exec -it <pod-name> -n tictactoe -- /bin/sh

# Check resource usage
kubectl top nodes
kubectl top pods -n tictactoe

# View deployment history
kubectl rollout history deployment/tictactoe -n tictactoe

# Emergency rollback
kubectl rollout undo deployment/tictactoe -n tictactoe

# Scale deployment
kubectl scale deployment tictactoe -n tictactoe --replicas=5


## Emergency Contacts

- **DevOps Team Lead**: +1-XXX-XXX-XXXX
- **Platform Engineering**: platform-oncall@company.com
- **Development Team Lead**: +1-XXX-XXX-XXXX
- **Cloud Provider Support**: [Support Portal Link]

## Additional Resources

- Grafana Dashboards: https://grafana.company.com/d/tictactoe
- Prometheus: https://prometheus.company.com
- Kubernetes Dashboard: https://k8s-dashboard.company.com
- Application Logs: https://logs.company.com/tictactoe
- Incident Management: https://pagerduty.com/incidents