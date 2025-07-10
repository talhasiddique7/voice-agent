import os
import json
import uuid
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import groq
from dotenv import load_dotenv
from .audio_utils import AudioProcessor

# Load environment variables
load_dotenv()

def home(request):
    """Render the main voice recording page with chat history."""
    # Debug: Check if GROQ_API_KEY is loaded
    groq_key = os.getenv("GROQ_API_KEY")
    print(f"GROQ_API_KEY loaded: {'Yes' if groq_key else 'No'}")
    print(f"GROQ_API_KEY starts with: {groq_key[:5] if groq_key else 'None'}...")
    
    # Add media URL to context
    context = {
        'MEDIA_URL': settings.MEDIA_URL.rstrip('/')
    }
    
    return render(request, 'voice/record_new.html', context)

@csrf_exempt
def debug_env(request):
    """Debug endpoint to check environment variables"""
    env_vars = {
        'GROQ_API_KEY_LOADED': bool(os.getenv("GROQ_API_KEY")),
        'GROQ_API_KEY_STARTS_WITH': os.getenv("GROQ_API_KEY", "")[:5] + '...' if os.getenv("GROQ_API_KEY") else 'Not found',
        'PYTHONPATH': os.getenv("PYTHONPATH"),
        'DJANGO_SETTINGS_MODULE': os.getenv("DJANGO_SETTINGS_MODULE"),
    }
    return JsonResponse({
        'success': True,
        'environment': env_vars
    })

def format_chat_history(history):
    """Format chat history for the GROQ API"""
    formatted_history = []
    
    # Add system message first
    system_prompt = """You are a friendly and helpful assistant for kids. Your name is Buddy. 
    You help with school questions, tell fun stories, and create poems. 
    Keep your responses simple, positive, and engaging for children.
    If the question is about school, provide clear and educational answers.
    If asked for a poem or story, make it fun and age-appropriate.
    Keep your responses concise but helpful."""
    formatted_history.append({"role": "system", "content": system_prompt})
    
    # Add conversation history
    for msg in history:
        role = msg.get('role', '').lower()
        content = msg.get('content', '').strip()
        if role in ['user', 'assistant'] and content:
            formatted_history.append({"role": role, "content": content})
    
    return formatted_history

@csrf_exempt
def save_audio_file(audio_file, file_extension='.wav'):
    """Save uploaded audio file and return its path"""
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
    
    # Ensure the file extension starts with a dot
    if not file_extension.startswith('.'):
        file_extension = f".{file_extension}"
    
    # Create a unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}{file_extension}"
    filepath = os.path.join('audio', 'recordings', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    return filepath, full_path

def text_to_speech_file(text, lang='en'):
    """Convert text to speech and save as file, return relative path"""
    if not text:
        return None
        
    audio_processor = AudioProcessor()
    temp_file = audio_processor.text_to_speech(text, lang=lang)
    
    if not temp_file:
        return None
    
    # Create a permanent location for the response audio
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    filename = f"response_{timestamp}_{unique_id}.mp3"
    rel_path = os.path.join('audio', 'responses', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Move the temp file to permanent location
    import shutil
    shutil.move(temp_file, full_path)
    
    return rel_path

@csrf_exempt
def upload_audio(request):
    """Handle audio file upload and return transcription"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)
    
    if 'audio' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No audio file provided'}, status=400)
    
    audio_file = request.FILES['audio']
    
    # Save the audio file
    try:
        # Read the uploaded file
        audio_data = audio_file.read()
        
        # Save with a .wav extension
        file_extension = os.path.splitext(audio_file.name)[1].lower()
        if file_extension != '.wav':
            file_extension = '.wav'
            
        rel_path, full_path = save_audio_file(audio_file, file_extension)
        
        # Save the audio data
        with open(full_path, 'wb') as f:
            f.write(audio_data)
        
        # Transcribe the audio
        audio_processor = AudioProcessor()
        text = audio_processor.transcribe_audio(full_path)
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Could not transcribe audio'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'text': text,
            'audio_url': os.path.join(settings.MEDIA_URL, rel_path.replace('\\', '/'))
        })
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def process_with_groq(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST method is allowed'
        }, status=405)
    
    try:
        # Parse the request data
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_input = data.get('text', '').strip()
                chat_history = data.get('history', [])
            else:
                # Handle form data
                user_input = request.POST.get('text', '').strip()
                chat_history = json.loads(request.POST.get('history', '[]'))
                
            print(f"Received request - Input: {user_input[:50]}...")  # Log first 50 chars of input
        except json.JSONDecodeError:
            error_msg = 'Invalid JSON data in request body'
            print(error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)
        
        if not user_input:
            error_msg = 'No text provided in the request'
            print(error_msg)
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)
        
        # Get GROQ API key from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            error_msg = 'GROQ_API_KEY not found in environment variables'
            print(error_msg)
            return JsonResponse({
                'success': False,
                'error': 'Server configuration error'
            }, status=500)
        
        # Initialize GROQ client
        try:
            print("Initializing GROQ client...")
            client = groq.Client(api_key=groq_api_key)
        except Exception as e:
            error_msg = f'Failed to initialize GROQ client: {str(e)}'
            print(error_msg)
            return JsonResponse({
                'success': False,
                'error': 'Failed to initialize AI service'
            }, status=500)
        
        # Format the conversation history
        try:
            print("Formatting chat history...")
            messages = format_chat_history(chat_history)
            print(f"Formatted messages: {len(messages)} messages")
        except Exception as e:
            error_msg = f'Error formatting chat history: {str(e)}'
            print(error_msg)
            return JsonResponse({
                'success': False,
                'error': 'Error processing conversation'
            }, status=500)
        
        # Add the current user input
        messages.append({"role": "user", "content": user_input})
        
        try:
            print("Sending request to GROQ API...")
            # Get response from GROQ
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=0.7,
                max_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract the response text
            response_text = completion.choices[0].message.content
            print("Successfully received response from GROQ")
            
            # Generate speech for the response
            audio_url = None
            response_audio_path = text_to_speech_file(response_text)
            if response_audio_path:
                audio_url = os.path.join(settings.MEDIA_URL, response_audio_path.replace('\\', '/'))
            
            return JsonResponse({
                'success': True,
                'response': response_text,
                'audio_url': audio_url
            })
            
        except Exception as e:
            error_msg = f'Error getting response from GROQ: {str(e)}'
            print(error_msg)
            return JsonResponse({
                'success': False,
                'error': 'Error communicating with AI service',
                'details': str(e)
            }, status=500)
        
    except Exception as e:
        error_msg = f'Unexpected server error: {str(e)}'
        print(error_msg)
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)
