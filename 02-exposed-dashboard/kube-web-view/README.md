# Kubernetes Dashboard

Insecure installation instructions for [KubeWebView](https://codeberg.org/hjacobs/kube-web-view/) in the demo cluster:

```sh
NS=exposed-dashboard
k create ns $NS

# Install an unprotected dashboard:
k -n $NS apply -f ./deploy

# Expose the dashboard via ingress
k -n $NS apply -f ./deploy-ingress
```

Check status:
```sh
k -n $NS get all,ingress
```

Uninstall:
```sh
k delete ns $NS
```


> Note: Alternatively, one can install the dashboad using the Helm package [decayofmind/kube-web-view](https://artifacthub.io/packages/helm/decayofmind/kube-web-view?modal=install), which can integrate with LDAP and OAuth.
