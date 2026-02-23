"""
AI Service for extracting structured data from user descriptions
using Groq AI API (FREE with generous limits!)
"""
import json
import os
import time
from typing import Dict, Optional
from openai import OpenAI


class ChatBotService:
    """Service class for interacting with Groq AI API"""
    
    def __init__(self):
        """Initialize Groq client with API key from environment"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        # Check if we should use mock mode (for testing)
        self.use_mock = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'
        
        if not self.use_mock:
            try:
                # Groq uses OpenAI-compatible API
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1",
                    timeout=60.0,
                    max_retries=2
                )
                # Use Llama model - fast and free!
                self.model_name = 'llama-3.3-70b-versatile'
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
                print("Falling back to MOCK mode. Set USE_MOCK_AI=true in .env to silence this warning.")
                self.use_mock = True
        
        self.available_tags = [
            'Electronics', 'Books', 'Clothing', 'ID Cards', 
            'Keys', 'Wallet', 'Bags', 'Accessories', 'Other'
        ]
    
    def extract_item_info(self, user_description: str) -> Dict:
        """
        Extract structured item information from user's natural language description
        
        Args:
            user_description: User's text describing lost or found item
            
        Returns:
            Dict containing extracted information:
            {
                "type": "LOST" or "FOUND",
                "title": "Item title/name",
                "description": "Detailed description",
                "location_description": "Location description",
                "latitude": float (optional),
                "longitude": float (optional),
                "tags": ["tag1", "tag2", ...]
            }
        """
        # Use mock implementation if mock mode is enabled
        if self.use_mock:
            return self._mock_extract_item_info(user_description)
        
        system_prompt = self._create_system_prompt()
        
        # Retry logic for network/SSL errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_description}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                # Extract JSON from response
                response_text = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                response_text = response_text.strip()
                
                # Parse the JSON response
                result = json.loads(response_text)
                
                # Validate and clean the result
                cleaned_result = self._validate_and_clean_result(result)
                
                return {
                    "success": True,
                    "data": cleaned_result
                }
                
            except (ConnectionError, TimeoutError, OSError) as e:
                # Network/SSL errors - retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"Network error after {max_retries} attempts: {str(e)}"
                    }
            except Exception as e:
                # Other errors - don't retry
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": False,
            "error": "Max retries exceeded"
        }
    
    def _mock_extract_item_info(self, user_description: str) -> Dict:
        """
        Mock implementation for testing/development (when AI API is unavailable)
        Uses simple keyword matching to simulate AI extraction
        """
        description = user_description.lower()
        
        # Determine type (LOST or FOUND)
        item_type = "LOST"
        if any(word in description for word in ["found", "find"]):
            item_type = "FOUND"
        
        # Identify item and assign tags
        tags = []
        title = "Unknown Item"
        
        if any(word in description for word in ["phone", "iphone", "android", "mobile", "smartphone"]):
            tags.append("Electronics")
            title = "Mobile Phone"
        elif any(word in description for word in ["laptop", "computer", "macbook"]):
            tags.append("Electronics")
            title = "Laptop"
        elif any(word in description for word in ["wallet", "purse"]):
            tags.append("Wallet")
            title = "Wallet"
        elif any(word in description for word in ["keys", "key"]):
            tags.append("Keys")
            title = "Keys"
        elif any(word in description for word in ["id", "card", "license"]):
            tags.append("ID Cards")
            title = "ID Card"
        elif any(word in description for word in ["book", "notebook", "textbook"]):
            tags.append("Books")
            title = "Book"
        elif any(word in description for word in ["bag", "backpack", "purse"]):
            tags.append("Bags")
            title = "Bag"
        elif any(word in description for word in ["watch", "glasses", "jewelry"]):
            tags.append("Accessories")
            title = "Accessory"
        else:
            tags.append("Other")
            title = "Item"
        
        # Extract location
        location = "Not specified"
        if "library" in description:
            location = "Library"
        elif "cafeteria" in description:
            location = "Cafeteria"
        elif "classroom" in description:
            location = "Classroom"
        elif "gym" in description:
            location = "Gym"
        
        result = {
            "type": item_type,
            "title": title,
            "description": user_description,
            "location_description": location,
            "latitude": None,
            "longitude": None,
            "tags": tags
        }
        
        return {
            "success": True,
            "data": result,
            "mock": True  # Indicate this is a mock response
        }
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for ChatGPT"""
        return f"""You are an AI assistant for a university lost and found system. 
Your task is to extract structured information from user descriptions about lost or found items.

Available tags: {', '.join(self.available_tags)}

Extract the following information and return it as a JSON object:
1. "type": Must be either "LOST" or "FOUND" (uppercase)
2. "title": A short, descriptive title for the item (max 200 characters)
3. "description": A detailed description of the item including color, brand, condition, and any unique features
4. "location_description": Description of where the item was lost or found
5. "latitude": If a specific location is mentioned and you can infer coordinates, provide it (optional, can be null)
6. "longitude": If a specific location is mentioned and you can infer coordinates, provide it (optional, can be null)
7. "tags": An array of relevant tags from the available tags list (at least one tag is required)

CRITICAL LANGUAGE RULES:
- **PRESERVE THE ORIGINAL LANGUAGE**: If the user writes in Persian/Farsi, Arabic, or any non-English language, keep ALL text (title, description, location) in that EXACT language. DO NOT TRANSLATE.
- Only use English if the user's input is in English
- The title and description should be in the SAME language as the user's input

Important rules:
- If the user doesn't explicitly state whether they lost or found something, try to infer from context
- If you can't determine if it's lost or found, default to "LOST"
- For latitude/longitude, only provide if you have high confidence about the location (e.g., "library", "engineering building"). Otherwise, set to null
- Choose tags that best match the item category
- Make the title concise but descriptive
- Include all relevant details in the description
- **The title should be very specific and match-friendly** - use the most important keywords that someone searching would use

Example input (English): "I lost my iPhone 13 Pro Max in blue color near the library yesterday. It has a cracked screen and a sticker on the back."
Example output:
{{
    "type": "LOST",
    "title": "iPhone 13 Pro Max - Blue",
    "description": "iPhone 13 Pro Max in blue color with a cracked screen and a sticker on the back. Lost near the library.",
    "location_description": "Near the library",
    "latitude": null,
    "longitude": null,
    "tags": ["Electronics"]
}}

Example input (Persian): "مداد رنگی گم کردم"
Example output:
{{
    "type": "LOST",
    "title": "مداد رنگی",
    "description": "مداد رنگی گم شده",
    "location_description": "",
    "latitude": null,
    "longitude": null,
    "tags": ["Other"]
}}

Always respond with valid JSON only, no additional text."""
    
    def _validate_and_clean_result(self, result: Dict) -> Dict:
        """Validate and clean the extracted result"""
        # Ensure type is valid
        item_type = result.get('type', 'LOST').upper()
        if item_type not in ['LOST', 'FOUND']:
            item_type = 'LOST'
        
        # Ensure title exists and is not too long
        title = result.get('title', 'Untitled Item')[:200]
        
        # Ensure description exists
        description = result.get('description', '')
        if not description:
            description = title
        
        # Location description
        location_description = result.get('location_description', 'Not specified')
        
        # Coordinates (optional)
        latitude = result.get('latitude')
        longitude = result.get('longitude')
        
        # Validate latitude and longitude
        if latitude is not None:
            try:
                latitude = float(latitude)
                if not (-90 <= latitude <= 90):
                    latitude = None
            except (ValueError, TypeError):
                latitude = None
        
        if longitude is not None:
            try:
                longitude = float(longitude)
                if not (-180 <= longitude <= 180):
                    longitude = None
            except (ValueError, TypeError):
                longitude = None
        
        # Validate tags
        tags = result.get('tags', [])
        if not isinstance(tags, list):
            tags = []
        
        # Filter tags to only include available ones
        valid_tags = [tag for tag in tags if tag in self.available_tags]
        if not valid_tags:
            valid_tags = ['Other']
        
        return {
            'type': item_type,
            'title': title,
            'description': description,
            'location_description': location_description,
            'latitude': latitude,
            'longitude': longitude,
            'tags': valid_tags
        }    
    def find_related_items(self, user_description: str, items_data: list) -> Dict:
        """
        Find related items from a list of items based on user's description
        
        Args:
            user_description: User's text describing lost or found item
            items_data: List of item dictionaries with id, title, description, type, tags
            
        Returns:
            Dict containing:
            {
                "success": True/False,
                "data": {
                    "related_item_ids": [id1, id2, id3, ...],  # List of matching item IDs
                    "explanation": "Brief explanation of why these items were selected"
                },
                "error": "Error message if failed"
            }
        """
        # Use mock implementation if mock mode is enabled
        if self.use_mock:
            return self._mock_find_related_items(user_description, items_data)
        
        # Create a concise summary of items for the prompt
        items_summary = []
        for item in items_data[:50]:  # Limit to first 50 items to avoid token limits
            items_summary.append({
                "id": item['id'],
                "title": item['title'],
                "description": item['description'][:200],  # Truncate long descriptions
                "type": item['type'],
                "tags": item.get('tags', [])
            })
        
        system_prompt = self._create_matching_system_prompt()
        user_prompt = f"""User's description: {user_description}

Available items in database:
{json.dumps(items_summary, ensure_ascii=False, indent=2)}

Find and return the IDs of items that match or are related to the user's description."""
        
        # Retry logic for network/SSL errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                # Extract JSON from response
                response_text = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                response_text = response_text.strip()
                
                # Parse the JSON response
                result = json.loads(response_text)
                
                # Validate the result
                related_ids = result.get('related_item_ids', [])
                if not isinstance(related_ids, list):
                    related_ids = []
                
                return {
                    "success": True,
                    "data": {
                        "related_item_ids": related_ids,
                        "explanation": result.get('explanation', 'AI matched these items based on similarity.')
                    }
                }
                
            except (ConnectionError, TimeoutError, OSError) as e:
                # Network/SSL errors - retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"Network error after {max_retries} attempts: {str(e)}"
                    }
            except Exception as e:
                # Other errors - don't retry
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": False,
            "error": "Max retries exceeded"
        }
    
    def _mock_find_related_items(self, user_description: str, items_data: list) -> Dict:
        """
        Mock implementation for testing - uses simple keyword matching
        """
        description_lower = user_description.lower()
        related_ids = []
        
        # Extract keywords from user description
        keywords = []
        for word in description_lower.split():
            if len(word) > 3:  # Only consider words longer than 3 characters
                keywords.append(word)
        
        # Score each item based on keyword matches
        item_scores = []
        for item in items_data:
            score = 0
            item_text = f"{item['title']} {item['description']}".lower()
            
            for keyword in keywords:
                if keyword in item_text:
                    score += 1
            
            if score > 0:
                item_scores.append((item['id'], score))
        
        # Sort by score and return top matches
        item_scores.sort(key=lambda x: x[1], reverse=True)
        related_ids = [item_id for item_id, _ in item_scores[:10]]  # Top 10 matches
        
        return {
            "success": True,
            "data": {
                "related_item_ids": related_ids,
                "explanation": "Mock: Items matched based on keyword similarity."
            },
            "mock": True
        }
    
    def _create_matching_system_prompt(self) -> str:
        """Create the system prompt for matching items"""
        return """You are an AI assistant for a university lost and found system.
Your task is to analyze a user's description of a lost or found item and find matching items from the database.

MATCHING RULES:
1. If the user says they LOST something, find items marked as FOUND that match their description
2. If the user says they FOUND something, find items marked as LOST that match their description
3. Match based on:
   - Item type/category (e.g., phone, wallet, keys)
   - Physical description (color, brand, size, features)
   - Location (if mentioned)
   - Any unique identifiers
4. LANGUAGE MATCHING: If the user writes in Persian/Farsi, Arabic, or any non-English language, match with items in the SAME language. Consider translations and similar meanings.
5. Rank matches by relevance - prioritize exact matches, then similar items
6. Return the IDs of matching items in order of relevance (most relevant first)
7. Limit results to a maximum of 10 items

OUTPUT FORMAT:
Return a JSON object with:
{
    "related_item_ids": [id1, id2, id3, ...],  // Array of item IDs, ordered by relevance
    "explanation": "Brief explanation of matching criteria used"
}

Example:
User description: "I lost my blue iPhone 13 near the library"
Items to search: [
    {"id": 1, "title": "iPhone 13 - Blue", "description": "Found blue iPhone 13 in library", "type": "FOUND"},
    {"id": 2, "title": "Black iPhone", "description": "Found black iPhone in cafeteria", "type": "FOUND"},
    {"id": 3, "title": "Samsung Phone", "description": "Found Samsung Galaxy", "type": "FOUND"}
]

Response:
{
    "related_item_ids": [1],
    "explanation": "Found exact match for blue iPhone 13 near library, marked as FOUND (opposite of user's LOST item)"
}

Always respond with valid JSON only, no additional text."""