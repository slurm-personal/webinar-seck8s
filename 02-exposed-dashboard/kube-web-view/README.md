# Kubernetes Dashboard

Insecure installation instructions for [KubeWebView](https://codeberg.org/hjacobs/kube-web-view/) in the demo cluster:

```
NS=exposed-dashboard
k create ns $NS

# Install an unprotected dashboard:
k -n $NS apply -f ./deploy

# Expose the dashboard via ingress
k -n $NS apply -f ./deploy-ingress
```


Note: there also exists a Helm package [decayofmind/kube-web-view](https://artifacthub.io/packages/helm/decayofmind/kube-web-view?modal=install) which can integrate with LDAP and OAuth.

