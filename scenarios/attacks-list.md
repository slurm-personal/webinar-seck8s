


# Cryptojacking

https://cloud.redhat.com/blog/cryptojacking-attacks-in-kubernetes-how-to-stop-them
TODO: picture here with matrix:
- Initial Access
    - Compromised images in registry
- Exposed Dashboard
    - Execution
    - New container
- Persistence
    - Backdoor container
- Discovery
    - Access Kubernetes Dashboard
- Lateral Movement
    - Container service account
    - Access Kubernetes Dashboard
- Impact
    - Resource Hijacking



## Mitigation
- Ensure images are secure
- Avoid risks associated with the Kubernetes Dashboard risks
- Leverage Kubernetes Role-based Access Control (RBAC) to ensure least privilege for service accounts



## Case: Tesla 2018

https://redlock.io/blog/cryptojacking-tesla
- exposed K8s console without password
- one of the pods contained credentials to S3 with sensitive info



## April 2020: Azure Security finds a large-scale cryptocurrency mining attack against Kubernetes clusters

https://azure.microsoft.com/en-us/blog/detect-largescale-cryptocurrency-mining-attack-against-kubernetes-clusters/

Profit the dashboard:

- Exposed dashboard to internet
[MAYBE_TO_SHOW_THIS_ONE] - The attacker gained access to a single container in the cluster and used the internal networking of the cluster for accessing the dashboard (which is possible by the default behavior of Kubernetes).
- Legitimate browsing to the dashboard using cloud or cluster credentials.



## June 2020, June 2021: Azure Security: Misconfigured Kubeflow

1) https://www.microsoft.com/security/blog/2020/06/10/misconfigured-kubeflow-workloads-are-a-security-risk/
2) https://techcommunity.microsoft.com/t5/azure-security-center/new-large-scale-campaign-targets-kubeflow/ba-p/2425750

Again, dashboard
backdoor container (legitime but running malicious code inside)


## TeamTNT


## FBK
- Mistake in an Ingress yaml (empty host)
- (also) Sensitive info stored in secrets
