# Mock email-sending service

A demo service that writes all received request data to a database (emulation of an email broadcasting service). This service logs received data to stdout via `logger.debug()` in order to illustrate how the sensitive data can be leaked through the debugging information.


```sh
NS=mock-email
k create ns $NS

# Install an unprotected dashboard:
k -n $NS apply -f ./deploy
```

Check status:
```sh
k -n $NS get all,ingress
```

Uninstall:
```sh
k delete ns $NS
```

