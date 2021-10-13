# Demo vulnerable application

Installation:

```sh
k create ns vulnerable-app

k apply -f another-app/deploy

k -n vulnerable-app create secret generic auth-db-secret \
    --from-literal root_password=P@ssw0rd \
    --from-literal database=userdata \
    --from-literal username=user \
    --from-literal password=password
k -n vulnerable-app create secret generic auth-api-secret \
    --from-literal secret=secret123

k -n vulnerable-app apply -f images-api/deploy
k -n vulnerable-app apply -f auth-api/deploy
```

Check status:
```sh
k -n vulnerable-app get all,ingress
k -n vulnerable-app get po -w
```

Uninstall:
```sh
k delete -f another-app/deploy
k -n vulnerable-app delete -f images-api/deploy
k -n vulnerable-app delete -f auth-api/deploy
k delete ns vulnerable-app
```


## Service: auth-api
- `/signup`: register new users and saves their details (email, name, password) into the MySQL database
- `/login`: check user-provided pair email+password and generate a temporary JWT token with the `user_role='user'` using the secret stored in environment variable `SECRET_KEY`
- once the login was successful, redirects to the `image-api` service with the JWT token stored in GET parameter `token`

## Service: image-api
- `/` (no `token`): fails with 401
- `/` (invalid `token`): fails with 403
- `/` (valid JWT in `token`): decodes the JWT using the key stored in env var `SECRET_KEY`, extracts the `user_role` from it. If `user_role='admin'`, offers additional functionality to select the file to read or upload a file

## Service: another-service
- some service that accidentally gave read-write permissions to the default service account in the namespace `vulnerable-app`

## Vulnerabilities:
1. Weak jwt auth scheme with client-side role trust
2. Weak hardcoded HS256 secret
3. Local File Inclusion
4. Remote File Inclusion
5. Root inside the container, ubuntu with apt-get
6. Too permissive service account
