import secrets



def generate_fake_puf_response(length):
    response = []
    
    for _ in range(length):
        bit = secrets.randbelow(2)
        response.append(bit)
        
    return response

response = generate_fake_puf_response(20)

print(response)
    
