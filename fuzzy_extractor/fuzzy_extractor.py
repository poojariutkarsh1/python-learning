import secrets
import hashlib

class FuzzyExtractor:
    def __init__(self, key_len_bits=32, repetition = 8):
        
        self.key_len_bits = key_len_bits
        self.repetition = repetition
        self.response_len_bits = key_len_bits * repetition
        
    def _random_key_bits(self):
        #Generate random key as list of bits
        k_int = secrets.randbits(self.key_len_bits)
        return self._int_to_bits(k_int, self.key_len_bits)
    
    @staticmethod
    def _int_to_bits(value, length):
        return[(value >> i) & 1 for i in range(length)][:: -1]
    
    def _encode(self, key_bits):
        encoded = []
        
        for b in key_bits:
            encoded.extend([b] * self.repetition)
        return encoded
    
    def _decode(self, noisy_encoded_bits):
        key_bits = []
        r = self.repetition
        
        for i in range(self.key_len_bits):
            chunk = noisy_encoded_bits[i* r:(i+1) * r]
            
            ones = sum(chunk)
            key_bits.append(1 if ones> r / 2 else 0)
        return key_bits

def generate_fake_puf_response(length_bits):
    #generate a random 256 bit response for PUF simulation
    value = secrets.randbits(length_bits)
    return [(value >> i) & 1 for i in range(length_bits)][::-1]
        
if __name__ == "__main__":
     fe = FuzzyExtractor()
     print("key length: ", fe.key_len_bits, "bits")
     print("Repetition:", fe.repetition)
     print("PUF response length:", fe.response_len_bits, "bits")
     
     key_bits = fe._random_key_bits()
     
     print("random key:", key_bits)
     print("key length:", len(key_bits))
     
     encoded_key = fe._encode(key_bits)
     print("Encoded key:", encoded_key)
     print("Encoded key length:", len(encoded_key))
     
     decoded_key = fe._decode(encoded_key)
     print("Decoded key:", decoded_key)
     print("Original key:", key_bits)
     print("Keys match: ", decoded_key == key_bits)
     
     original_response = generate_fake_puf_response(fe.response_len_bits)
     print("PUF response:", original_response)
     print("PUF response length:", len(original_response))
     

    
