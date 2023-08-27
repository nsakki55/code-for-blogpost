import socket

s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
s.bind(("ns2-veth0", 0))

ethernet_frame  = b'\x00\x00\x5e\x00\x53\x01' # Destination MAC Address
ethernet_frame += b'\x00\x00\x5e\x00\x53\x02' # Source MAC Address
ethernet_frame += b'\x08\x00'                 # Protocol-Type

ip_header  = b'\x45\x00\x00\x28'  # Version, IHL, DSCP, ECN | Total Length
ip_header += b'\xab\xcd\x40\x00'  # Identification | Flags, Fragment Offset
ip_header += b'\x40\x06\x0a\xff'  # TTL, Protocol | Checksum
ip_header += b'\xc0\x00\x02\x02'  # Source Address
ip_header += b'\xc0\x00\x02\x01'  # Destination Address

tcp_header  = b'\x30\x39\xd4\x31' # Source Port | Destination Port
tcp_header += b'\x00\x00\x00\x00' # Sequence Number
tcp_header += b'\x00\x00\x00\x00' # Acknowledgement Number
tcp_header += b'\x50\x02\xfa\xf0' # Data Offset, Reserved, Flags | Window Size
tcp_header += b'\x2c\x83\x00\x00' # Checksum | Urgent Pointer

packet = ethernet_frame + ip_header + tcp_header

s.send(packet)

