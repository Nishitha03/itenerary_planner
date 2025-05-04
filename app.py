

import os
import streamlit as st
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from itinerary_planner import ItineraryPlanner

# Page configuration
st.set_page_config(
    page_title="AI Travel Itinerary Planner",
    page_icon="✈️",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Check if the API keys are available
google_api_key = os.getenv("GOOGLE_API_KEY")
weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

# Currency exchange rates (approximations)
# In a production app, you would use a currency API
exchange_rates = {
    "USD": 1.0,
    "EUR": 0.91,
    "GBP": 0.78,
    "JPY": 151.23,
    "INR": 83.42,
    "AUD": 1.49,
    "CAD": 1.35
}

# Currency symbols
currency_symbols = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "INR": "₹",
    "AUD": "A$",
    "CAD": "C$"
}

def convert_currency(amount_usd, target_currency):
    """Convert USD amount to target currency"""
    if target_currency == "USD":
        return f"{currency_symbols[target_currency]}{amount_usd:,.2f}"
    else:
        converted = amount_usd * exchange_rates[target_currency]
        # Format JPY and INR without decimal places
        if target_currency in ["JPY", "INR"]:
            return f"{currency_symbols[target_currency]}{converted:,.0f}"
        else:
            return f"{currency_symbols[target_currency]}{converted:,.2f}"

def generate_budget_section(itinerary, preferred_currency):
    """Extract and enhance budget information from the itinerary"""
    # This is a simplified approach - in reality, you would
    # need more sophisticated parsing of the markdown text
    budget_section = ""
    budget_found = False
    
    lines = itinerary.split('\n')
    for i, line in enumerate(lines):
        if "budget" in line.lower() and "#" in line:
            budget_found = True
            budget_section = line + "\n"
            j = i + 1
            while j < len(lines) and not (lines[j].startswith('#')):
                budget_section += lines[j] + "\n"
                j += 1
            break
    
    # Remove asterisks from budget section
    budget_section = remove_asterisks(budget_section)
    
    if budget_found and preferred_currency != "USD":
        # Add currency conversions
        enhanced_budget = budget_section
        # Find dollar amounts in text
        import re
        dollar_amounts = re.findall(r'\$(\d+(?:,\d+)?(?:\.\d+)?)', budget_section)
        
        for amount_str in dollar_amounts:
            # Remove commas
            clean_amount = amount_str.replace(',', '')
            try:
                amount_usd = float(clean_amount)
                converted = convert_currency(amount_usd, preferred_currency)
                enhanced_budget = enhanced_budget.replace(
                    f"${amount_str}", 
                    f"${amount_str} ({converted})"
                )
            except ValueError:
                continue
        
        return enhanced_budget
    
    return budget_section

def remove_asterisks(text):
    """Remove all ** from the text"""
    return text.replace("**", "")

