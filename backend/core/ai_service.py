"""
AI Service for extracting structured data from user descriptions
using OpenAI's ChatGPT API
"""
import json
import os
from typing import Dict, Optional
from openai import OpenAI


class ChatBotService:
    """Service class for interacting with ChatGPT API"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
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
        system_prompt = self._create_system_prompt()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_description}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Validate and clean the result
            cleaned_result = self._validate_and_clean_result(result)
            
            return {
                "success": True,
                "data": cleaned_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
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

Important rules:
- If the user doesn't explicitly state whether they lost or found something, try to infer from context
- If you can't determine if it's lost or found, default to "LOST"
- For latitude/longitude, only provide if you have high confidence about the location (e.g., "library", "engineering building"). Otherwise, set to null
- Choose tags that best match the item category
- Make the title concise but descriptive
- Include all relevant details in the description

Example input: "I lost my iPhone 13 Pro Max in blue color near the library yesterday. It has a cracked screen and a sticker on the back."

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
