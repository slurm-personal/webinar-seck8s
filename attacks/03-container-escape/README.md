# Exploit Application Vulnerability to Escape the Container


Status check -> ssrf -> network security exploitation ->

--
jwt scheme:

ms1 - generates
ms2

//зашел на статус чек -> ssrf to internal service that crafts tokens to admin for this status check ->
//service: status check, checks facebook status.


ssrf -> /docs -> see info about jwt -> gen short-lived jwt -> see its crypto problems, default secret: "123" -> can self-generate tokens

go with this token to a web playground (via weak network policy) -> RCE -> read /etc/sa-token -> authenticate your kubectl -> run crypto-miner (dokcer container).


--

1)
admin-form + jwt => hard-coded secret + hs256
    https://auth0.com/blog/brute-forcing-hs256-is-possible-the-importance-of-using-strong-keys-to-sign-jwts/
UI + jwt-protected: take model URL + image file -> RCE
    torch.load(): https://pytorch.org/docs/stable/generated/torch.load.html
    or sklearn: https://machinelearningmastery.com/save-load-machine-learning-models-python-scikit-learn/
Read /etc/sa-token
ubuntu: apt-get and curl/kubectl, internal-only access Kube API


2)
example -> in /docs open to internet ->
admin-form + jwt => hard-coded secret + hs256
    https://auth0.com/blog/brute-forcing-hs256-is-possible-the-importance-of-using-strong-keys-to-sign-jwts/

jwt-protected cats reading service -> LFI: read files with cats. Result: ../../../../../etc/sa-token
go via internet to kube api with sa-token



user-password form + registration.
You register -> follow redirection -> see JWT: role+secret -> replace role with admin -> go to cats again and see another page (with LFI) -> read ../../../../../etc/sa-token and print it base64-encoded -> use it to authenticate your kubectl/curl.

Cats service:
    reads file <img data="base-64-encoded-content"/>
    unauthenticated mode: 503
    user mode: button "Next image" (selecting a random image from a local directory)
    admin mode: text input "filename" (allows "../")
