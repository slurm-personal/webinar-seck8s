# Kubernetes Dashboard

Insecure installation instructions for [KubeWebView](https://codeberg.org/hjacobs/kube-web-view/) in the demo cluster:

```sh
k create ns exposed-dashboard

# Install an unprotected dashboard:
k -n exposed-dashboard apply -f ./deploy

# Expose the dashboard via ingress
k -n exposed-dashboard apply -f ./deploy-ingress
```

Check status:
```sh
k -n exposed-dashboard get all,ingress
```

Uninstall:
```sh
k -n exposed-dashboard delete -f ./deploy
k -n exposed-dashboard delete -f ./deploy-ingress
```


> Note: Alternatively, you can install the dashboad using the Helm package [decayofmind/kube-web-view](https://artifacthub.io/packages/helm/decayofmind/kube-web-view?modal=install), which can integrate with LDAP and OAuth.
