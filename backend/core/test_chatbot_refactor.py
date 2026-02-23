"""
Test script for refactored chatbot functionality
Tests the new AI-based item matching approach
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lost_found_project.settings')
django.setup()

from core.models import Item, Tag
from core.ai_service import ChatBotService
from django.contrib.auth import get_user_model

User = get_user_model()

def test_refactored_chatbot():
    """Test the refactored chatbot with new approach"""
    
    print("\n" + "="*70)
    print("TESTING REFACTORED CHATBOT - New AI Matching Approach")
    print("="*70)
    
    # Step 1: Check if we have items in database
    print("\nStep 1: Checking database for items...")
    all_items = Item.objects.filter(status='ACTIVE')
    print(f"Found {all_items.count()} active items in database")
    
    if all_items.count() == 0:
        print("\n⚠️  No items in database. Creating sample items for testing...")
        create_sample_items()
        all_items = Item.objects.filter(status='ACTIVE')
        print(f"Created sample items. Now have {all_items.count()} items")
    
    # Step 2: Prepare items data for AI
    print("\nStep 2: Preparing items data for AI...")
    items_data = []
    for item in all_items:
        items_data.append({
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'type': item.type,
            'tags': [tag.name for tag in item.tags.all()],
            'location_description': f"Lat: {item.latitude}, Lon: {item.longitude}"
        })
    
    print(f"Prepared {len(items_data)} items")
    print("\nSample items:")
    for i, item in enumerate(items_data[:3], 1):
        print(f"  {i}. [{item['type']}] {item['title']}")
    
    # Step 3: Test with a description
    print("\nStep 3: Testing AI matching with user description...")
    test_descriptions = [
        "I lost my iPhone near the library",
        "Found a blue wallet in the cafeteria",
        "گم کردم کلید اتاقم را"  # Persian: "I lost my room key"
    ]
    
    for idx, description in enumerate(test_descriptions, 1):
        print(f"\n--- Test Case {idx} ---")
        print(f"Description: {description}")
        
        try:
            # Initialize AI service
            chatbot_service = ChatBotService()
            
            # Find related items
            result = chatbot_service.find_related_items(description, items_data)
            
            if result['success']:
                related_ids = result['data']['related_item_ids']
                explanation = result['data'].get('explanation', '')
                
                print(f"✅ Success!")
                print(f"Found {len(related_ids)} related items")
                print(f"Explanation: {explanation}")
                
                if related_ids:
                    print("\nRelated items:")
                    for item_id in related_ids[:5]:  # Show first 5
                        item = all_items.filter(id=item_id).first()
                        if item:
                            print(f"  - [{item.type}] {item.title}")
                else:
                    print("No matching items found")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)


def create_sample_items():
    """Create sample items for testing"""
    user = User.objects.first()
    if not user:
        print("No users found in database. Please create a user first.")
        return
    
    # Create tags
    tags_data = ['Electronics', 'Keys', 'Wallet', 'Books', 'Other']
    tags = {}
    for tag_name in tags_data:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        tags[tag_name] = tag
    
    # Sample items
    sample_items = [
        {
            'title': 'iPhone 13 Pro - Blue',
            'description': 'Blue iPhone 13 Pro found near the library. Has a cracked screen.',
            'type': 'FOUND',
            'latitude': 35.7219,
            'longitude': 51.3347,
            'tags': ['Electronics']
        },
        {
            'title': 'Black Wallet',
            'description': 'Lost black leather wallet in cafeteria. Contains ID cards.',
            'type': 'LOST',
            'latitude': 35.7220,
            'longitude': 51.3350,
            'tags': ['Wallet']
        },
        {
            'title': 'Room Keys',
            'description': 'Found a set of keys near the gym. Has a blue keychain.',
            'type': 'FOUND',
            'latitude': 35.7225,
            'longitude': 51.3355,
            'tags': ['Keys']
        },
        {
            'title': 'Blue Backpack',
            'description': 'Lost blue backpack with laptop inside near engineering building.',
            'type': 'LOST',
            'latitude': 35.7230,
            'longitude': 51.3360,
            'tags': ['Other']
        }
    ]
    
    for item_data in sample_items:
        item_tags = item_data.pop('tags')
        item = Item.objects.create(
            author=user,
            **item_data
        )
        for tag_name in item_tags:
            if tag_name in tags:
                item.tags.add(tags[tag_name])
        
        print(f"Created: [{item.type}] {item.title}")


if __name__ == '__main__':
    test_refactored_chatbot()
