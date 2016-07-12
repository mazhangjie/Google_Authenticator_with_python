#!/usr/bin/python
"""
   2016_03_01
"""
import sys
import hmac
import base64
import struct
import hashlib
import time
import datetime
import getopt
import qrcode
import random as _random

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

def random_base32(length=16, random=_random.SystemRandom(),
                  chars=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')):
    return ''.join(
        random.choice(chars)
        for _ in range(length)
    )
    
def HOTP(secret, scaler):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", scaler)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7FFFFFFF) % 1000000
    return h

def TOTP(secret, Time_Span = 30):
    scaler = int(time.mktime(datetime.datetime.now().timetuple()))//Time_Span
    return HOTP(secret, scaler)
    
def build_uri(secret, name, Ishotp=None):
    Is_HOTP = (Ishotp is not None)
    if Is_HOTP:
        otp_type = 'hotp' 
    else:
        otp_type = 'totp'
    base = 'otpauth://%s/' % otp_type
    uri = '%(base)s%(name)s?secret=%(secret)s' % {
        'name': quote(name, safe='@'),
        'secret': secret,
        'base': base,
    }
    if Is_HOTP:
        uri += '&counter=%s' % Ishotp
    return uri

    
#ouput QRCODE with time-base key
def QR_tim(key, name):
    qr = qrcode.main.QRCode()
    url_time = build_uri(key, name)
    qr.add_data(url_time)
    qr.make()
    save_qr_time = qr.make_image()
    save_qr_time.save('/root/%s_time.png' % name)
    print "New QRcode With Time-base Output:\n/root/%s_time.png" % name
    
#output QRCODE with couter-base key
def QR_cou(key, name, scaler):
    qr = qrcode.main.QRCode()
    url_counter = build_uri(key, name, Ishotp = scaler)
    qr.add_data(url_counter)
    qr.make()
    save_qr_counter =  qr.make_image()
    save_qr_counter.save("/root/%s_counter.png" % name)
    print "New QRcode With Counter-base Output:\n/root/%s_counter.png" % name

def usage():
    print("Usage:%s [g|-o|-c|-t|-q|-k|-s|-n|-h]    \n\n    -g         GENERATEKEY, Output New Key\n    -o         OTPKEY: -k GENERATEKEY -o\n    -c         COUNTERKEY:-k GENERATEKEY -s SCALER -c\n    -t         QRCODE With Time-Base Key: -k GENERATEKEY -n NAME -t\n    -q         QRCODE With Counter-Base Key: -k GENERATEKEY -s SCALER -n NAME -q\n    -h,--help  HELP\n" % sys.argv[0])
    
if __name__ == '__main__':

    name = ""
    key = ""
    scaler = ""
    
    try :
        opts, args = getopt.getopt(sys.argv[1:], "gk:os:cn:tqh", ["help"])
        if not opts :
            usage()
        for op, value in opts:
            if op in ("-h", "--help"):
                usage()
            elif op == "-g":
                print random_base32()
            elif op == "-k":
                key = value
            elif op == "-o":
                if key == "":
                    print "Please Input Key!"
                else:
                    totp = TOTP(key)
                    print totp
            elif op == "-s":
                scaler = value
            elif op == "-c":
                if key == "" or scaler == "":
                    print "Please Check Parameter!"
                else:
                    hotp = HOTP(key, int(scaler))
                    print "%s %s" % (scaler, hotp)
            elif op == "-n":
                name = value
            elif op == "-t":
                if name == "" or key == "":
                    print "Please Check Parameter!"
                else:
                    QR_tim(key, name)
            elif op == "-q":
                if name == "" or key == "" or scaler == "":
                    print "Please Check Parameter!"
                else:
                    QR_cou(key, name, int(scaler))
        
        
    except getopt.GetoptError:
        print "Parameter Error, Please check!"
        usage()
        sys.exit()








