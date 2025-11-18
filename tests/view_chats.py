#!/usr/bin/env python3
"""
Utility script to view and analyze saved chat histories.
Usage:
    python view_chats.py                    # List all chats
    python view_chats.py user_abc12345      # View specific user's chats
    python view_chats.py user_abc12345_xyz  # View specific chat
    python view_chats.py --stats            # Show statistics
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

def get_all_chats() -> List[Path]:
    """Get all chat files."""
    chat_dir = Path("data/chats")
    if not chat_dir.exists():
        return []
    return list(chat_dir.glob("*.json"))

def load_chat(filepath: Path) -> Dict:
    """Load a chat file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def print_chat(chat_data: Dict):
    """Pretty print a chat."""
    print(f"\n{'='*80}")
    print(f"User: {chat_data['user_id']}")
    print(f"Thread: {chat_data['thread_id']}")
    print(f"Timestamp: {chat_data['timestamp']}")
    print(f"Total Messages: {chat_data['message_count']}")
    print(f"{'='*80}\n")
    
    for i, msg in enumerate(chat_data['messages'], 1):
        role = "👤 USER" if msg['role'] == 'user' else "🤖 ASSISTANT"
        print(f"{i}. {role}")
        print(f"   {msg['content']}\n")

def list_all_chats():
    """List all chat files."""
    chats = get_all_chats()
    
    if not chats:
        print("❌ No chats found in data/chats/")
        return
    
    print(f"\n📊 Found {len(chats)} chat file(s):\n")
    
    for chat_file in sorted(chats):
        chat_data = load_chat(chat_file)
        print(f"✓ {chat_file.name}")
        print(f"  User: {chat_data['user_id']}")
        print(f"  Messages: {chat_data['message_count']}")
        print(f"  Time: {chat_data['timestamp']}")
        print()

def view_user_chats(user_id: str):
    """View all chats for a specific user."""
    chats = get_all_chats()
    # Match user_id at start of filename
    user_chats = [c for c in chats if c.name.startswith(user_id)]
    
    if not user_chats:
        print(f"❌ No chats found for user: {user_id}")
        return
    
    print(f"\n📁 Found {len(user_chats)} chat(s) for {user_id}:\n")
    
    for chat_file in sorted(user_chats):
        chat_data = load_chat(chat_file)
        print_chat(chat_data)

def view_specific_chat(filename: str):
    """View a specific chat file."""
    chat_file = Path("data/chats") / f"{filename}.json"
    
    if not chat_file.exists():
        # Try without .json extension
        chat_file = Path("data/chats") / filename
    
    if not chat_file.exists():
        print(f"❌ Chat file not found: {filename}")
        return
    
    chat_data = load_chat(chat_file)
    print_chat(chat_data)

def show_statistics():
    """Show statistics about all chats."""
    chats = get_all_chats()
    
    if not chats:
        print("❌ No chats found")
        return
    
    total_messages = 0
    total_users = set()
    
    for chat_file in chats:
        chat_data = load_chat(chat_file)
        total_messages += chat_data['message_count']
        total_users.add(chat_data['user_id'])
    
    print(f"\n📈 Chat Statistics")
    print(f"{'='*40}")
    print(f"Total Chat Sessions: {len(chats)}")
    print(f"Unique Users: {len(total_users)}")
    print(f"Total Messages: {total_messages}")
    print(f"Avg Messages per Chat: {total_messages / len(chats):.1f}")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - list all chats
        list_all_chats()
    elif sys.argv[1] == "--stats":
        # Show statistics
        show_statistics()
    else:
        arg = sys.argv[1]
        # Count underscores: user_XXXX_threadID has 2+ underscores
        underscore_count = arg.count("_")
        
        if underscore_count >= 2:
            # Specific chat (e.g., user_abc12345_xyz or longer)
            view_specific_chat(arg)
        else:
            # User ID (e.g., user_abc12345)
            view_user_chats(arg)