def main():
    # Initialize the planner
    planner = ItineraryPlanner()
    
    # Initialize session state to maintain state between reruns
    if 'user_request' not in st.session_state:
        st.session_state.user_request = ""
    if 'previous_selection' not in st.session_state:
        st.session_state.previous_selection = "Write your own"
    
    # Header section
    st.title("🌍 AI Travel Itinerary Planner")
    st.markdown("""
    Let our AI create a personalized travel itinerary based on your preferences! 
    Simply describe your travel plans, and we'll generate a detailed day-by-day itinerary.
    """)
    
    # API key warnings if needed
    if not google_api_key:
        st.warning("⚠️ GOOGLE_API_KEY not found in environment variables. The application won't work without it.")
    
    if not weather_api_key:
        st.info("ℹ️ OPENWEATHERMAP_API_KEY not found. Weather information will be limited.")
    
    # User input section
    st.header("Enter Your Travel Details")
    
    # Example prompts
    examples = [
        "I want to visit Paris for 5 days in June with my family",
        "Plan a 7-day trip to Tokyo and Kyoto in autumn for a solo traveler",
        "Weekend getaway to Miami in July for a couple",
        "10-day adventure trip to Costa Rica in December for a group of friends",
        "Plan a budget trip to Goa, India for 4 days next month"
    ]
    
    # Input method selection
    input_method = st.radio(
        "Choose how to provide your travel details:",
        ["Use an example", "Write your own request"],
        horizontal=True
    )
    
    # User input based on selection
    if input_method == "Use an example":
        example_selection = st.selectbox(
            "Select an example request:",
            examples
        )
        user_request = example_selection
    else:
        user_request = st.text_area(
            "Describe your travel plans:",
            height=100,
            placeholder="Example: I want to visit Amsterdam for 3 days in May with my partner",
            value=st.session_state.user_request
        )
        # Save the user input to session state
        st.session_state.user_request = user_request
    
    # Additional options
    with st.expander("Additional Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_weather = st.checkbox("Include weather information", value=True)
            include_attractions = st.checkbox("Include attraction recommendations", value=True)
            include_budget = st.checkbox("Include budget estimate", value=True)
        
        with col2:
            preferred_currency = st.selectbox(
                "Preferred currency for budget:", 
                options=["USD", "EUR", "GBP", "JPY", "INR", "AUD", "CAD"],
                index=0,
                format_func=lambda x: f"{x} ({currency_symbols[x]})"
            )
    
    # Generate button
    generate_button = st.button("Generate Itinerary", type="primary")
    
    # Process the request
    if generate_button and user_request:
        with st.spinner("Generating your personalized travel itinerary... This may take a moment."):
            try:
                # Generate itinerary
                itinerary = planner.generate_itinerary(user_request)
                
                # Remove asterisks from the itinerary
                itinerary_no_asterisks = remove_asterisks(itinerary)
                
                # Display the results
                st.success("✅ Your itinerary is ready!")
                
                # Get destinations and dates for the info box
                destinations = planner.extract_destinations(user_request)
                duration = planner.extract_duration(user_request)
                dates = planner.extract_dates(user_request)
                
                # Create a nice info box
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.subheader("Trip Summary")
                    st.markdown(f"**Destinations:** {', '.join(destinations) if destinations else 'Not specified'}")
                    st.markdown(f"**Duration:** {duration if duration else 'Not specified'} days")
                    st.markdown(f"**Dates:** {', '.join(dates) if dates else 'Not specified'}")
                    st.markdown(f"**Currency:** {preferred_currency} ({currency_symbols[preferred_currency]})")
                    
                    # Get weather for the first destination
                    if include_weather and destinations:
                        st.subheader("Weather Info")
                        weather_info = planner.get_weather(destinations[0])
                        if isinstance(weather_info, dict):
                            if "forecasts" in weather_info:
                                st.markdown(f"**Location:** {weather_info['location']}")
                                for forecast in weather_info['forecasts'][:3]:
                                    st.markdown(f"- **{forecast['date']}**: {forecast['temperature']}, {forecast['conditions']}")
                            else:
                                st.markdown(f"**Current weather in {weather_info['location']}**: {weather_info['temperature']}, {weather_info['conditions']}")
                        else:
                            st.markdown(weather_info)  # Display error message if any
                
                # Display the full itinerary
                with col2:
                    st.subheader("Your Itinerary")
                    
                    # If user wants a non-USD currency and budget is included
                    if preferred_currency != "USD" and include_budget:
                        # Modified itinerary with currency conversions
                        budget_section = generate_budget_section(itinerary_no_asterisks, preferred_currency)
                        if budget_section:
                            # Display the itinerary until we find the budget section
                            budget_index = itinerary_no_asterisks.lower().find("budget")
                            if budget_index > 0:
                                st.markdown(itinerary_no_asterisks[:budget_index])
                                st.markdown(budget_section)
                                # Find where the budget section ends
                                next_section = itinerary_no_asterisks[budget_index:].find("\n#")
                                if next_section > 0:
                                    st.markdown(itinerary_no_asterisks[budget_index + next_section:])
                            else:
                                st.markdown(itinerary_no_asterisks)
                        else:
                            st.markdown(itinerary_no_asterisks)
                    else:
                        st.markdown(itinerary_no_asterisks)
                
                # Attraction section
                if include_attractions and destinations:
                    st.subheader("Top Attractions")
                    attractions = planner.get_attractions(destinations[0])
                    if isinstance(attractions, list):
                        cols = st.columns(min(5, len(attractions)))
                        for i, attraction in enumerate(attractions[:5]):
                            with cols[i % len(cols)]:
                                st.markdown(f"**{attraction['name']}**")
                                st.markdown(f"*{attraction['category']}*")
                                st.markdown(attraction['description'])
                                st.markdown(f"Best for: {attraction['best_for']}")
                                st.divider()
                    else:
                        st.markdown(attractions)  # Display error message if any
                
                # Add a download button for the itinerary
                st.download_button(
                    label="Download Itinerary",
                    data=itinerary_no_asterisks,  # Use the version without asterisks
                    file_name=f"travel_itinerary_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.markdown("Please check your API keys and try again.")
    
    # Footer
    st.divider()
    st.markdown("### How to use this planner")
    st.markdown("""
    1. Choose between using an example or writing your own travel request
    2. For custom requests, include destinations, duration, dates, and travel preferences
    3. Select your preferred currency for budget calculations
    4. Click the 'Generate Itinerary' button
    5. Review your personalized itinerary
    6. Download the itinerary for offline use
    """)
    
    st.markdown("*Powered by Gemini AI and OpenWeatherMap*")

if __name__ == "__main__":
    main()