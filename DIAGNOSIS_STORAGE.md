# Diagnosis Data Storage Guide

## Overview

Chat history now includes **diagnosis/assessment data** that gets saved automatically when the `update_diagnosis` tool is called by the agent.

## 📊 What Gets Saved

When the agent calls `update_diagnosis()`, the following data is stored:

```json
{
  "user_id": "user_abc12345",
  "thread_id": "abc12345-def67890-...",
  "timestamp": "2025-11-12T10:30:45.123456",
  "message_count": 6,
  "messages": [...],
  "diagnosis": {
    "score": "5",
    "content": "Người dùng cảm thấy mệt mỏi, khó tập trung, học không được nhiều, khó đi vào giấc ngủ (khoảng 2 tiếng mới ngủ được). Có cảm giác lo lắng...",
    "total_guess": "Có thể bị trầm cảm nhẹ với các biểu hiện mệt mỏi, lo lắng...",
    "timestamp": "2025-11-12T10:35:20.654321"
  }
}
```

## 🔄 How It Works

### Step 1: Agent Calls Tool
```python
[Tool Call: update_diagnosis] 
Score: 5
Content: Người dùng cảm thấy mệt mỏi...
```

### Step 2: Tool Stores in Session
```python
diagnosis_data = {
    "score": "5",
    "content": "...",
    "total_guess": "...",
    "timestamp": datetime.now().isoformat()
}
cl.user_session.set("diagnosis_data", diagnosis_data)
```

### Step 3: Auto-Save to File
```python
# After each message
save_chat_history(user_id, thread_id, message_history, diagnosis_data)
```

Result: `data/chats/user_abc12345_thread_id.json` is updated with diagnosis

### Step 4: Reload on Next Session
```python
message_history, diagnosis_data = load_chat_history(user_id, thread_id)
# Both messages AND diagnosis are restored
```

## 📖 JSON File Structure

```json
{
  "user_id": "user_09423dc1",
  "thread_id": "09423dc1-a2d3-465e-b9d0-3d66f6334986",
  "timestamp": "2025-11-12T10:30:45.123456",
  "message_count": 4,
  "messages": [
    {
      "role": "user",
      "content": "tôi cảm thấy mệt mỏi"
    },
    {
      "role": "assistant",
      "content": "Bạn có thể chia sẻ thêm?"
    }
  ],
  "diagnosis": {
    "score": "5",
    "content": "Detailed assessment of user's mental state...",
    "total_guess": "Preliminary diagnosis/recommendations...",
    "timestamp": "2025-11-12T10:35:20.654321"
  }
}
```

## 🔍 How to View Diagnosis Data

### Option 1: View All Chats (Shows Diagnosis Summary)
```bash
python view_chats.py
```

Output:
```
📊 Found 2 chat file(s):

✓ user_09423dc1_09423dc1-a2d3-465e-b9d0-3d66f6334986.json
  User: user_09423dc1
  Messages: 6
  Time: 2025-11-12T10:30:45.123456
  Score: 5
```

### Option 2: View Specific User's Chats
```bash
python view_chats.py user_09423dc1
```

Shows all conversations for that user **with full diagnosis data**

### Option 3: View Specific Chat (Full Details)
```bash
python view_chats.py user_09423dc1_09423dc1
```

Output:
```
================================================================================
User: user_09423dc1
Thread: 09423dc1-a2d3-465e-b9d0-3d66f6334986
Timestamp: 2025-11-12T10:30:45.123456
Total Messages: 6
================================================================================

1. 👤 USER
   chào bạn

2. 🤖 ASSISTANT
   Chào bạn, tôi có thể giúp gì?

[... more messages ...]

================================================================================
📊 DIAGNOSIS/ASSESSMENT DATA
================================================================================
Score: 5

Content Analysis:
Người dùng cảm thấy mệt mỏi, khó tập trung, học không được nhiều, khó đi vào giấc ngủ (khoảng 2 tiếng mới ngủ được). Có cảm giác lo lắng, đặc biệt vào ban đêm, và cảm giác "không muốn làm gì" vào ban ngày. Các triệu chứng này có thể ảnh hưởng đến sinh hoạt hàng ngày.

Total Assessment:
Có thể bị trầm cảm nhẹ với các biểu hiện mệt mỏi, lo lắng. Khuyến nghị tham khảo chuyên gia tâm lý.

Timestamp: 2025-11-12T10:35:20.654321
================================================================================
```

