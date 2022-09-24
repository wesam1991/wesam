import random
from random import randint
import re
import netifaces
import socket
import subprocess
import struct
import os
import hashlib
import platform


BRED = '\033[1;31;40m'
RED = '\033[0;31;40m'
BRED_BLACK = '\033[1;30;41m'
RED_BLACK = '\033[0;30;41m'
BGREEN = '\033[1;32;40m'
GREEN = '\033[0;32;40m'
BGREEN_BLACK = '\033[1;30;42m'
GREEN_BLACK = '\033[0;30;42m'
BYELLOW = '\033[1;33;40m'
YELLOW = '\033[0;33;40m'
BBLUE = '\033[1;34;40m'
BLUE = '\033[0;34;40m'
BMAGENTA = '\033[1;35;40m'
MAGENTA = '\033[0;35;40m'
BCYAN = '\033[1;36;40m'
CYAN = '\033[0;36;40m'
BWHITE = '\033[1;37;40m'
WHITE = '\033[0;37;40m'


def screen_clear():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix' or os.name == 'Linux':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')


def get_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    _, port = sock.getsockname()
    sock.close()

    return port


def system_call(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()


def searchInterface():
    ifaces = netifaces.interfaces()
    local_ip = get_machine_default_ip()
    networkInterface = ''

    for iface in ifaces:
        data = netifaces.ifaddresses(iface)
        if str(data).find(local_ip) != -1:
            networkInterface = iface

    return networkInterface


def ping(host, time='1'):
    # parameter = '-n' if platform.system().lower() == 'windows' else '-c'
    ping = 'ping -t 1 -c 1 -W %s %s >/dev/null' % (time, host)
    response = os.system(ping)

    if response == 0:
        return True
    else:
        return False


def get_default_gateway_mac():
    return system_call("route -n get default | grep 'gateway' | awk '{print $2}'").decode()


def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                # If not default route or not RTF_GATEWAY, skip it
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


def get_machine_default_ip(type='ip'):
    """Return the default gateway IP for the machine."""
    gateways = netifaces.gateways()
    defaults = gateways.get("default")
    if not defaults:
        return

    def default_ip(family):
        gw_info = defaults.get(family)
        if not gw_info:
            return
        addresses = netifaces.ifaddresses(gw_info[1]).get(family)
        if addresses:
            if type == 'mask':
                return addresses[0]["netmask"]
            else:
                return addresses[0]["addr"]

    return default_ip(netifaces.AF_INET) or default_ip(netifaces.AF_INET6)


def _enable_mac_iproute():
    cmd = 'sudo sysctl -w net.inet.ip.forwarding=1'
    try:
        exec(cmd)
    except:
        print(RED + '\nError executing %s. Please execute it manually' %
              cmd + WHITE)


def _disable_mac_iproute():
    cmd = 'sudo sysctl -w net.inet.ip.forwarding=0'
    try:
        exec(cmd)
    except:
        print(RED + '\nError executing %s. Please execute it manually' %
              cmd + WHITE)


def _enable_linux_iproute():
    """
    Enables IP route ( IP Forward ) in linux-based distro
    """

    file_path = "/proc/sys/net/ipv4/ip_forward"
    with open(file_path) as f:
        if f.read() == 1:
            # already enabled
            return
    with open(file_path, "w") as f:
        print(1, file=f)


def _disable_linux_iproute():
    """
    Disables IP route ( IP Forward ) in linux-based distro
    """
    file_path = "/proc/sys/net/ipv4/ip_forward"
    with open(file_path) as f:
        if f.read() == 0:
            # already enabled
            return
    with open(file_path, "w") as f:
        print(0, file=f)

# def _enable_windows_iproute():
#     """
#     Enables IP route (IP Forwarding) in Windows
#     """
#     from services import WService
#     # enable Remote Access service
#     service = WService("RemoteAccess")
#     service.start()


def disable_ip_route(verbose=1):
    """
    Disables IP forwarding
    """
    if verbose > 0:
        print("[!] Disabling IP Routing...")
    # _enable_windows_iproute() if "nt" in os.name else _disable_linux_iproute()
        ops = platform.system()
        if ops == 'Darwin':
            _disable_mac_iproute()
        if ops == 'Linux':
            _disable_linux_iproute()
    if verbose > 0:
        print("[!] IP Routing disabled.")


def enable_ip_route(verbose=1):
    """
    Enables IP forwarding
    """
    if verbose > 0:
        print("[!] Enabling IP Routing...")
    # _enable_windows_iproute() if "nt" in os.name else _enable_linux_iproute()
        ops = platform.system()
        if ops == 'Darwin':
            _enable_mac_iproute()
        if ops == 'Linux':
            _enable_linux_iproute()
    if verbose > 0:
        print("[!] IP Routing enabled.")


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def long2ip(ip):
    return str(socket.inet_ntoa(struct.pack('!L', ip)))


def generate_random_string(len_ini, len_end, type):
    len = generate_random_integer(len_ini, len_end)

    if type == 'all':
        str = ''.join(chr(i) for i in range(128))
        result_str = ''.join(random.choice(str) for i in range(len))
    elif type == 'printable':
        result_str = ''.join(random.choice(
            '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c') for i in range(len))
    elif type == 'ascii':
        result_str = ''.join(random.choice(
            '0123456789abcdefghijklmnopqqrstuvwxyz') for i in range(len))
    else:
        # By default use 'hex'
        result_str = ''.join(random.choice('0123456789abcdef')
                             for i in range(len))

    return result_str


def generate_random_integer(len_ini, len_end):
    return randint(len_ini, len_end)


def create_message(method, contactdomain, fromuser, fromname, fromdomain, touser, toname, todomain, proto, domain, useragent, fromport, branch, callid, tag, cseq, totag, digest, auth_type, referto, withsdp, via, rr):
    if method == 'REGISTER' or method == 'NOTIFY' or method == 'ACK':
        starting_line = '%s sip:%s SIP/2.0' % (method, domain)
    else:
        starting_line = '%s sip:%s@%s SIP/2.0' % (method, touser, domain)

    if branch == '':
        branch = generate_random_string(71, 71, 'ascii')
    if callid == '':
        callid = generate_random_string(32, 32, 'hex')
    if tag == '':
        tag = generate_random_string(8, 8, 'hex')

    if method == 'REFER' and referto == '':
        referto = '999'

    headers = dict()
    if via == '':
        headers['Via'] = 'SIP/2.0/%s %s:%s;branch=%s' % (
            proto.upper(), contactdomain, fromport, branch)
    else:
        headers['Via'] = via

    if rr != '':
        rrs = rr.split("#")
        count = 0

        # for rr in rrs:
        for rr in rrs[::-1]:
            count += 1
            headers['Route %s' % str(count)] = rr

    headers['From'] = '%s <sip:%s@%s>;tag=%s' % (
        fromname, fromuser, fromdomain, tag)

    if method == 'NOTIFY':
        if totag == '':
            headers['To'] = '<sip:%s>' % todomain
        else:
            headers['To'] = '<sip:%s>;tag=%s' % (todomain, totag)
    else:
        if totag == '':
            headers['To'] = '%s <sip:%s@%s>' % (toname, touser, todomain)
        else:
            headers['To'] = '%s <sip:%s@%s>;tag=%s' % (
                toname, touser, todomain, totag)

    if method != 'CANCEL' and method != 'ACK':
        headers['Contact'] = '<sip:%s@%s:%d;transport=%s>' % (
            fromuser, contactdomain, fromport, proto)

    headers['Call-ID'] = '%s' % callid

    if digest != '':
        if auth_type == 2:
            headers['Proxy-Authorization'] = '%s' % digest
        else:
            headers['Authorization'] = '%s' % digest

    headers['CSeq'] = '%s %s' % (cseq, method)
    headers['Max-Forwards'] = '70'

    if method == 'REFER':
        headers['Refer-To'] = '<sip:%s@%s>' % (referto, domain)
        headers['Referred-By'] = '<sip:%s@%s:%s>' % (
            fromuser, domain, fromport)

    if method == 'SUBSCRIBE':
        headers['Accept'] = 'application/x-as-feature-event+xml'
        headers['Event'] = 'as-feature-event'

    if method == 'NOTIFY':
        headers['Event'] = 'keep-alive'

    if method != 'ACK':
        headers['User-Agent'] = '%s' % useragent
        if method != 'CANCEL':
            headers['Allow'] = 'INVITE,REGISTER,ACK,CANCEL,BYE,NOTIFY,REFER,OPTIONS,INFO,SUBSCRIBE,UPDATE,PRACK,MESSAGE'

    if method == 'REGISTER':
        headers['Expires'] = '10'

    msg = starting_line+'\r\n'
    for h in headers.items():
        # msg += '%s: %s\r\n' % h
        name = h[0]
        value = h[1]

        m = re.search('^Route', name)
        if m:
            name = 'Route'
        msg += '%s: %s\r\n' % (name, value)

    sdp = ''
    if withsdp == 1:
        sdp = '\r\n'
        sdp += 'v=0\r\n'
        sdp += 'o=anonymous 1312841870 1312841870 IN IP4 %s\r\n' % contactdomain
        sdp += 's=session\r\n'
        sdp += 'c=IN IP4 %s\r\n' % contactdomain
        sdp += 't=0 0\r\n'
        sdp += 'm=audio 2362 RTP/AVP 0\r\n'
        sdp += 'a=rtpmap:18 G729/8000\r\n'
        sdp += 'a=rtpmap:0 PCMU/8000\r\n'
        sdp += 'a=rtpmap:8 PCMA/8000\r\n'

    if withsdp == 2:
        # Use SRTP
        sdp = '\r\n'
        sdp += 'v=0\r\n'
        sdp += 'o=anonymous 1312841870 1312841870 IN IP4 %s\r\n' % contactdomain
        sdp += 's=SIP Call\r\n'
        sdp += 'c=IN IP4 %s\r\n' % contactdomain
        sdp += 't=0 0\r\n'
        sdp += 'm=audio 2362 RTP/AVP 0\r\n'
        sdp += 'a=sendrecv\r\n'
        sdp += 'a=rtpmap:18 G729/8000\r\n'
        sdp += 'a=fmtp:18 annexb=no\r\n'
        sdp += 'a=ptime:20\r\n'
        sdp += 'a=rtpmap:8 PCMA/8000\r\n'
        sdp += 'a=rtpmap:4 G723/8000\r\n'
        sdp += 'a=rtpmap:9 G722/8000\r\n'
        sdp += 'a=rtpmap:97 iLBC/8000\r\n'
        sdp += 'a=fmtp:97 mode=30\r\n'
        sdp += 'a=rtpmap:2 G726-32/8000\r\n'
        sdp += 'a=rtpmap:123 opus/48000/2\r\n'
        sdp += 'a=rtpmap:101 telephone-event/8000\r\n'
        sdp += 'a=fmtp:101 0-15\r\n'
        sdp += 'a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:4EvYRd22P8n36wRrlWCMZIWegovyv7iWm464D4Pt\r\n'
        sdp += 'a=crypto:2 AES_CM_128_HMAC_SHA1_32 inline:mWQ4cakWKOnfH9Tji2pEF87JtVFUqBAMPqub9roe\r\n'

    msg += 'Content-Length: ' + str(len(sdp)) + '\r\n'
    msg += sdp

    msg += '\r\n'

    return (msg)


def create_response_error(message, fromuser, touser, proto, domain, fromport, cseq, method, branch, callid, tag, totag, iplocal, via, auth_code):
    realm = 'asterisk'
    nonce = generate_random_string(8, 8, 'ascii')
    digest = 'Digest algorithm=MD5, realm="%s", nonce="%s\"' % (realm, nonce)

    starting_line = 'SIP/2.0 %s' % message

    headers = dict()
    if via == '':
        headers['Via'] = 'SIP/2.0/%s %s:%s;branch=%s' % (
            proto.upper(), domain, fromport, branch)
    else:
        vias = via.split("#")
        count = 0

        for via in vias[::-1]:
            count += 1
            headers['Via %s' % str(count)] = via

    headers['From'] = '<sip:%s@%s>;tag=%s' % (fromuser, domain, totag)
    headers['To'] = '<sip:%s@%s>;tag=%s' % (touser, iplocal, tag)
    headers['Call-ID'] = '%s' % callid
    headers['CSeq'] = '%d %s' % (cseq, method)
    if method == 'BYE':
        headers[auth_code] = '%s' % digest
        # headers['WWW-Authenticate'] = '%s' % digest
        # headers['Proxy-Authenticate'] = '%s' % digest
    headers['Content-Length'] = '0'

    msg = starting_line+'\r\n'
    for h in headers.items():
        #     msg += '%s: %s\r\n' % h
        name = h[0]
        value = h[1]

        m = re.search('^Via', name)
        if m:
            name = 'Via'
        msg += '%s: %s\r\n' % (name, value)

    msg += '\r\n'

    return (msg)


def create_response_ok(fromuser, touser, proto, domain, fromport, cseq, branch, callid, tag, totag):
    starting_line = 'SIP/2.0 200 Ok'

    headers = dict()
    headers['Via'] = 'SIP/2.0/%s %s:%s;branch=%s' % (
        proto.upper(), domain, fromport, branch)
    headers['From'] = '<sip:%s@%s>;tag=%s' % (fromuser, domain, totag)
    headers['To'] = '<sip:%s@%s>;tag=%s' % (touser, domain, tag)
    headers['Call-ID'] = '%s' % callid
    headers['CSeq'] = '%d BYE' % cseq
    headers['Content-Length'] = '0'

    msg = starting_line+'\r\n'
    for h in headers.items():
        msg += '%s: %s\r\n' % h

    msg += '\r\n'

    return (msg)


def parse_message(buffer):
    headers = buffer.split('\r\n')

    data = dict()
    data['sipuser'] = ''
    data['sipdomain'] = ''
    data['ua'] = ''
    data['via'] = ''
    data['via2'] = ''
    data['rr'] = ''
    data['route'] = ''
    data['auth-type'] = 1
    data['type'] = 'Unknown'

    for header in headers:
        m = re.search('^SIP\/[0-9|\.]+\s([0-9]+)\s(.+)', header)
        if m:
            data['response_code'] = '%s' % (m.group(1))
            data['response_text'] = '%s' % (m.group(2))

        m = re.search('([a-z|A-Z]+)\ssip\:(.*)\sSIP\/[0-9|\.]*', header)
        if m:
            data['method'] = '%s' % (m.group(1))
            uri = '%s' % (m.group(2))
            if uri.find('@') > 0:
                n = re.search('(.*)@(.*)', uri)
                data['sipuser'] = '%s' % (n.group(1))
                data['sipdomain'] = '%s' % (n.group(2))
            else:
                data['sipdomain'] = uri
            if data['sipdomain'].find(':') > 0:
                n = re.search('(.*):(.*)', uri)
                data['sipdomain'] = '%s' % (n.group(1))
                data['sipport'] = '%s' % (n.group(2))
            else:
                data['sipport'] = '5060'

        m = re.search('^From:\s.*\<sip:([a-z|A-z|0-9|_]*)\@.*', header)
        if m:
            data['fromuser'] = '%s' % (m.group(1))

        m = re.search('^From:\s(.+)', header)
        if m:
            hfrom = '%s' % (m.group(1))

            try:
                n = re.search('.*;tag=(.+)', hfrom)
                if n:
                    data['fromtag'] = '%s' % (n.group(1))
                else:
                    data['fromtag'] = ''
            except:
                data['fromtag'] = ''

        m = re.search('^Record-Route:\s(.*)', header)
        if m:
            if data['rr'] == '':
                data['rr'] = '%s' % (m.group(1))
            else:
                data['rr'] = data['rr'] + '#' + '%s' % (m.group(1))

        m = re.search('^Via:\s(.*)', header)
        if m:
            data['via'] = '%s' % (m.group(1))

            if data['via2'] == '':
                data['via2'] = '%s' % (m.group(1))
            else:
                data['via2'] = '%s' % (m.group(1)) + '#' + data['via2']

            n = re.search('.+;branch=(.+);*.*', data['via'])
            if n:
                data['branch'] = '%s' % (n.group(1))
            else:
                data['branch'] = ''

        m = re.search('^Call-ID:\s(.*)', header)
        if m:
            data['callid'] = '%s' % (m.group(1))

        m = re.search('^Server:\s(.+)', header)
        if m:
            data['ua'] = '%s' % (m.group(1))
            data['type'] = 'Server'
        else:
            m = re.search('^User-Agent:\s(.+)', header)
            if m:
                data['ua'] = '%s' % (m.group(1))
                data['type'] = 'Device'

        m = re.search('^To:\s(.+)', header)
        if m:
            to = '%s' % (m.group(1))

            try:
                n = re.search('.*;tag=(.+)', to)
                if n:
                    data['totag'] = '%s' % (n.group(1))
                else:
                    data['totag'] = ''
            except:
                data['totag'] = ''

        m = re.search('^Contact:\s(.+)', header)
        if m:
            m = re.search('\@', header)
            if m:
                m = re.search(
                    '^Contact:\s.*\<sip:([a-z|A-z|0-9|_]*)\@(.*)\>.*', header)
                # '^Contact:\s.*\<sip:([a-z|A-z|0-9|_]*)\@([0-9|\.]*):*.*\>.*', header)
                if m:
                    data['contactuser'] = '%s' % (m.group(1))
                    data['contactdomain'] = '%s' % (m.group(2))
            else:
                m = re.search(
                    '^Contact:\s.*\<sip:(.*)\>.*', header)
                if m:
                    data['contactuser'] = ''
                    data['contactdomain'] = '%s' % (m.group(1))

        m = re.search('^CSeq:\s([0-9]+)\s.*', header)
        if m:
            data['cseq'] = '%s' % (m.group(1))

        m = re.search('^Authorization:\s(.+)', header)
        if m:
            data['auth'] = '%s' % (m.group(1))
        else:
            m = re.search('^WWW-Authenticate:\s(.+)', header)
            if m:
                data['auth'] = '%s' % (m.group(1))
                data['auth-type'] = 1
            else:
                m = re.search('^Proxy-Authenticate:\s(.+)', header)
                if m:
                    data['auth'] = '%s' % (m.group(1))
                    data['auth-type'] = 2

        m = re.search('^CSeq:\s([0-9]+)\s.*', header)
        if m:
            data['cseq'] = '%s' % (m.group(1))

    return data


def parse_digest(buffer):
    headers = buffer.split('\r\n')

    data = dict()

    data['algorithm'] = 'MD5'

    for header in headers:
        m = re.search('username=\"([a-z|A-Z|0-9|-|_]+)\"', header)
        if m:
            data['username'] = '%s' % (m.group(1))
        else:
            data['username'] = ''

        m = re.search('realm=\"([a-z|A-Z|0-9|-|_|\.]+)\"', header)
        if m:
            data['realm'] = '%s' % (m.group(1))
        else:
            data['realm'] = ''

        m = re.search('\snonce=\"([a-z|A-Z|0-9|\/|\+|\=]+)\"', header)
        if m:
            data['nonce'] = '%s' % (m.group(1))
        else:
            data['nonce'] = ''

        m = re.search('uri=\"([a-z|A-Z|0-9|-|_|\.|\:|\;|\=|\@|\#]+)\"', header)
        if m:
            data['uri'] = '%s' % (m.group(1))
        else:
            data['uri'] = ''

        m = re.search('response=\"([a-z|0-9]+)\"', header)
        if m:
            data['response'] = '%s' % (m.group(1))
        else:
            data['response'] = ''

        m = re.search('algorithm=([a-z|A-Z|0-9|-|_]+)', header)
        if m:
            data['algorithm'] = '%s' % (m.group(1))
        else:
            data['algorithm'] = 'MD5'

        m = re.search('cnonce=\"([\w\+\/]+)\"', header)
        if m:
            data['cnonce'] = '%s' % (m.group(1))
        else:
            data['cnonce'] = ''

        m = re.search('nc=\"*([\w\+]+)\"*', header)
        if m:
            data['nc'] = '%s' % (m.group(1))
        else:
            data['nc'] = ''

        m = re.search('qop=\"*([\w\+]+)\"*', header)
        if m:
            data['qop'] = '%s' % (m.group(1))
        else:
            data['qop'] = ''

    return data


def getHash(algorithm, string):
    if algorithm == 'MD5':
        hashfunc = hashlib.md5
    elif algorithm == 'SHA':
        hashfunc = hashlib.sha1
    elif algorithm == 'SHA-256':
        hashfunc = hashlib.sha256
    elif algorithm == 'SHA-512':
        hashfunc = hashlib.sha512

    return hashfunc(string.encode()).hexdigest()


def calculateHash(username, realm, pwd, method, uri, nonce, algorithm, cnonce, nc, qop, verbose, entitybody):
    # HA1 = MD5(username:realm:password)
    # HA2 = MD5(method:digestURI)
    # response = MD5(HA1:nonce:HA2)

    # If the algorithm directive's value is "MD5-sess":
    #   HA1 = MD5(MD5(username:realm:password):nonce:cnonce)
    # If the qop directive's value is "auth-int":
    #   HA2 = MD5(method:digestURI:MD5(entityBody))
    # If the qop directive's value is "auth" or "auth-int":
    #   response = MD5(HA1:nonce:nonceCount:cnonce:qop:HA2)

    a1 = '%s:%s:%s' % (username, realm, pwd)
    a2 = '%s:%s' % (method, uri)

    ha1 = getHash(algorithm, a1)
    if algorithm == 'MD5-sess':
        a1 = '%s:%s:%s' % (ha1, nonce, cnonce)
        ha1 = getHash(algorithm, a1)
    ha2 = getHash(algorithm, a2)
    if (qop == 'auth' or qop == 'auth-int') and cnonce != '':
        if entitybody != '':
            a2 = '%s:%s:%s' % (method, uri, getHash(algorithm, entitybody))
            ha2 = getHash(algorithm, a2)
        b = '%s:%s:%s:%s:%s:%s' % (ha1, nonce, nc, cnonce, qop, ha2)
    else:
        b = '%s:%s:%s' % (ha1, nonce, ha2)
    ret = getHash(algorithm, b)

    if verbose == 1:
        print(WHITE+'Calculating %s hash:' % (algorithm))
        print(WHITE+'A1 hash %s(%s): %s' % (algorithm, a1, ha1))
        print(WHITE+'A2 hash %s(%s): %s' % (algorithm, a2, ha2))
        print(WHITE+'B  hash %s(%s): %s' % (algorithm, b, ret))
        print(WHITE)
    return ret


def fingerprinting(method, msg, headers):
    fp = []

    tag = headers['totag']
    ua = headers['ua']
    type = headers['type']
    code = headers['response_code']

    if method == 'REGISTER':
        if code == '405':
            type = 'Device'
        if code == '401':
            type = 'Server'

    # Device or Unknown
    if type != 'Server':
        m = re.search('^[a-fA-F0-9]{6,8}-[a-fA-F0-9]{2,4}$', tag)
        if m:
            fp.append('Cisco VoIP Gateway')
        m = re.search('^[a-fA-F0-9]{16}i0$', tag)
        if m:
            fp.append('Sipura/Linksys SPA')
        m = re.search('^[0-9]{5,10}$', tag)
        if m:
            fp.append('Grandstream')
            fp.append('Aastra')
        m = re.search('^[0-9]{8,10}$', tag)
        if m:
            fp.append('Fanvil')
        m = re.search('^[a-f0-9]{8}$', tag)
        if m:
            fp.append('Cisco IP Phone')
            fp.append('3CX Phone')
            fp.append('Mitel Border GW')
        m = re.search('^[a-z0-9]{10}$', tag)
        if m:
            fp.append('Panasonic')
        m = re.search('^[a-z]{8}$', tag)
        if m:
            fp.append('Ozeki VoIP SIP SDK')
        m = re.search('^[a-f0-9]{16}$', tag)
        if m:
            fp.append('Grandtream')
        m = re.search('^[a-f0-9]{15}$', tag)
        if m:
            fp.append('Sangoma')
            fp.append('Tandberg')
        m = re.search('^[a-f0-9]{32}$', tag)
        if m:
            fp.append('Comrex')
            fp.append('OXO')

        if tag == '123456':
            fp.append('Alcatel')
        if tag == '':
            fp.append('SNOM')

        hdr = msg.split('\r\n')
        for h in hdr:
            if h.lower().find('x-grandstream-pbx:') == 0:
                fp.append('Grandstream ')

    # Server or Unknown or not found in Device
    if type != 'Device' or fp == []:
        m = re.search('^as[0-9a-f]{8}$', tag)
        if m:
            fp.append('Asterisk PBX')
        m = re.search('^[a-f0-9]{32}.[a-f0-9]{2,8}$', tag)
        if m:
            fp.append('Kamailio SIP Proxy')
        m = re.search('^[a-fA-F0-9]{6,8}-[a-fA-F0-9]{2,4}$', tag)
        if m:
            fp.append('Cisco SIP Gateway')
        m = re.search('^[a-f0-9]{16}$', tag)
        if m:
            fp.append('Tandberg')
        m = re.search('^DL[a-f0-9]{10}$', tag)
        if m:
            fp.append('LifeSize Media Server')
        m = re.search('^[a-zA-Z0-9]{13}$', tag)
        if m:
            fp.append('FreeSWITCH')
        m = re.search('^[a-f0-9]{19}$', tag)
        if m:
            fp.append('SIParator')
        m = re.search('^[0-9]{5,10}$', tag)
        if m:
            fp.append('Panasonic')
        m = re.search('^[0-9A-Z]{32}$', tag)
        if m:
            fp.append('RTC')
        m = re.search('^[0-9a-z]{71}$', tag)
        if m:
            fp.append('Grandstream PBX')
        m = re.search('^1c[0-9]{9,10}$', tag)
        if m:
            fp.append('Mediant SBC')

        if tag == '12345678':
            fp.append('Alcatel')
        if tag == '':
            fp.append('Aastra SIP Server')
            fp.append('Yate SIP Server')

        hdr = msg.split('\r\n')
        for h in hdr:
            if h.lower().find('av-global-session-id:') == 0:
                fp.append('Avaya Session Manager')
            if h.lower().find('www-authenticate:') == 0 and h.lower().find('realm="asterisk"') > 0:
                fp.append('Asterisk PBX')

    if ua != '':
        for f in fp:
            if ua.lower().replace(' ', '').replace('-', '').find(f.lower().replace(' ', '').replace('-', '')) == 0:
                return [f]

    if fp == []:
        return (['Unknown'])

    if len(fp) > 3:
        return ['Too many matches']

    clearfp = []

    for f in fp:
        if f not in clearfp:
            clearfp.append(f)

    return clearfp
