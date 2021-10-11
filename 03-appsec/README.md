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
NS=vulnapp

k create ns $NS
k -n $NS create secret generic auth-db-secret \
    --from-literal root_password=P@ssw0rd \
    --from-literal database=userdata \
    --from-literal username=user \
    --from-literal password=password
k -n $NS create secret generic auth-api-secret \
    --from-literal secret=secret123
k -n $NS apply -f ../../apps/03-appsec/images-api/deploy
k -n $NS apply -f ../../apps/03-appsec/auth-api/deploy

k -n $NS get all,ingress
k -n $NS get po -w


k delete ns $NS

```

---

# Demo vulnerable app

## Vulnerabilities:
1. Weak jwt auth scheme with client-side role trust
2. Weak hardcoded HS256 secret
3. Local File Inclusion

## How to use it

1. Deploy it
2. Go to auth service (5000 port on dev)
3. Sign-up any user and login
4. Get redirection to the page with the greatest cat in the world :)
5. Decode JWT token and try to get more privileges
6. Write any interesting file, that you want to read and look at your image b64 data
7. Profit