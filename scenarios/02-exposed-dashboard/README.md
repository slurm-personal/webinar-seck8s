# Profit the K8s Dashboard



can see deployments in all ns


---
```
# install via helm: https://artifacthub.io/packages/helm/decayofmind/kube-web-view?modal=install
$ helm repo add decayofmind https://decayofmind.github.io/charts/
$ k create ns web-dashboard-ingress
$ helm -n web-dashboard-ingress install my-kube-web-view decayofmind/kube-web-view --version 0.0.4
```
---


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
    LDAP auth disabled: `nginx-ldapauth-proxy.enabled	bool	false`





