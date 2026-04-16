import json
import os
import datetime
from config import JSON_FILE, CACHE_FILE

def load_cache():
    if not os.path.exists(CACHE_FILE): return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_to_cache(query, answer, source):
    cache = load_cache()
    cache[query.lower().strip()] = {"answer": answer, "source": source}
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def load_db():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "chats" not in data: data["chats"] = {}
        if "pinned" not in data: data["pinned"] = []
        return data
    except:
        data = {"chats": {}, "pinned": []}
        save_db(data)
        return data

def save_db(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_message(cid, title, role, content, timestamp=None):
    if not timestamp:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = load_db()
    if cid not in db["chats"]:
        db["chats"][cid] = {"title": title, "messages": [], "created_at": timestamp}
    db["chats"][cid]["messages"].append({"role": role, "content": content, "timestamp": timestamp})
    save_db(db)

def delete_chat(cid):
    db = load_db()
    if cid in db["chats"]: del db["chats"][cid]
    if cid in db["pinned"]: db["pinned"].remove(cid)
    save_db(db)

def pin_chat(cid):
    db = load_db()
    if cid not in db["pinned"]: db["pinned"].append(cid)
    save_db(db)

def unpin_chat(cid):
    db = load_db()
    if cid in db["pinned"]: db["pinned"].remove(cid)
    save_db(db)