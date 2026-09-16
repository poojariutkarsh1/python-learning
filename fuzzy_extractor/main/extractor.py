"""
Fuzzy extractor for 64-bit Arbiter PUF CRP data.

Expected CSV format (one row per challenge-response pair):
    c0,c1,c2,c3,c4,c5,c6,c7,response
where c0..c7 are integers 0-255 (one byte each, together forming a
64-bit challenge) and response is a single bit (0 or 1).

This uses the standard "code-offset construction":
    Gen(w)          -> key, helper_data      (enrollment)
    Rep(w', helper) -> key or None           (reconstruction)

helper_data = repetition_encode(random_key) XOR w
At reconstruction time:
    noisy_codeword = w' XOR helper_data
                    = repetition_encode(random_key) XOR (w XOR w')
So if w and w' differ in only a few bits (measurement noise), the
majority-vote decoder can still recover the original key.
"""

import csv
import hashlib
import hmac
import secrets
import time


# --------------------------------------------------------------------------
# CRP loading / challenge handling
# --------------------------------------------------------------------------

def load_crp_csv(path):
    """
    Load a PUF CRP CSV.

    Returns a dict: {challenge_tuple (8 ints, 0-255 each): response_bit}
    Using a dict (keyed by the raw challenge) lets us match up rows
    between two different instance files even if the row order differs.
    """
    crps = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            challenge = tuple(int(x) for x in row[:8])
            response = int(row[8])
            crps[challenge] = response
    return crps


def challenge_to_bits(challenge_bytes):
    """Convert 8 bytes (0-255 each) into a 64-bit list, MSB first per byte."""
    bits = []
    for byte_val in challenge_bytes:
        bits.extend([(byte_val >> i) & 1 for i in range(7, -1, -1)])
    return bits


def build_response_vector(crps, challenge_order):
    """Pull response bits, in a fixed challenge order, out of a CRP dict."""
    return [crps[c] for c in challenge_order]


def hamming_distance(bits_a, bits_b):
    return sum(a != b for a, b in zip(bits_a, bits_b))


# --------------------------------------------------------------------------
# Fuzzy extractor
# --------------------------------------------------------------------------

