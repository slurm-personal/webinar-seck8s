# Profit the K8s Dashboard

Exposed and unprotected Kubernetes dashboard is one of the most common attack entrypoints on K8s clusters.


## Attack on ${NAME} June 2021

### Timeline:
- July 21: user's public report: https://habr.com/ru/post/568842/
- July 22: team's tech report: https://habr.com/ru/post/569176/

### Description:
- ingress.enabled=true (NOT default)
- Mistake in ingress configuration => Kubernetes WebView dashboard is available via several public DNS names
- The dashboard is unprotected (no auth)
- read-only access (cannot create new K8s object)
- all K8s namespaces
- secrets are hidden by the dashboard (default behaviour), howver the team stored some secrets in config maps
- container logs are accessible, which is NOT default behaviour (`--show-container-logs`)


Note: there exist a Helm package [decayofmind/kube-web-view](https://artifacthub.io/packages/helm/decayofmind/kube-web-view?modal=install) which can integrate with LDAP and OAuth.




<!-- TODO: develop фронт и бэк на django -->

Default security config:
    https://codeberg.org/hjacobs/kube-web-view/src/commit/bc5231296/deploy/deployment.yaml#L24-L29
    logs:
        http://localhost:8080/clusters/local/namespaces/mock-payload/pods
        disabled by default, but enabled in FBK (service 'ganimed', 'headquarters')
        - ganimed:
            на бэке не был отключен дебаг
            kube-web-viiew: can read logs
    secrets:
        avail but hidden by default
        http://localhost:8080/clusters/local/namespaces/mock-payload/secrets/db-secret
        show Secrets (hidden)
        show secrets in ConfigMap

however, some secrets might be stored in ConfigMaps
    http://localhost:8080/clusters/local/namespaces/mock-payload/configmaps

RBAC:
    - read-only (both in github manifests and helm)


Ingress:
```
--- a/kube-web-view/templates/ingress.yaml
+++ b/kube-web-view/templates/ingress.yaml
@@ -27,7 +27,7 @@ spec:
```
    most likely, used this template: https://artifacthub.io/packages/helm/decayofmind/kube-web-view?modal=template&template=ingress.yaml
    LDAP auth disabled by default: `nginx-ldapauth-proxy.enabled	bool	false`

Errors:
    - Maybe they had LDAP or OAuth, but ingress made exposed/bypassed it
    - understand your access control: it had admin privs
    - Secrets in ConfigMaps (even though...)
    - --show-container-logs: ehh

