# 🌍 AI Travel Itinerary Planner

An AI-powered travel itinerary generator that creates personalized day-by-day travel plans based on natural language input. This application uses Google's Gemini AI and OpenWeatherMap to create comprehensive travel itineraries with weather information, attraction recommendations, and budget estimates.

![itinerary](https://github.com/user-attachments/assets/517c2094-df1c-4c8e-bff1-9bdc71513ddc)

![iti1](https://github.com/user-attachments/assets/50024f22-4836-4c58-814d-560be2f224dc)

## ✨ Features

- **Natural Language Input**: Simply describe your travel plans, and the AI generates a detailed itinerary
- **Day-by-Day Breakdown**: Complete schedule with morning, afternoon, and evening activities
- **Weather Integration**: Current weather and forecasts for your destination
- **Attraction Recommendations**: Top tourist spots with descriptions
- **Budget Estimates**: Cost projections with multi-currency support
- **Travel Tips**: Customized advice based on destination and conditions
- **Streamlit Web Interface**: User-friendly interface to input requests and view results
- **Downloadable Itineraries**: Save your travel plans as Markdown files

## 🛠️ Technologies Used

- Python 3.8+
- Google Gemini AI (via google-generativeai package)
- OpenWeatherMap API
- Streamlit for web interface
- Regular expressions for text parsing

## 📋 Prerequisites

- Python 3.8 or higher
- A Google API key for Gemini AI
- An OpenWeatherMap API key (optional, but recommended for weather functionality)

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ai-travel-itinerary-planner.git
   cd ai-travel-itinerary-planner
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
   ```

## 🖥️ Usage

### Command Line Interface

Run the application in command-line mode:

```bash
python itinerary_planner.py "I want to visit Paris for 5 days in June with my family"
```

Or start the interactive mode:

```bash
python itinerary_planner.py
```

### Web Interface

Launch the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

Then open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

## 📝 How It Works

1. The application parses your natural language request to extract destinations, duration, and dates
2. It fetches current weather or forecasts for the destination using OpenWeatherMap
3. It identifies popular attractions in the area using Gemini AI
4. All this information is used to create a context-rich prompt for Gemini AI
5. The AI generates a comprehensive itinerary based on the enhanced context
6. For the web interface, additional features like currency conversion and budget enhancement are applied

## 🔑 API Keys

### Google API Key
- Sign up for Google AI Studio: https://makersuite.google.com/
- Create a Gemini API key

### OpenWeatherMap API Key (Optional)
- Register at OpenWeatherMap: https://home.openweathermap.org/users/sign_up
- Get a free API key from your account

## 📦 Project Structure

```
ai-travel-itinerary-planner/
├── itinerary_planner.py     # Core functionality and CLI
├── streamlit_app.py         # Streamlit web interface
├── requirements.txt         # Required packages
├── .env                     # API keys (not tracked by Git)
└── README.md                # This file
```

## 🛠️ Customization

- Edit the `extract_destinations` method to improve location detection
- Modify the Gemini prompt in `generate_itinerary` to change the itinerary style
- Add new currency options in the Streamlit app by updating the `exchange_rates` dictionary

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements

- Google Gemini AI for natural language processing
- OpenWeatherMap for weather data
- Streamlit for the web interface framework

---


