# ✅ Diagnosis Data Storage - Implementation Complete

## 🎯 What You Asked For

> "tôi muốn lưu cả nội dung này vào file json của chat log"

**Status: ✅ DONE**

## 📋 What's Implemented

### 1. **Automatic Diagnosis Saving**
- When `update_diagnosis` tool is called, ALL data is saved:
  - `score`: Assessment score (e.g., "5")
  - `content`: Detailed analysis of user's state
  - `total_guess`: Final diagnosis/recommendations
  - `timestamp`: When diagnosis was made

### 2. **Updated Chat JSON Format**
```json
{
  "user_id": "user_09423dc1",
  "thread_id": "...",
  "timestamp": "...",
  "message_count": 6,
  "messages": [...],
  "diagnosis": {
    "score": "5",
    "content": "Người dùng cảm thấy mệt mỏi...",
    "total_guess": "Có thể bị trầm cảm nhẹ...",
    "timestamp": "2025-11-12T10:35:20..."
  }
}
```

### 3. **Enhanced View Tool**
- `python view_chats.py` → Shows score in summary
- `python view_chats.py user_ABC` → Shows full diagnosis
- `python view_chats.py --stats` → Shows average score, score range

### 4. **Session Management**
- Diagnosis loads automatically when chat session resumes
- Previous assessments persist across sessions
- Multiple diagnoses can be updated during same session

## 🔧 Code Changes

### Modified Functions in `src/app.py`

#### 1. `save_chat_history()`
```python
def save_chat_history(user_id: str, thread_id: str, message_history: list, diagnosis_data: dict = None):
    # Now saves diagnosis along with messages
    chat_data = {
        "user_id": user_id,
        "thread_id": thread_id,
        "timestamp": datetime.now().isoformat(),
        "message_count": len(message_history),
        "messages": message_history,
        "diagnosis": diagnosis_data or {}  # NEW!
    }
```

#### 2. `load_chat_history()`
```python
def load_chat_history(user_id: str, thread_id: str) -> tuple:
    # Now returns BOTH messages and diagnosis
    return messages, diagnosis  # tuple instead of just list
```

#### 3. `update_diagnosis()` Tool
```python
@tool
def update_diagnosis(...):
    # NEW: Store diagnosis in session
    diagnosis_data = {
        "score": score,
        "content": content,
        "total_guess": total_guess,
        "timestamp": datetime.now().isoformat()
    }
    cl.user_session.set("diagnosis_data", diagnosis_data)  # NEW!
```

#### 4. `on_chat_start()`
```python
# Load BOTH messages and diagnosis
message_history, diagnosis_data = load_chat_history(user_id, thread_id)
cl.user_session.set("diagnosis_data", diagnosis_data)  # NEW!
```

#### 5. `on_message()`
```python
# Save diagnosis along with messages
diagnosis_data = cl.user_session.get("diagnosis_data", {})
save_chat_history(user_id, thread_id, message_history, diagnosis_data)  # Updated!
```

## 📁 Updated Files

| File | Changes |
|------|---------|
| `src/app.py` | Added diagnosis saving/loading, updated tool, session management |
| `view_chats.py` | Added diagnosis display in all view modes |
| `DIAGNOSIS_STORAGE.md` | **NEW** - Complete guide for diagnosis data |
| `CHAT_STORAGE.md` | Reference to new diagnosis feature |

## 🚀 How to Use

### 1. Run the App
```bash
chainlit run src/app.py
```

### 2. Chat Normally
User chats → Agent gathers information

### 3. Agent Calls update_diagnosis
When agent has enough info, it calls the tool:
```
[Tool Call: update_diagnosis]
Score: 5
Content: Người dùng cảm thấy mệt mỏi...
```

### 4. Diagnosis is Auto-Saved
File is saved to: `data/chats/user_XXXXX_thread_ID.json`

### 5. View the Data
```bash
# View with diagnosis
python view_chats.py user_XXXXX_thread_ID

# See statistics including scores
python view_chats.py --stats
```

## 📊 Example Output

### Terminal Log
```
📊 [DIAGNOSIS UPDATE]
   Score: 5
   Content: Người dùng cảm thấy mệt mỏi, khó tập trung...
   Assessment: Có thể bị trầm cảm nhẹ...
✓ Chat history saved: data/chats/user_09423dc1_09423dc1.json
✓ Diagnosis data saved: Score=5
```

### View Chat Output
```
================================================================================
📊 DIAGNOSIS/ASSESSMENT DATA
================================================================================
Score: 5

Content Analysis:
Người dùng cảm thấy mệt mỏi, khó tập trung, học không được nhiều, 
khó đi vào giấc ngủ (khoảng 2 tiếng mới ngủ được). Có cảm giác lo lắng...

Total Assessment:
Có thể bị trầm cảm nhẹ với các biểu hiện mệt mỏi, lo lắng. 
Khuyến nghị tham khảo chuyên gia tâm lý.

Timestamp: 2025-11-12T10:35:20.654321
================================================================================
```

## ✨ Key Features

✅ **Automatic Saving** - No manual steps needed  
✅ **Persistent Storage** - Survives app restart  
✅ **Session Reloading** - Previous diagnosis loads automatically  
✅ **Rich Logging** - All operations logged to `.logs/app.log`  
✅ **Easy Viewing** - Multiple view modes for analysis  
✅ **Statistics** - Track scores and trends  

## 📚 Documentation

- **DIAGNOSIS_STORAGE.md** - Complete guide with examples
- **CHAT_STORAGE.md** - Original chat storage guide (still valid)
- **Inline comments** - Detailed code comments in app.py

## 🎉 Ready to Use!

The system is now fully set up to:
1. Capture diagnosis data during conversations
2. Save it automatically to JSON
3. Load it on session resume
4. Display it for analysis
5. Track trends over time

**Just run the app and start chatting!**

```bash
chainlit run src/app.py
```

Then view any saved diagnosis:
```bash
python view_chats.py --stats
```

Done! 🚀
