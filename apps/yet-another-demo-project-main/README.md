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