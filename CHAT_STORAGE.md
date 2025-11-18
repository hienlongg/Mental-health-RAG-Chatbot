# Chat History Storage Guide

## Overview

Chat content is now automatically saved to disk in **JSON format** at:
```
data/chats/user_xxxxx_thread_id.json
```

Each chat session creates a separate JSON file containing:
- User ID
- Thread ID
- Timestamp
- Message count
- Full conversation (user + assistant messages)

## 📁 Storage Location

```
data/chats/
├── user_abc12345_5f6g7h8i.json    # Chat 1
├── user_abc12345_9j0k1l2m.json    # Chat 2
└── user_def67890_3n4o5p6q.json    # Different user's chat
```

## 🔍 How to View Chats

### Option 1: View All Chats
```bash
python view_chats.py
```

Output:
```
📊 Found 5 chat file(s):

✓ user_abc12345_5f6g7h8i.json
  User: user_abc12345
  Messages: 6
  Time: 2025-11-12T10:30:45.123456

✓ user_abc12345_9j0k1l2m.json
  User: user_abc12345
  Messages: 4
  Time: 2025-11-12T11:15:30.654321
```

### Option 2: View Specific User's Chats
```bash
python view_chats.py user_abc12345
```

Shows all chat sessions for that user with full conversation.

### Option 3: View Specific Chat
```bash
python view_chats.py user_abc12345_5f6g7h8i
```

Displays the full conversation:
```
================================================================================
User: user_abc12345
Thread: 5f6g7h8i-...
Timestamp: 2025-11-12T10:30:45.123456
Total Messages: 6
================================================================================

1. 👤 USER
   chào bạn

2. 🤖 ASSISTANT
   Chào bạn, tôi có thể giúp gì cho bạn hôm nay?

3. 👤 USER
   tôi cảm thấy mệt mỏi, không muốn làm gì nữa

4. 🤖 ASSISTANT
   Tôi hiểu rằng bạn đang cảm thấy mệt mỏi...
```

### Option 4: View Statistics
```bash
python view_chats.py --stats
```

Output:
```
📈 Chat Statistics
========================================
Total Chat Sessions: 5
Unique Users: 2
Total Messages: 28
Avg Messages per Chat: 5.6
========================================
```

## 📊 JSON File Format

Example chat file: `data/chats/user_abc12345_5f6g7h8i.json`

```json
{
  "user_id": "user_abc12345",
  "thread_id": "5f6g7h8i-a1b2-c3d4-e5f6-g7h8i9j0k1l",
  "timestamp": "2025-11-12T10:30:45.123456",
  "message_count": 6,
  "messages": [
    {
      "role": "user",
      "content": "chào bạn"
    },
    {
      "role": "assistant",
      "content": "Chào bạn, tôi có thể giúp gì cho bạn hôm nay?"
    },
    {
      "role": "user",
      "content": "tôi cảm thấy mệt mỏi, không muốn làm gì nữa"
    },
    {
      "role": "assistant",
      "content": "Tôi hiểu rằng bạn đang cảm thấy mệt mỏi..."
    }
  ]
}
```

## 🔄 How It Works

### On New Chat Session:
1. User opens the chat
2. System generates `user_id` and `thread_id`
3. System checks if chat history exists
4. If exists → loads previous conversation
5. If not → starts new empty history

### On Each Message:
1. User message is added to history
2. Agent processes the message
3. Assistant response is added to history
4. **Chat is saved to disk** (`data/chats/user_id_thread_id.json`)

### On Chat End:
1. Final chat file remains saved on disk
2. User can reload same session later with same thread_id

## 📝 Logs

Chat operations are logged to `.logs/app.log`:

```
2025-11-12 10:30:45,123 - __main__ - INFO - ✓ Chat history saved: data/chats/user_abc12345_5f6g7h8i.json
2025-11-12 10:35:20,456 - __main__ - INFO - ✓ Chat history loaded: data/chats/user_abc12345_5f6g7h8i.json
```

## 📂 File Organization

```
RAG-agent/
├── data/
│   ├── chats/              # 📁 Chat histories (NEW)
│   │   └── *.json
│   ├── documents/          # PDF documents
│   └── embeddings/         # Vector store
├── .logs/                  # Application logs
├── src/
│   └── app.py
├── view_chats.py          # 🆕 Chat viewer utility
└── ...
```

## 🛠️ Tips

### Backup Chats
```bash
# Backup all chats
cp -r data/chats data/chats.backup

# Archive chats
tar -czf chats_backup_$(date +%Y%m%d).tar.gz data/chats
```

### Search in Chats
```bash
# Find chats containing specific word
grep -r "anxiety" data/chats/ | head -10

# Count messages for a user
grep -r "user_abc12345" data/chats/ | wc -l
```

### Export to CSV (Optional)
```bash
# Convert JSON chats to CSV format
python -c "
import json
from pathlib import Path
import csv

chats = Path('data/chats').glob('*.json')
with open('chats_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['User ID', 'Thread ID', 'Role', 'Message', 'Timestamp'])
    for chat_file in chats:
        with open(chat_file) as cf:
            data = json.load(cf)
            for msg in data['messages']:
                writer.writerow([
                    data['user_id'],
                    data['thread_id'],
                    msg['role'],
                    msg['content'],
                    data['timestamp']
                ])
"
```

## ✅ Verification

After running the app, you should see:

```bash
$ ls -la data/chats/
total 12
-rw-r--r-- user_09423dc1_09423dc1.json

$ python view_chats.py
📊 Found 1 chat file(s):

✓ user_09423dc1_09423dc1.json
  User: user_09423dc1
  Messages: 4
  Time: 2025-11-12T10:30:45.123456
```

Chat content is now **persistent** and saved between sessions! 🎉
