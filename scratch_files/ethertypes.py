ETHERTYPES_NAMES = """Internet Protocol version 4 (IPv4) 
Address Resolution Protocol (ARP)
Wake-on-LAN[3]
Audio Video Transport Protocol
IETF TRILL Protocol
DECnet Phase IV
Reverse Address Resolution Protocol
AppleTalk (Ethertalk)
AppleTalk Address Resolution Protocol (AARP)
VLAN-tagged frame (IEEE 802.1Q) & Shortest Path Bridging
IPX
IPX
QNX Qnet
Internet Protocol Version 6 (IPv6)
Ethernet flow control
Slow Protocols (IEEE 802.3)
CobraNet
MPLS unicast
MPLS multicast
PPPoE Discovery Stage
PPPoE Session Stage
Jumbo Frames[2]
HomePlug 1.0 MME
EAP over LAN (IEEE 802.1X)
PROFINET Protocol
HyperSCSI (SCSI over Ethernet)
ATA over Ethernet
EtherCAT Protocol
Provider Bridging (IEEE 802.1ad) & Shortest Path Bridging
Ethernet Powerlink[citation needed]
Link Layer Discovery Protocol (LLDP)
SERCOS III
HomePlug AV MME[citation needed]
Media Redundancy Protocol (IEC62439-2)
MAC security (IEEE 802.1AE)
Precision Time Protocol (PTP) over Ethernet (IEEE 1588)
IEEE 802.1ag Connectivity Fault Management (CFM) Protocol 
Fibre Channel over Ethernet (FCoE)
FCoE Initialization Protocol
RDMA over Converged Ethernet (RoCE)
High-availability Seamless Redundancy (HSR)
Ethernet Configuration Testing Protocol[6]
Veritas Low Latency Transport (LLT)"""

ETHERTYPES_VALUES = """0x0800 	
0x0806 	
0x0842 	
0x22F0 	
0x22F3 	
0x6003 	
0x8035 	
0x809B 	
0x80F3 	
0x8100 	
0x8137 	
0x8138 	
0x8204 	
0x86DD 	
0x8808 	
0x8809 	
0x8819 	
0x8847 	
0x8848 	
0x8863 	
0x8864 	
0x8870 	
0x887B 	
0x888E 	
0x8892 	
0x889A 	
0x88A2 	
0x88A4 	
0x88A8 	
0x88AB 	
0x88CC 	
0x88CD 	
0x88E1 	
0x88E3 	
0x88E5 	
0x88F7 	
0x8902 	
0x8906 	
0x8914 	
0x8915 	
0x892F 	
0x9000 	
0xCAFE"""

ETHERTYPES = dict((name, int(value, 16)) for name, value in zip(ETHERTYPES_NAMES.split("\n"),
                                                                ETHERTYPES_VALUES.split("\n")))