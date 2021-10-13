# Mock email-sending service

A demo service that writes all received request data to a database (emulation of an email broadcasting service):
- This service logs received data to stdout via `logger.debug()` in order to illustrate how the sensitive data can be leaked through the debugging information.
- In addition, it stores the DB credentials in a ConfigMap, not in a Secret or elsewhere.


```sh
k create ns mock-email

# Install an unprotected dashboard:
k -n mock-email apply -f ./deploy
```

Check status:
```sh
k -n mock-email get all,ingress
```

Uninstall:
```sh
k -n mock-email delete -f ./deploy
k delete ns mock-email
```

