# 自作パケットをsocket通信で送る
## network作成
Network Namespaceを作成

```bash
$ sudo ip netns add ns1
$ sudo ip netns add ns2
```

vethインターフェイスを作成

```bash
$ sudo ip link add ns1-veth0 type veth peer name ns2-veth0
```

vethインターフェイスをnetwork namespaceに所属させる

```bash
$ sudo ip link set ns1-veth0 netns ns1
$ sudo ip link set ns2-veth0 netns ns2
```

ネットワークインターフェイスをupの状態に設定

```bash
$ sudo ip netns exec ns1 ip link set ns1-veth0 up
$ sudo ip netns exec ns2 ip link set ns2-veth0 up
```

IPアドレスを設定

```bash
$ sudo ip netns exec ns1 ip address add 102.0.2.1/24 dev ns1-veth0
$ sudo ip netns exec ns2 ip address add 102.0.2.2/24 dev ns2-veth0
```

MACアドレスを設定

```bash
$ sudo ip netns exec ns1 ip link set dev ns1-veth0 address 00:00:5E:00:53:01
$ sudo ip netns exec ns2 ip link set dev ns2-veth0 address 00:00:5E:00:53:02
```

pingで結果が返ってくることを確認
```bash
$ sudo ip netns exec ns2 ping -c 3 192.0.2.1 -I 192.0.2.2
PING 192.0.2.1 (192.0.2.1) 56(84) bytes of data.
64 bytes from 192.0.2.1: icmp_seq=1 ttl=64 time=1.20 ms
64 bytes from 192.0.2.1: icmp_seq=2 ttl=64 time=0.056 ms
64 bytes from 192.0.2.1: icmp_seq=3 ttl=64 time=0.052 ms

--- 192.0.2.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2015ms
rtt min/avg/max/mdev = 0.052/0.434/1.196/0.538 ms
```

## server起動
```bash
$ sudo ip netns exec ns1 python3 server.py
```

## Packet送信
```bash
$ sudo ip netns exec ns2 python3 raw_packet.py
```
