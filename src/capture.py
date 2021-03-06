# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 18:25:46 2019
@author: shyoo
"""
from time import gmtime, strftime
from socket import *
import os
import struct
import textwrap

DNS_QUERY_SECTION_FORMAT = struct.Struct("!2H")

def decode_labels(message, offset):
    labels = []

    while True:
        length, = struct.unpack_from("!B", message, offset)

        if (length & 0xC0) == 0xC0:
            pointer, = struct.unpack_from("!H", message, offset)
            offset += 2

            return labels + decode_labels(message, pointer & 0x3FFF), offset

        if (length & 0xC0) != 0x00:
            raise StandardError("unknown label encoding")

        offset += 1

        if length == 0:
            return labels, offset

        labels.append(*struct.unpack_from("!%ds" % length, message, offset))
        offset += length


DNS_QUERY_SECTION_FORMAT = struct.Struct("!2H")

def decode_question_section(message, offset, qdcount):
    questions = []

    for _ in range(qdcount):
        qname, offset = decode_labels(message, offset)

        qtype, qclass = DNS_QUERY_SECTION_FORMAT.unpack_from(message, offset)
        offset += DNS_QUERY_SECTION_FORMAT.size

        question = {"domain_name": qname,
                    "query_type": qtype,
                    "query_class": qclass}

        questions.append(question)

    return questions, offset


DNS_QUERY_MESSAGE_HEADER = struct.Struct("!6H")

def decode_dns_message(message):

    id, misc, qdcount, ancount, nscount, arcount = DNS_QUERY_MESSAGE_HEADER.unpack_from(message)

    qr = (misc & 0x8000) != 0
    opcode = (misc & 0x7800) >> 11
    aa = (misc & 0x0400) != 0
    tc = (misc & 0x200) != 0
    rd = (misc & 0x100) != 0
    ra = (misc & 0x80) != 0
    z = (misc & 0x70) >> 4
    ans = (misc & 32) >> 6
    non = (misc & 16) >> 5
    rcode = misc & 0xF

    offset = DNS_QUERY_MESSAGE_HEADER.size
    questions, offset = decode_question_section(message, offset, qdcount)
    # print(misc, type(misc) ,hex(misc))
    result = {"id": id,
              "flags": flag,
              "is_response": qr,
              "opcode": opcode,
              "is_authoritative": aa,
              "is_truncated": tc,
              "recursion_desired": rd,
              "recursion_available": ra,
              "reserved": z,
              "answer_authen": ans,
              "Non_authen": non,
              "response_code": rcode,
              "question_count": qdcount,
              "answer_count": ancount,
              "authority_count": nscount,
              "additional_count": arcount,
              "questions": questions}

# =============================================================================
#     print('\n\t\t###[ DNS ]###')
# =============================================================================
    dnsString = '\t\t\tid: {}\n'.format(hex(id)) \
    +'\t\t\tFlags: {}\n'.format(hex(misc)) \
    +'\t\t\tIs Response: {}\n'.format(qr) + '\t\t\tOpcode: {}\n'.format(opcode) \
    +'\t\t\tIs Authoritative: {}\n'.format(int(aa)) \
    +'\t\t\tIs Truncated: {}\n'.format(int(tc)) \
    +'\t\t\tRecursion desired: {}\n'.format(int(rd)) \
    +'\t\t\tRecursion available: {}\n'.format(int(ra)) \
    +'\t\t\tZ: Reserved: {}\n'.format(z) \
    +'\t\t\tAnswer authenticated: {}\n'.format(ans) \
    +'\t\t\tNon-authenticated data: {}\n'.format(non) \
    +'\t\t\tReply code: {}\n'.format(rcode) \
    +'\t\t\tQuestions: {}\n'.format(qdcount) \
    +'\t\t\tAnswer RRs: {}\n'.format(ancount) \
    +'\t\t\tAuthority RRs: {}\n'.format(nscount) \
    +'\t\t\tAdditional RRs: {}\n'.format(arcount)
    #print('\t\t\tquestions: {}'.format(questions))
# =============================================================================
    return questions, dnsString
if __name__ == '__main__':
    
    #host = "192.168.181.199"

    #if os.name == 'nt':
    #    sock_protocol = IPPROTO_IP
    #else:
    #    sock_protocol = IPPROTO_ICMP
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))
    ipAddress = s.getsockname()[0]
    RawSocket = socket(AF_INET, SOCK_RAW)
    #sniffer = socket(AF_PACKET, SOCK_RAW, ntohs(3))
    RawSocket.bind((ipAddress, SOCK_RAW))
    #sniffer.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
    packet_inven = []
    packet_count = 0

    if os.name == 'nt':
        RawSocket.ioctl(SIO_RCVALL, RCVALL_ON)

    filter_option = input('filter option : ')
    special_keyword = input('special keyword option : ')
    if not os.path.isdir(filter_option+' '+special_keyword):
        os.mkdir(filter_option+' '+special_keyword)
    
    os.chdir(os.getcwd()+'\\'+filter_option+' '+special_keyword)
    
    try:
        while True:

            #raw_data = recvData(sniffer)
            Packet = RawSocket.recvfrom(65565)
            #EthernetHeader = Packet[0][0:14]
            #Ethernet_Header = struct.unpack('!6s6sH', EthernetHeader)
            raw_data = Packet[0]
            #raw_data = sniffer.recvfrom(65565)
            #Ethdest, Ethsrc, Ethprototype = struct.unpack('! 6s 6s H', Ethernet_Header)

            #Ethbyte_str = map('{:02x}'.format, Ethdest)
            #Ethdest_mac = ':'.join(Ethbyte_str).upper() # destination mac addr

            #Ethbyte_str = map('{:02x}'.format, Ethsrc)
            #Ethsrc_mac = ':'.join(Ethbyte_str).upper() # destination src addr

            #Ethproto = htons(Ethprototype)
            IPv4data = raw_data[0:]

            #print('###[ Ethernet ]###')
            #print('\tdst: {}, \n \tsrc: {}, \n \ttype: {}'.format(Ethdest_mac, Ethsrc_mac, Ethproto))
            #proto = map('{:x}'.format, raw_data[9:10])
            #IPv4proto = ':'.join(proto).upper()

            (ver,) = struct.unpack('!B', raw_data[0:1])
            IPv4ver = ver >> 4
            IPv4len = (raw_data[0] & 15) * 4
            (IPv4service,) = struct.unpack('!B', raw_data[1:2])
            IPv4service = hex(IPv4service)
            (IPv4total,) = struct.unpack('!H', raw_data[2:4])
            (IPv4id,) = struct.unpack('!H', raw_data[4:6])
            IPv4id = hex(IPv4id)
            (flag,) = struct.unpack('!H', raw_data[6:8])
            #IPv4flag = flag >> 13 # 플래그 조금다름
            IPv4flag = hex(flag)
            IPv4rb = int(flag == 32768)
            IPv4df = int(flag == 16384)
            IPv4mf = int(flag == 8192)
            (offset,) = struct.unpack('!H', raw_data[6:8])
            IPv4offset = (offset & 0x1FFF) << 2
            (IPv4ttl,) = struct.unpack('!B', raw_data[8:9])
            (IPv4type,) = struct.unpack('!B', raw_data[9:10])
            (check_sum,) = struct.unpack('!H', raw_data[10:12])
            IPv4check_sum = hex(check_sum)
            src = struct.unpack('!4B', raw_data[12:16])
            IPv4src = '%d.%d.%d.%d' % src
            dst = struct.unpack('!4B', raw_data[16:20])
            IPv4dst = '%d.%d.%d.%d' % dst

            IPv4version_header_length = IPv4data[0]
            #IPv4version = IPv4version_header_length >> 4
            IPv4header_length = (IPv4version_header_length & 15) * 4
            #IPv4ttl, IPv4proto, IPv4src, IPv4target = struct.unpack('! 8x B B 2x 4s 4s', IPv4data[:20])
            #IPv4src = '.'.join(map(str, IPv4src))
            #IPv4target = '.'.join(map(str, IPv4target))
            ETCdata = IPv4data[IPv4header_length:]

            strIpHeader = '\n###[ IP ]###\n' + '\tVersion: {} \n \tHeader Length: {} \n \tDifferentiated Services Field: {} \n'\
                .format(IPv4ver, IPv4len, IPv4service) + '\tTotal Length: {} \n \tIdentification: {} \n \tFlags: {} \n'\
                .format(IPv4total, IPv4id, IPv4flag) + '\t\tReserved bit: {} \n \t\tDon\'t fragment: {} \n \t\tMore fragments: {}\n'\
                .format(IPv4rb, IPv4df, IPv4mf) + '\tFragment offset: {} \n \tTime to live: {} \n \tProtocol: {} \n'\
                .format(IPv4offset, IPv4ttl, IPv4type) + '\tHeader checksum status: {} \n \tSource: {} \n \tDestination: {}\n'\
                .format(IPv4check_sum, IPv4src, IPv4dst)

            # ICMP
            if IPv4type == 1:
                #ICMPtype, ICMPcode, ICMPchecksum = struct.unpack('! B B H', ETCdata[:4])

                (ICMPtype,) = struct.unpack('!B', ETCdata[0:1])
                (ICMPcode,) = struct.unpack('!B', ETCdata[1:2])
                (ICMPchecksum,) = struct.unpack('!H', ETCdata[2:4])
                ICMPchecksum = hex(ICMPchecksum)
                (ICMPidentifier_be,) = struct.unpack('!H', ETCdata[4:6])
                ICMPidentifier_le = int(hex(ICMPidentifier_be) + '00',16)
                (ICMPsequence_be,) = struct.unpack('!H', ETCdata[6:8])
                ICMPsequence_le = int(hex(ICMPsequence_be) + '00',16)
                #(ICMPpointer,) = struct.unpack('!B', ETCdata[4:5])
                #(ICMPidentifier,) = struct.unpack('!H', ETCdata[5:7])
                #(ICMPsequence,) = struct.unpack('!H', ETCdata[7:9])
                #(ICMPgateway,) = struct.unpack('!2H', ETCdata[9:13])
                #(ICMPmask,) = struct.unpack('!2H', ETCdata[13:17])
                TEMPdata = ETCdata[8:]
                try:
                    TRdata = TEMPdata.decode('utf-8')
                except:
                    TRdata = TEMPdata
                # 빠진거 identifier be,le / sequence number be,le / data, length
                """
                print()
                print('\tType: {} \n \tCode: {} \n \tChecksum: {}'.format(ICMPtype, ICMPcode, ICMPchecksum))
                print('\tIdentifier (BE): {} \n \tSequence number (BE): {}'.format(ICMPidentifier_be, ICMPidentifier_le))
                print('\tIdentifier (LE): {} \n \tSequence number (LE): {}'.format(ICMPsequence_be, ICMPsequence_le))
                print('\tData: {}'.format(TEMPdata.decode('utf-8')))
                """
                strIcmpHeader = '\n###[ ICMP ]###\n' + '\tType: {} \n \tCode: {} \n \tChecksum: {} \n'\
                    .format(ICMPtype, ICMPcode, ICMPchecksum) + '\tIdentifier (BE): {} \n \tSequence number (BE): {} \n'\
                    .format(ICMPidentifier_be, ICMPidentifier_le) + '\tIdentifier (LE): {} \n \tSequence number (LE): {}\n'\
                    .format(ICMPsequence_be, ICMPsequence_le) + '\tData: {}\n'.format(TRdata)

                #print('\tICMP Data:')

            # TCP
            elif IPv4type == 6:
                #TCPsrc_port, TCPdest_port, TCPsequence, TCPacknowledgment, \
                #TCPoffset_reserved_flags = struct.unpack('! H H L L H', ETCdata[:14])
                #tcp_header = struct.unpack('!HHLLBBHHH', ETCdata[0:20])
                (TCPsrc_port,) = struct.unpack('!H', ETCdata[0:2])
                (TCPdest_port,) = struct.unpack('!H', ETCdata[2:4])
                (TCPsequence,) = struct.unpack('!L', ETCdata[4:8])
                (TCPacknowledgment,) = struct.unpack('!L', ETCdata[8:12])
                TCPlength = len(ETCdata)
                #(TCPoffset,) = struct.unpack('!H', ETCdata[12:13])
                (flags,) = struct.unpack('!H', ETCdata[12:14])
                (flags,) = struct.unpack('!H', ETCdata[12:14])
                (TCPflags,) = struct.unpack('!b', ETCdata[13:14])
                TCPflags = hex(TCPflags)
                (TCPwindow,) = struct.unpack('!H', ETCdata[14:16])
                (TCPchecksum,) = struct.unpack('!H', ETCdata[16:18])
                TCPchecksum = hex(TCPchecksum)
                (TCPurgptr,) = struct.unpack('!H', ETCdata[18:20])

                TCPoffset = (flags >> 12) * 4
                TCPflag_res1 = (flags & 2048) >> 11
                TCPflag_res2 = (flags & 1024) >> 10
                TCPflag_res3 = (flags & 512) >> 9
                TCPflag_res = TCPflag_res1 & TCPflag_res2 & TCPflag_res3
                TCPflag_hs = (flags & 256) >> 8
                TCPflag_cwr = (flags & 128) >> 7
                TCPflag_ece = (flags & 64) >> 6
                TCPflag_urg = (flags & 32) >> 5
                TCPflag_ack = (flags & 16) >> 4
                TCPflag_psh = (flags & 8) >> 3
                TCPflag_rst = (flags & 4) >> 2
                TCPflag_syn = (flags & 2) >> 1
                TCPflag_fin = flags & 1

                TEMPdata = ETCdata[TCPoffset:]

                strTcpHeader = '\n###[ TCP ]###\n' + '\tSource Port: {} \n \tDestination Port: {} \n'\
                    .format(TCPsrc_port, TCPdest_port) + '\tSequence number: {} \n \tAcknowledgment number: {} \n'\
                    .format(TCPsequence, TCPacknowledgment) + '\tHeader Length: {} \n \tFlags: {} \n'\
                    .format(TCPlength, TCPflags) + '\t\tReserved: {} \n \t\tNonce: {} \n \t\tCongestion Window Reduced: {} \n'\
                    .format(TCPflag_res, TCPflag_hs, TCPflag_cwr) + '\t\tECN-Echo: {} \n \t\tUrgent: {} \n \t\tAcknowledgment:{} \n'\
                    .format(TCPflag_ece, TCPflag_urg, TCPflag_ack) + '\t\tPush: {} \n \t\tReset: {} \n \t\tSyn: {} \n \t\tFin: {} \n'\
                    .format(TCPflag_psh, TCPflag_rst, TCPflag_syn, TCPflag_fin) + '\tWindow size value: {} \n \tChecksum: {} \n \tUrgent pointer:{} \n'\
                    .format(TCPwindow, TCPchecksum, TCPurgptr)

                #if len(TEMPdata) > 0:

                if TCPsrc_port == 80 or TCPdest_port == 80:
                    
                    strHttpHeader = '\n\t###[ HTTP ]###\n'

                    try:
                        try:
                            HTTPdata = TEMPdata.decode('utf-8')
                        except:
                            HTTPdata = TEMPdata
                        http_info = str(HTTPdata).split('\n')
                        for line in http_info:
                            ad=  '\t\t' +str(line) + "\n"
                            strHttpHeader = strHttpHeader + ad
                    except:
                        size = 80
                        size -= len('\t\t')
                        if isinstance(TEMPdata, bytes):
                            joinPdata = ''.join(r'\x{:02x}'.format(byte) for byte in TEMPdata)
                            if size % 2:
                                size -= 1
                        strHttpHeader = strHttpHeader + '\n'.join(['\t\t' + line for line in textwrap.wrap(joinPdata, size)])
                        #print('HTTPS:' + str(TEMPdata))
                        
                if TCPsrc_port == 443 or TCPdest_port == 443:
                    
                    strHttpsHeader = '\n\t###[ HTTPS ]###\n'

                    try:
                        try:
                            HTTPSdata = TEMPdata.decode('utf-8')
                        except:
                            HTTPSdata = TEMPdata
                        http_info = str(HTTPSdata).split('\n')
                        for line in http_info:
                            ad=  '\t\t' +str(line) + "\n"
                            strHttpsHeader = strHttpsHeader + ad
                    except:
                        size = 80
                        size -= len('\t\t')
                        if isinstance(TEMPdata, bytes):
                            joindata = ''.join(r'\x{:02x}'.format(byte) for byte in TEMPdata)
                            if size % 2:
                                size -= 1
                        strHttpHeader = strHttpHeader + '\n'.join(['\t\t' + line for line in textwrap.wrap(joindata, size)])
                        #print('HTTPS:' + str(TEMPdata))
            elif IPv4type == 17:

                (UDPsrc_port,) = struct.unpack('! H', ETCdata[0:2])
                (UDPdest_port,) = struct.unpack('! H', ETCdata[2:4])
                (UDPsize,) = struct.unpack('! H', ETCdata[4:6])
                (UDPcheck_sum,) = struct.unpack('! H', ETCdata[6:8])
                UDPcheck_sum = hex(UDPcheck_sum)
                TEMPdata = ETCdata[8:]

                strUdpHeader = '\n###[ UDP ]###\n' + '\tSource Port: {} \n \tDestination Port: {} \n \tLength: {}\n'\
                    .format(UDPsrc_port, UDPdest_port, UDPsize) + '\tChecksum: {}\n'.format(UDPcheck_sum)

                if filter_option.find('dns') != -1:
                    #regDNS = re.compile('[^a-zA-Z0-9-@:%._\+~#=]')

                    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    recvHeader = struct.unpack_from('!HHHHHH', TEMPdata)
                    #recvData = TEMPdata[13:].split(b'\x00', 1)
                    flag_QnA = recvHeader[1] & 0b1000000000000000
                    if flag_QnA == 0 :
                        strDnsHeader = '\n\t###[ DNS Query ]###\n'
                    else :
                        strDnsHeader = '\n\t###[ DNS Response ]###\n'
                    strDnsHeader = strDnsHeader + '\t\tTime : ' + now + '\n\t\tTransaction ID : ' + str(hex(recvHeader[0])) + '\n\t\tFlags : ' \
                                   + str(hex(recvHeader[1])) + '\n\t\tQuestions : ' + str(recvHeader[2])+ '\n\t\tAnswer RR : ' \
                                   + str(recvHeader[3]) + '\n\t\tAuthority RRs: ' +  str(recvHeader[4]) + '\n\t\tAdditional RRs: '\
                                   + str(recvHeader[5]) + "\n"

                    # ㅡㅡㅡㅡ 여기까지 Domain Name System

                    if (UDPsrc_port == 53 or UDPdest_port == 53) and filter_option.find('dns') != -1:
                        strDnsHeader = strDnsHeader + '\n\t\t###[ DNS ]###\n'
                        dnsquery, dnsString = decode_dns_message(TEMPdata)
                        strDnsHeader = strDnsHeader + dnsString
                        strDnsHeader = strDnsHeader + '\n\t\t\t###[ DNS Queries ]###\n' + '\t\t\t\tDomain name: '
                        #print('\n\t\t\t###[ DNS Queries ]###')
                        domain_name = [dnsquery[0]['domain_name'][i].decode('utf-8') for i, _ in enumerate(dnsquery[0]['domain_name'])]
                        #print('\t\t\t\tDomain name: ', end='')
                        for i, v in enumerate(domain_name):
                            if i+1 == len(domain_name):
                                strDnsHeader = strDnsHeader + v
                                #print(v, end='')
                            else:
                                strDnsHeader = strDnsHeader + v + "."
                                #print(v, end='.')

                        strDnsHeader = strDnsHeader + '\n\t\t\t\tQuery type: {}\n'.format(dnsquery[0]['query_type']) +\
                                       '\t\t\t\tQuery class: {}\n'.format(dnsquery[0]['query_class'])

                        #print('\n\t\t\t\tQuery type: {}'.format(dnsquery[0]['query_type']))
                        #print('\t\t\t\tQuery class: {}'.format(dnsquery[0]['query_class']))
                        #print('\t\t\t',str(TEMPdata))
                        
            
            #filter_option_list = filter_option.split(" ")
            #filter_count = 0
# =============================================================================
# TCP    
# =============================================================================
            if filter_option.find('tcp') != -1 and IPv4type == 6:
                
                if filter_option.find('http') != -1 and \
                    filter_option.find('https') == -1:
                    
                    packet_inven.append(
                            '---------------------No. {}'
                            .format(packet_count)
                            +strIpHeader+strTcpHeader+strHttpHeader)
                    if packet_inven.pop().find(special_keyword) != -1:
                        print('---------------------No. {}'
                              .format(packet_count),
                              '---------------------')
                        print(strIpHeader, strTcpHeader)
                        print(strHttpHeader)
                    
                elif filter_option.find('https') != -1:
                    
                    packet_inven.append(
                            '---------------------No. {}'
                            .format(packet_count)
                            +strIpHeader+strTcpHeader+strHttpsHeader)
                    if packet_inven.pop().find(special_keyword) != -1:
                        print('---------------------No. {}'
                              .format(packet_count),
                              '---------------------')
                        print(strIpHeader, strTcpHeader)
                        print(strHttpsHeader)
                else:
                    
                    packet_inven.append(
                            '---------------------No. {}'
                            .format(packet_count)
                            +strIpHeader+strTcpHeader)
                    if packet_inven.pop().find(special_keyword) != -1:
                        print('---------------------No. {}'
                              .format(packet_count),
                              '---------------------')
                        print(strIpHeader, strTcpHeader)
# =============================================================================
# UDP
# =============================================================================
            if filter_option.find('udp') != -1 and IPv4type == 17:
                
                if filter_option.find('dns') != -1:
                    
                    packet_inven.append(
                            '---------------------No. {}'
                            .format(packet_count)
                            +strIpHeader+strUdpHeader+strDnsHeader)
                    if packet_inven.pop().find(special_keyword) != -1:
                        print('---------------------No. {}'
                              .format(packet_count),
                              '---------------------')
                        print(strIpHeader, strUdpHeader)
                        print(strDnsHeader)
                else:
                    
                    packet_inven.append(
                            '---------------------No. {}'
                            .format(packet_count)
                            +strIpHeader+strUdpHeader)
                    if packet_inven.pop().find(special_keyword) != -1:
                        print('---------------------No. {}'
                              .format(packet_count),
                              '---------------------')
                        print(strIpHeader, strUdpHeader)
# =============================================================================
# ICMP
# =============================================================================
            if filter_option.find('icmp') != -1 and IPv4type == 1:
                
                packet_inven.append(
                        '---------------------No. {}'
                        .format(packet_count)
                        +strIpHeader+strIcmpHeader)
                print('---------------------No. {}'
                          .format(packet_count),
                          '---------------------')
                print(strIpHeader, strIcmpHeader)
# =============================================================================
            #filter_count=0
            packet_count += 1
        #print('\n')
    except KeyboardInterrupt:
        if os.name == 'nt':
            RawSocket.ioctl(SIO_RCVALL, RCVALL_OFF)
            
    for index, packet in enumerate(packet_inven):
        f = open('packet_log'+str(index)+'.txt', 'w')
        f.write(packet)