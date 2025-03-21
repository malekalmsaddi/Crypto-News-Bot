import sys
from database import add_chat, get_all_chats, init_db

def add_test_chat_to_database(chat_id=None, chat_title=None, chat_type=None):
    """
    Add a test chat to the database.
    
    Usage:
    python add_test_chat.py CHAT_ID "CHAT_TITLE" CHAT_TYPE
    
    Example:
    python add_test_chat.py 123456789 "My Test Group" group
    python add_test_chat.py -100987654321 "Crypto News Test" supergroup
    python add_test_chat.py 123456789 "Personal Chat" private
    """
    # Ensure database is initialized
    init_db()
    
    # Check if arguments were provided
    if not chat_id and len(sys.argv) >= 4:
        chat_id = sys.argv[1]
        chat_title = sys.argv[2]
        chat_type = sys.argv[3]
    
    # Validate input
    if not chat_id or not chat_title or not chat_type:
        print("\n⚠️ Please provide all required information:")
        print("Usage: python add_test_chat.py CHAT_ID \"CHAT_TITLE\" CHAT_TYPE")
        print("\nExample:")
        print("python add_test_chat.py 123456789 \"My Test Group\" group")
        return False
    
    # Add the chat to the database
    try:
        add_chat(chat_id, chat_title, chat_type)
        print(f"\n✅ Successfully added chat to database:")
        print(f"ID: {chat_id}")
        print(f"Title: {chat_title}")
        print(f"Type: {chat_type}")
        
        # Display all chats in the database
        chats = get_all_chats()
        print(f"\nTotal chats in database: {len(chats)}")
        
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat['chat_title']} (ID: {chat['chat_id']}, Type: {chat['chat_type']})")
        
        return True
    except Exception as e:
        print(f"\n❌ Error adding chat to database: {str(e)}")
        return False

if __name__ == "__main__":
    print("📋 Add Test Chat - أخبار الكريبتو من إنفترون داو")
    print("-----------------------------------------------")
    
    add_test_chat_to_database()