class FuzzyExtractor:
    def __init__(self, key_len_bits=32, repetition=8):
        self.key_len_bits = key_len_bits
        self.repetition = repetition
        self.response_len_bits = key_len_bits * repetition  # e.g. 256

    # ---- key helpers ----
    def _random_key_bits(self):
        k_int = secrets.randbits(self.key_len_bits)
        return self._int_to_bits(k_int, self.key_len_bits)

    @staticmethod
    def _int_to_bits(value, length):
        return [(value >> i) & 1 for i in range(length)][::-1]

    @staticmethod
    def _bits_to_bytes(bits):
        value = 0
        for b in bits:
            value = (value << 1) | b
        return value.to_bytes((len(bits) + 7) // 8, "big")

    # ---- repetition code ----
    def _encode(self, key_bits):
        encoded = []
        for b in key_bits:
            encoded.extend([b] * self.repetition)
        return encoded

    def _decode(self, noisy_encoded_bits):
        key_bits = []
        r = self.repetition
        for i in range(self.key_len_bits):
            chunk = noisy_encoded_bits[i * r:(i + 1) * r]
            ones = sum(chunk)
            key_bits.append(1 if ones > r / 2 else 0)
        return key_bits

    @staticmethod
    def _xor_bits(a, b):
        return [x ^ y for x, y in zip(a, b)]

    # ---- Gen / Rep ----
    def gen(self, response_bits):
        """
        Enrollment. response_bits = raw PUF response bits for a fixed,
        agreed-upon set of challenges (length must be response_len_bits).
        Returns (key_bits, helper_data). helper_data is public / storable.
        """
        if len(response_bits) != self.response_len_bits:
            raise ValueError(
                f"Expected {self.response_len_bits} response bits, "
                f"got {len(response_bits)}"
            )

        key_bits = self._random_key_bits()
        codeword = self._encode(key_bits)
        helper_mask = self._xor_bits(codeword, response_bits)

        key_hash = hashlib.sha256(self._bits_to_bytes(key_bits)).hexdigest()
        helper_data = {"mask": helper_mask, "key_hash": key_hash}
        return key_bits, helper_data

    def rep(self, noisy_response_bits, helper_data):
        """
        Reconstruction. noisy_response_bits = a later PUF measurement over
        the SAME challenge set used in gen(). Returns the recovered key
        if it matches the enrolled key's hash, else None.
        """
        if len(noisy_response_bits) != self.response_len_bits:
            raise ValueError(
                f"Expected {self.response_len_bits} response bits, "
                f"got {len(noisy_response_bits)}"
            )

        noisy_codeword = self._xor_bits(noisy_response_bits, helper_data["mask"])
        recovered_key_bits = self._decode(noisy_codeword)

        recovered_hash = hashlib.sha256(
            self._bits_to_bytes(recovered_key_bits)
        ).hexdigest()

        if hmac.compare_digest(recovered_hash, helper_data["key_hash"]):
            return recovered_key_bits
        return None


# --------------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------------

if __name__ == "__main__":
    fe = FuzzyExtractor(key_len_bits=32, repetition=8)
    N = fe.response_len_bits  # 256 challenges needed per Gen/Rep call
    print(f"Key length: {fe.key_len_bits} bits, repetition: {fe.repetition}")
    print(f"Challenges needed per Gen/Rep call: {N}\n")

    # ---- Load instance 1 (enrollment device) ----
    crps_1 = load_crp_csv("CRP_10000_Br_1.csv")
    enrolled_challenges = list(crps_1.keys())[:N]  # fixed, public challenge set
    w_enroll = build_response_vector(crps_1, enrolled_challenges)

    start_gen = time.perf_counter()
    key, helper = fe.gen(w_enroll)
    end_gen = time.perf_counter()

    print("Enrolled key:", key)
    print("Private Key:")
    print("".join(map(str, key)))

    print("\nPublic Helper Data:")
    print("Mask:")
    print("".join(map(str, helper["mask"])))
    print("Key Hash:")
    print(helper["key_hash"])

    print(f"\nGen() time taken: {(end_gen - start_gen) * 1000:.6f} ms")

    # ---- Simulate realistic measurement noise on the SAME instance ----
    noisy_w = w_enroll.copy()
    flip_count = max(1, int(0.04 * N))  # ~4% bit-flip rate, typical PUF noise
    flip_positions = secrets.SystemRandom().sample(range(N), flip_count)
    for pos in flip_positions:
        noisy_w[pos] ^= 1

    start_rep_noise = time.perf_counter()
    recovered_noisy = fe.rep(noisy_w, helper)
    end_rep_noise = time.perf_counter()

    print(f"\n[Noise test] Flipped {flip_count}/{N} bits (same instance):")
    print("  Match:", recovered_noisy == key)
    print(f"  Rep() time taken: {(end_rep_noise - start_rep_noise) * 1000:.6f} ms")

    # ---- Cross-instance test: needs the second PUF's CSV ----
    try:
        crps_2 = load_crp_csv("CRP_10000_Br_2.csv")
        common = [c for c in enrolled_challenges if c in crps_2]
        if len(common) < N:
            print(f"\n(Only {len(common)} matching challenges found in "
                  f"instance 2 - need {N}. Skipping cross-instance test.)")
        else:
            common = common[:N]
            w1 = build_response_vector(crps_1, common)
            w2 = build_response_vector(crps_2, common)
            hd = hamming_distance(w1, w2)
            print(f"\n[Cross-instance] Hamming distance: {hd}/{N} bits "
                  f"({100 * hd / N:.1f}%)")

            key1, helper1 = fe.gen(w1)
            recovered_cross = fe.rep(w2, helper1)
            print("  Recovered instance-2 response with instance-1 helper data:")
            print("  Match:", recovered_cross == key1)
    except FileNotFoundError:
        print("\n(CRP_10000_Br_2.csv not found - skipping cross-instance test. "
              "Add the second instance's CSV to compare the two PUFs.)")
