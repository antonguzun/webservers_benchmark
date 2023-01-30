# python redis_data_generator.py | redis-cli --pipe -p 26379
import json
import uuid

def gen_str(len: int):
    return uuid.uuid4().hex[:len]

for i in range(10000):
    user_id = i + 1
    name = f'user_{user_id}'
    value = {"user_id": user_id, "username": f"user{user_id}_{gen_str(6)}", 
        "email": f"{gen_str(13)}@gmail.com", "created_at": "2023-01-30T12:38:22.271595+00:00", 
        "updated_at": "2023-01-30T12:38:22.271595+00:00", "is_archived": False}
    print(f"SET {name} '{json.dumps(value)}'")
