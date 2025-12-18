# Swarm Wrapped

Generate your own Spotify Wrapped-style report from your Foursquare Swarm check-ins.

## Features

- 📊 Total check-ins, venues, cities, and countries
- 🔥 Longest check-in streak
- 🏆 Top venues and categories
- ⏰ Time personality analysis
- 👥 Check-in crew stats
- 🗺️ Interactive map of all your check-ins

## Setup

### Prerequisites

- Python 3.9+
- Foursquare Developer Account

### Foursquare API Setup

1. Go to [Foursquare Developer Console](https://foursquare.com/developers/apps)
2. Create a new app
3. Note your Client ID and Client Secret
4. Add `http://localhost:8000/callback` as a redirect URI

### Installation

```bash
# Clone the repo
git clone https://github.com/alexpriest/swarm-wrapped-app.git
cd swarm-wrapped-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FOURSQUARE_CLIENT_ID="your_client_id"
export FOURSQUARE_CLIENT_SECRET="your_client_secret"
export SESSION_SECRET="your_random_secret_key"

# Run the app
uvicorn app:app --reload
```

Visit `http://localhost:8000` and connect your Swarm account!

## Deployment

This app can be deployed to Vercel, Railway, or any Python hosting platform.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `FOURSQUARE_CLIENT_ID` | Your Foursquare app client ID |
| `FOURSQUARE_CLIENT_SECRET` | Your Foursquare app client secret |
| `FOURSQUARE_REDIRECT_URI` | OAuth callback URL (e.g., `https://yourapp.com/callback`) |
| `SESSION_SECRET` | Random string for session encryption |

## Privacy

- Your check-in data is fetched directly from Foursquare
- Data is processed in-memory and never stored
- Your access token is only kept in your browser session
- Disconnect anytime to clear your session

## Credits

Built with [swarm-mcp](https://github.com/alexpriest/swarm-mcp)

## License

MIT
