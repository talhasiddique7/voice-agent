# Voice Agent with Django and GROQ

A simple web application that allows users to record their voice and transcribe it using GROQ's API.

## Features

- Record audio directly from the browser
- Send audio to the server for processing
- Display transcription results
- Modern, responsive UI with Tailwind CSS

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- A GROQ API key (get it from [GROQ Console](https://console.groq.com/))

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice-agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following content:
   ```
   DEBUG=True
   SECRET_KEY='your-secret-key-here'
   GROQ_API_KEY='your-groq-api-key-here'
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

## Project Structure

- `voice_agent/` - Main project configuration
- `voice/` - Voice app containing the core functionality
  - `templates/voice/` - HTML templates
  - `views.py` - View functions
  - `urls.py` - URL routing

## Important Notes

- This is a development setup. For production, you'll need to:
  - Set `DEBUG=False` in `.env`
  - Configure a production web server (e.g., Gunicorn with Nginx)
  - Set up proper static file serving
  - Use a production database (PostgreSQL recommended)

## License

MIT
