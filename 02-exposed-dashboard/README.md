# Profit the K8s Dashboard
Exposed and unprotected Kubernetes dashboard is one of the most common attack entrypoints on K8s clusters.

## Steps to reproduce:
1. install the kubernetes dashboard [./kube-web-view](kube-web-view) in an insecure way
2. install the mock email-sending service [./mock-email-service](mock-email-service)
3. explore the dashboard:
   - [pods](http://rus-vote.seck8s.slurm.io/clusters/local/namespaces/mock-payload/pods)
   - [nodes](http://rus-vote.seck8s.slurm.io/clusters/local/nodes)
   - [secrets](http://rus-vote.seck8s.slurm.io/clusters/local/namespaces/mock-payload/secrets)
   - [config maps](http://rus-vote.seck8s.slurm.io/clusters/local/namespaces/mock-payload/configmaps)


# Attacks

## Attack on ${NAME}, June 2021

### Timeline:
- July 21: user's public report: https://habr.com/ru/post/568842/
- July 22: tech team's report: https://habr.com/ru/post/569176/

### Description:
- ingress.enabled=true (NOT default)
- Mistake in ingress configuration => Kubernetes WebView dashboard is available via several public DNS names
- The dashboard is unprotected (no auth)
- read-only access (cannot create new K8s object)
- access to all K8s namespaces
- [secrets were hidden by default](https://codeberg.org/hjacobs/kube-web-view/src/commit/bc5231296/deploy/deployment.yaml#L27-L29) in the dashboard (`--show-secrets`), however the team stored some secrets in config maps (!)
- [container logs were accessible](https://codeberg.org/hjacobs/kube-web-view/src/commit/bc5231296/deploy/deployment.yaml#L24-L26), which is NOT default (`--show-container-logs`), in addition, the DEBUG mode was enabled on the production servers


### Notes
- other secrets like DB credentials might have been leaked to be used for future attacks (after the attack discovery the team claimed to have all secrets rotated)


## Attack on Tesla, 2018

- Also, accidentally exposed K8s dashboard
- then, AWS creds stolen
- mining Monero on their K8s cluster
- carefully hiding presence of mining pods (CPU utilisation throttling, using non-default mining pools, hiding IP via CloudFare CDN)


## Attack(s): reports by Azure Security Center, 2019-2021

[2019](https://azure.microsoft.com/en-us/blog/detect-largescale-cryptocurrency-mining-attack-against-kubernetes-clusters/), [June 2020](https://www.microsoft.com/security/blog/2020/06/10/misconfigured-kubeflow-workloads-are-a-security-risk/), [May 2021](https://techcommunity.microsoft.com/t5/azure-security-center/new-large-scale-campaign-targets-kubeflow/ba-p/2425750)

- using Monero docker image from public dockerhub
- mining pods running as dashboard’s service account, which means they were deployed via a K8s dashboard
- 2020 & 2021: attacking Kubeflow's pipelines to deploy mining images
