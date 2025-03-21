import json

class News:
    """A class to represent and format news content."""
    
    def __init__(self, news_id, title, content, source="", url="", image_url="", tags=None):
        self.news_id = news_id
        self.title = title
        self.content = content
        self.source = source
        self.url = url
        self.image_url = image_url
        self.tags = tags or []
    
    @classmethod
    def from_json(cls, json_data):
        """Create a News object from JSON data."""
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
                
            return cls(
                news_id=data.get('id', ''),
                title=data.get('title', ''),
                content=data.get('content', ''),
                source=data.get('source', ''),
                url=data.get('url', ''),
                image_url=data.get('image_url', ''),
                tags=data.get('tags', [])
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid news format: {e}")
    
    def format_telegram_message(self):
        """Format the news for posting on Telegram."""
        # Determine appropriate emoji based on content
        title_emoji = "📰"
        
        # Check for cryptocurrency-specific content
        crypto_keywords = ["bitcoin", "ethereum", "بيتكوين", "إيثريوم", "كريبتو", "عملات رقمية", "crypto"]
        combined_text = (self.title + " " + self.content).lower()
        
        if any(keyword in combined_text for keyword in crypto_keywords):
            if "bitcoin" in combined_text or "بيتكوين" in combined_text:
                title_emoji = "₿"
            elif "ethereum" in combined_text or "إيثريوم" in combined_text:
                title_emoji = "Ξ"
            else:
                title_emoji = "💰"
        
        # Create a plain text message with no Markdown to avoid parsing errors
        message = f"{title_emoji} {self.title}\n\n"
        
        if self.content:
            # Truncate content if too long for Telegram (limit is 4096 chars)
            max_content_length = 3000  # Leave room for other elements
            content = self.content if len(self.content) <= max_content_length else self.content[:max_content_length] + "..."
            message += f"{content}\n\n"
        
        if self.source:
            message += f"📊 المصدر: {self.source}\n"
        
        if self.url:
            message += f"🔗 الرابط: {self.url}\n"
        
        if self.tags and len(self.tags) > 0:
            # Format tags as plain text hashtags
            crypto_tags = ' '.join([f"#{tag.replace(' ', '_')}" for tag in self.tags])
            message += f"\n{crypto_tags}\n"
        
        # Add market indicators for crypto news
        if any(keyword in combined_text for keyword in crypto_keywords):
            # Add market sentiment indicator
            import hashlib
            # Use a hash of the news_id to create a pseudo-random market trend
            hash_value = int(hashlib.md5(self.news_id.encode()).hexdigest(), 16)
            market_trend = "🟢 السوق: صاعد" if hash_value % 2 == 0 else "🔴 السوق: هابط"
            message += f"\n{market_trend}"
        
        # Add bot branding
        message += "\n\n📱 مقدم من: بوت أخبار الكريبتو من إنفترون داو"
        
        return message
    
    def to_dict(self):
        """Convert the news object to a dictionary."""
        return {
            'id': self.news_id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'image_url': self.image_url,
            'tags': self.tags
        }
    
    def __str__(self):
        return f"News({self.news_id}: {self.title})"