### Option 4: View Statistics (Including Score Data)
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
Chats with Diagnosis: 3
Average Score: 4.5
Score Range: 2 - 7
========================================
```

## 💾 File Updates

### First Message → No Diagnosis Yet
```json
{
  "user_id": "user_test",
  "thread_id": "thread_123",
  "message_count": 1,
  "messages": [{"role": "user", "content": "hi"}],
  "diagnosis": {}  // Empty object
}
```

### After Agent Calls update_diagnosis → Diagnosis Saved
```json
{
  "user_id": "user_test",
  "thread_id": "thread_123",
  "message_count": 4,
  "messages": [...],
  "diagnosis": {
    "score": "5",
    "content": "Assessment...",
    "total_guess": "Diagnosis...",
    "timestamp": "2025-11-12T..."
  }
}
```

## 🔧 Code Examples

### In app.py
```python
# When update_diagnosis tool is called:
diagnosis_data = {
    "score": score,
    "content": content,
    "total_guess": total_guess,
    "timestamp": datetime.now().isoformat()
}
cl.user_session.set("diagnosis_data", diagnosis_data)

# When saving chat:
diagnosis_data = cl.user_session.get("diagnosis_data", {})
save_chat_history(user_id, thread_id, message_history, diagnosis_data)

# When loading chat:
message_history, diagnosis_data = load_chat_history(user_id, thread_id)
cl.user_session.set("diagnosis_data", diagnosis_data)
```

## 📝 Logs

Diagnosis saving is logged to `.logs/app.log`:

```
2025-11-12 10:35:20,456 - __main__ - INFO - 📊 [DIAGNOSIS UPDATE]
2025-11-12 10:35:20,457 - __main__ - INFO -    Score: 5
2025-11-12 10:35:20,458 - __main__ - INFO -    Content: Người dùng cảm thấy mệt mỏi...
2025-11-12 10:35:20,459 - __main__ - INFO - ✓ Chat history saved: data/chats/user_09423dc1_09423dc1.json
2025-11-12 10:35:20,460 - __main__ - INFO - ✓ Diagnosis data saved: Score=5
```

## 🎯 Use Cases

### Track Mental Health Progress
```bash
# View scores over time
python view_chats.py --stats

# Get average score for specific user
grep -r "user_abc12345" data/chats/ | grep "score"
```

### Export for Analysis
```bash
# Convert all diagnosis data to CSV
python3 -c "
import json
from pathlib import Path
import csv

with open('diagnosis_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['User', 'Thread', 'Score', 'Timestamp'])
    
    for chat_file in Path('data/chats').glob('*.json'):
        with open(chat_file) as cf:
            data = json.load(cf)
            diag = data.get('diagnosis', {})
            if diag:
                writer.writerow([
                    data['user_id'],
                    data['thread_id'],
                    diag.get('score'),
                    diag.get('timestamp')
                ])
"
```

### Backup Diagnosis Data
```bash
# Backup only diagnosis files
mkdir -p backups
for file in data/chats/*.json; do
  cp \"\$file\" \"backups/\$(basename \$file)\"
done
```

## ✅ Verification

After running the app and triggering diagnosis:

```bash
# Check if diagnosis was saved
python view_chats.py user_XXXXX

# Should show full diagnosis data in output
# Look for "DIAGNOSIS/ASSESSMENT DATA" section
```

Diagnosis data is now **fully integrated** with chat history! 🎉
