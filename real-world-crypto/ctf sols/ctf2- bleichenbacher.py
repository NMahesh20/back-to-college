# It's like Bleichenbacher's attack just can't stay dead. It keeps on returning

from pwn import *
from collections import namedtuple
# context(arch = 'arm64', os = 'android')
context.encoding = 'utf-8'
context.timeout = .8
context.log_level = 'debug'


# code refered from https://github.com/alexandru-dinu/bleichenbacher/tree/master
# paper: https://archiv.infsec.ethz.ch/education/fs08/secsem/bleichenbacher98.pdf

# r_conn is the remote connection, n is the modulus
global r_conn, n
Interval = namedtuple("Interval", ["lower_bound", "upper_bound"])

# math.ceil and math.floor don't work for large integers
def floor(a, b):
    return a // b


def ceil(a, b):
    return a // b + (a % b > 0)

def PKCS1_decode(encoded):
    """
    Decodes a PKCS1 v1.5 string.
    Remove constant bytes and random pad until arriving at "\x00".
    The rest is the message.
    """

    encoded = encoded[2:]
    idx = encoded.index(b"\x00")

    message = encoded[idx + 1 :]

    return message

def bytes_to_integer(bytes_obj):
    return int.from_bytes(bytes_obj, byteorder="big")


def integer_to_bytes(integer):
    k = integer.bit_length()

    # adjust number of bytes
    bytes_length = k // 8 + (k % 8 > 0)

    bytes_obj = integer.to_bytes(bytes_length, byteorder="big")

    return bytes_obj

def update_intervals(M, s, B):
    """
    After found the s value, compute the new list of intervals
    """

    M_new = []

    for a, b in M:
        r_lower = ceil(a * s - 3 * B + 1, n)
        r_upper = ceil(b * s - 2 * B, n)

        for r in range(r_lower, r_upper):
            lower_bound = max(a, ceil(2 * B + r * n, s))
            upper_bound = min(b, floor(3 * B - 1 + r * n, s))

            interval = Interval(lower_bound, upper_bound)
            M_new = safe_interval_insert(M_new, interval)
    M.clear()

    return M_new

def safe_interval_insert(M_new, interval):
    """
    Deal with interval overlaps when adding a new one to the list
    """

    for i, (a, b) in enumerate(M_new):

        # overlap found, construct the larger interval
        if (b >= interval.lower_bound) and (a <= interval.upper_bound):
            lb = min(a, interval.lower_bound)
            ub = max(b, interval.upper_bound)
            print(f"Overlapping intervals: [{a}, {b}] and [{interval.lower_bound}, {interval.upper_bound}] -> [{lb}, {ub}]")
            M_new[i] = Interval(lb, ub)
            return M_new

    # no overlaps found, just insert the new interval
    M_new.append(interval)
    return M_new

def check_oracle(attempt):
    """
    Check with the oracle if the attempt
    """
    my_hex_string = hex(attempt)[2:]
    if len(my_hex_string) % 2 != 0:
        my_hex_string = my_hex_string.zfill(len(my_hex_string) + 1)
    r_conn.sendlineafter("option:","1")
    r_conn.sendlineafter("c>",my_hex_string)
    if r_conn.recvline_contains("Could decrypt message"):
        return True
    return False

def send_s_to_oracle(s):
    """
    Send the s value to the oracle
    """
    r_conn.sendlineafter("option:","2")
    r_conn.sendlineafter("s1:",str(s))

def send_bounds_to_oracle(lower_bound, upper_bound):
    """
    Send the current bounds to the oracle
    """
    r_conn.sendlineafter("lb>",str(lower_bound))
    r_conn.sendlineafter("ub>",str(upper_bound))

def find_smallest_s(lower_bound, c):
    """
    Find the smallest s >= lower_bound,
    such that (c * s^e) (mod n) decrypts to a PKCS conforming string
    """
    s = lower_bound

    while True:
        attempt = (c * pow(s, e, n)) % n
        if check_oracle(attempt):
            return s
        s += 1

def find_s_in_range(a, b, prev_s, B, c):
    """
    Given the interval [a, b], reduce the search
    only to relevant regions (determined by r)
    and stop when an s value that gives
    a PKCS1 conforming string is found.
    """
    ri = ceil(2 * (b * prev_s - 2 * B), n)

    while True:
        si_lower = ceil(2 * B + ri * n, b)
        si_upper = ceil(3 * B + ri * n, a)

        for si in range(si_lower, si_upper):
            attempt = (c * pow(si, e, n)) % n
            
            if check_oracle(attempt):
                return si

        ri += 1

r_conn = remote('c-bleichenbacher-0.rwc.cs.uni-paderborn.de', 10003)
# EXPLOIT CODE GOES HERE
r_conn.sendlineafter("username>",b'mahesh')
e= int(r_conn.recvline_startswith("e:",drop=True).split(b' ')[1])
n= int(r_conn.recvline_startswith("N:",drop=True).split(b' ')[1])
c= int(r_conn.recvline_startswith("c:",drop=True).split(b' ')[1],16)

k = (n.bit_length() + 7) // 8          # → 128
assert k == 128

B    = 1 << (8 * (k - 2))               # 2**1008
low  = 2 * B                             # 2**1009
high = 3 * B - 1

M = [Interval(2 * B, 3 * B - 1)]

# Implementing Bleichenbacher's attack
s = find_smallest_s(ceil(n, 3 * B), c)
send_s_to_oracle(s)
M = update_intervals(M, s, B)
send_bounds_to_oracle(M[0][0], M[0][1])

while True:
    # Step 2.B.
    if len(M) >= 2:
        print("finding smallest s")
        s = find_smallest_s(s + 1, c)

    # Step 2.C.
    elif len(M) == 1:
        a, b = M[0]

        if a == b:
            print("Found the message!")
            send_s_to_oracle(s)
            send_bounds_to_oracle(a, b)
            decrypted=integer_to_bytes(a % n)
            flag=PKCS1_decode(decrypted)
            print("msg is: ",flag)
            r_conn.close()

        s = find_s_in_range(a, b, s, B, c)

    M = update_intervals(M, s, B)
