
import os
import json
import argparse
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import re
import requests
import urllib.parse

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)

class ItineraryPlanner:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def get_weather(self, location, date_str=None):
        """Get weather information using OpenWeatherMap API"""
        try:
            # Use OpenWeatherMap API
            api_key = os.getenv("OPENWEATHERMAP_API_KEY")
            if not api_key:
                return "Weather data unavailable - missing API key"
            
            encoded_location = urllib.parse.quote(location)
            
            # Get current weather if no date is provided
            if not date_str or date_str.lower() == "current":
                url = f"https://api.openweathermap.org/data/2.5/weather?q={encoded_location}&appid={api_key}&units=metric"
                response = requests.get(url)
                
                if response.status_code != 200:
                    return f"Weather data unavailable for {location}"
                
                data = response.json()
                return {
                    "location": f"{data['name']}, {data['sys']['country']}",
                    "date": "current",
                    "temperature": f"{data['main']['temp']}°C",
                    "conditions": data['weather'][0]['description']
                }
            else:
                # Parse the date and get forecast
                url = f"https://api.openweathermap.org/data/2.5/forecast?q={encoded_location}&appid={api_key}&units=metric"
                response = requests.get(url)
                
                if response.status_code != 200:
                    return f"Weather forecast unavailable for {location}"
                
                data = response.json()
                
                # Simple processing of forecast data
                forecasts = []
                for item in data['list'][:5]:  # Just get first 5 forecasts
                    forecasts.append({
                        "date": item['dt_txt'],
                        "temperature": f"{item['main']['temp']}°C",
                        "conditions": item['weather'][0]['description']
                    })
                
                return {
                    "location": f"{data['city']['name']}, {data['city']['country']}",
                    "forecasts": forecasts
                }
        except Exception as e:
            return f"Error fetching weather data: {str(e)}"
    
    def get_attractions(self, location):
        """Get attractions using Gemini"""
        try:
            prompt = f"""
            Generate a JSON array of 5 real, popular tourist attractions in {location}. 
            For each attraction, include these fields:
            - name: The full name of the attraction
            - category: Type of attraction (museum, landmark, park, etc.)
            - description: A brief description
            - best_for: What type of travelers would enjoy this most
            
            Format as a clean JSON array with only these fields.
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract the JSON from the response
            attractions_text = response.text
            
            # Clean up the text to ensure it's valid JSON
            if "json" in attractions_text:
                attractions_text = attractions_text.split("json")[1].split("")[0].strip()
            elif "" in attractions_text:
                attractions_text = attractions_text.split("")[1].split("")[0].strip()
            
            # Try to parse the JSON
            try:
                attractions = json.loads(attractions_text)
                return attractions
            except Exception:
                # Fallback
                return [
                    {
                        "name": f"Top Attraction 1 in {location}",
                        "category": "Popular Landmark",
                        "description": "A must-visit destination known for its significance.",
                        "best_for": "History enthusiasts"
                    },
                    {
                        "name": f"Top Attraction 2 in {location}",
                        "category": "Museum",
                        "description": "Famous museum housing an impressive collection.",
                        "best_for": "Art and history lovers"
                    }
                ]
        except Exception as e:
            return f"Error generating attractions: {str(e)}"
    
    def generate_itinerary(self, user_request):
        """Generate a complete itinerary using Gemini"""
        print("Generating itinerary...")
        
        # Extract key info from request
        destinations = self.extract_destinations(user_request)
        duration = self.extract_duration(user_request)
        dates = self.extract_dates(user_request)
        
        # Get additional information for the first destination
        primary_destination = destinations[0] if destinations else "Unknown"
        weather_info = self.get_weather(primary_destination)
        attractions = self.get_attractions(primary_destination)
        
        # Create a context-rich prompt for Gemini
        prompt = f"""
        As an expert travel planner, create a detailed itinerary based on this request:
        
        "{user_request}"
        
        Extracted information:
        - Destinations: {', '.join(destinations) if destinations else 'Not specified'}
        - Duration: {duration if duration else 'Not specified'} days
        - Dates: {', '.join(dates) if dates else 'Not specified'}
        
        Weather information for {primary_destination}:
        {json.dumps(weather_info, indent=2)}
        
        Top attractions in {primary_destination}:
        {json.dumps(attractions, indent=2)}
        
        Create a comprehensive day-by-day itinerary in Markdown format with:
        1. A title and brief introduction
        2. Key information (dates, duration, destinations)
        3. Day-by-day breakdown with:
           - Morning, afternoon, and evening activities
           - Specific attraction recommendations (use the provided attractions)
           - Meal suggestions
           - Accommodation recommendations
        4. Budget estimate
        5. Travel tips considering the weather and local conditions
        
        Format the itinerary as a well-structured Markdown document.
        
        IMPORTANT: Do not use asterisks (**) in the Markdown formatting. Instead, use other formatting options like headers (##) for emphasis.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def extract_destinations(self, text):
        """Extract potential destinations from the text"""
        # This is a simplified extraction method
        # A real implementation would use more sophisticated NLP
        
        # List of common travel-related verbs and prepositions
        travel_verbs = ['visit', 'travel to', 'go to', 'explore', 'see', 'vacation in', 'holiday in', 'trip to']
        
        destinations = []
        
        # Simple pattern matching for destination after travel verbs
        for verb in travel_verbs:
            pattern = f"{verb}\\s+([A-Za-z\\s,]+)"
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the destination name
                dest = match.strip()
                # Remove trailing punctuation
                dest = re.sub(r'[,.!?]+$', '', dest)
                if dest and len(dest) > 2:  # Avoid very short matches
                    destinations.append(dest)
        
        # If no destinations found using verbs, try to extract location names
        if not destinations:
            # This is a very simplified approach - in a real app, you'd use a NER model
            # or a geo database to identify location names
            words = text.split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 3 and word.lower() not in ['plan', 'trip', 'day', 'week', 'itinerary']:
                    destinations.append(word)
        
        # Remove duplicates while preserving order
        unique_destinations = []
        for dest in destinations:
            if dest not in unique_destinations:
                unique_destinations.append(dest)
        
        return unique_destinations
    
    def extract_duration(self, text):
        """Extract trip duration from text"""
        duration_patterns = [
            r'(\d+)\s+days?',
            r'(\d+)\s+weeks?',
            r'(\d+)\s+nights?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                unit = match.group(0).split()[-1].lower()
                
                if 'week' in unit:
                    return number * 7  # Convert weeks to days
                else:
                    return number  # Days or nights
        
        return None
    
    def extract_dates(self, text):
        """Extract dates from text"""
        date_patterns = [
            r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{1,2}-\d{1,2})'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates

def main():
    parser = argparse.ArgumentParser(description='Simplified AI Travel Itinerary Planner')
    parser.add_argument('prompt', nargs='?', default=None, help='Natural language itinerary request')
    args = parser.parse_args()
    
    planner = ItineraryPlanner()
    
    if args.prompt:
        result = planner.generate_itinerary(args.prompt)
        print(result)
    else:
        print("Welcome to the Simplified AI Travel Itinerary Planner!")
        print("This version requires fewer API keys and has simpler dependencies.")
        print("Required API key in your .env file:")
        print("- GOOGLE_API_KEY (for Gemini Pro)")
        print("Optional API key for enhanced weather data:")
        print("- OPENWEATHERMAP_API_KEY (for weather forecasts)")
        
        while True:
            user_input = input("\nEnter your itinerary request (or 'exit' to quit): ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            result = planner.generate_itinerary(user_input)
            print("\n" + "="*80)
            print(result)
            print("="*80)

if __name__ == "__main__":
    main()