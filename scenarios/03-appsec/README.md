# Exploit Application Vulnerabilities

user-password form + registration.
You sign-up -> follow redirection -> see JWT: role+secret -> replace role with admin -> go to cats again and see another page (with LFI) -> read ../../../../../etc/sa-token and print it base64-encoded -> use it to authenticate your kubectl/curl.

Cats service:
    reads file <img data="base-64-encoded-content"/>
    unauthenticated mode: 503
    user mode: button "Next image" (selecting a random image from a local directory)
    admin mode: text input "filename" (allows "../")

Additional: use Postgres, store secret in K8s secrets, read it via kubectl, access DB directly


---

```
NS=vulnapp2

k create ns $NS
k -n $NS create secret generic auth-db-secret \
k -n $NS create secret generic auth-api-secret \
    --from-literal secret=secret123
k -n $NS apply -f ./deploy

k -n $NS get all,ingress
k -n $NS get po -w


k delete ns $NS

```
