import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import os
import json
import toml  # Import toml module to read secrets.toml

# Function to load API key from secrets.toml file
def load_api_key():
    """Reads the API key from the secrets.toml file."""
    try:
        secrets = toml.load("secrets.toml")
        return secrets.get("GEMINI_API_KEY", None)  # Extract API key
    except FileNotFoundError:
        print("Error: secrets.toml file not found!")
        return None
    except toml.TomlDecodeError:
        print("Error: Invalid TOML format in secrets.toml!")
        return None

# Function to set up Gemini API
def setup_gemini():
    """Configures Gemini API with the stored API key."""
    api_key = load_api_key()
    if api_key:
        genai.configure(api_key=api_key)
    else:
        print("Failed to load API key! Exiting...")
        exit()

# Function to generate AI interview questions
def generate_interview_question(role, company, experience, difficulty, conversation_history):
    """Generates an adaptive interview question using Gemini AI."""
    prompt = f"""
    You are an AI interviewer for a {role} position at {company}.
    The candidate has {experience} experience. Difficulty: {difficulty}

    Previous conversation:
    {conversation_history}

    Based on this, ask the next most relevant question.
    - EASY: General questions.
    - MEDIUM: Questions requiring reasoning.
    - HARD: Deep technical or situational questions.

    Adjust follow-ups based on the candidate's previous response.
    """
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Function to analyze the user's response
def analyze_response(user_response):
    """Analyzes the user's response and provides feedback."""
    word_count = len(user_response.split())
    clarity, depth, relevance = 0, 0, 0
    
    if word_count < 5:
        clarity = 1
    elif word_count < 15:
        clarity = 2
    else:
        clarity = 3
    
    if "example" in user_response.lower() or "experience" in user_response.lower():
        depth = 3
    elif word_count > 20:
        depth = 2
    else:
        depth = 1
    
    if "I don't know" in user_response.lower():
        relevance = 1
    elif word_count > 10:
        relevance = 3
    else:
        relevance = 2
    
    total_score = clarity + depth + relevance

    feedback = "Try to elaborate more." if total_score <= 3 else \
               "Good effort! Add more depth." if total_score <= 6 else \
               "Great response! Well-structured and detailed."

    return clarity, depth, relevance, total_score, feedback

# Function to convert text to speech
def speak_text(text, offline=False):
    """Speaks text using either offline or online TTS."""
    if offline:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        tts = gTTS(text=text, lang='en')
        tts.save("question.mp3")
        os.system("start question.mp3" if os.name == "nt" else "mpg321 question.mp3")

# Function to capture speech input
def get_speech_input():
    """Captures and processes speech input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak your response:")
        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                audio = recognizer.listen(source)
                return recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                print("Could not understand. Please try again.")
            except sr.RequestError:
                print("Speech service unavailable. Please type your response.")
                return input("Your answer: ")

# Function to show the final performance summary
def show_performance_summary(responses):
    """Calculates and displays the performance summary."""
    total_score = sum(responses.values())
    max_score = len(responses) * 9  # Max 9 points per question
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0

    print("\n--- Performance Summary ---")
    print(f"Total Score: {total_score}/{max_score} ({percentage:.2f}%)")

    if percentage >= 80:
        print("🌟 Excellent performance! You are well-prepared.")
    elif percentage >= 50:
        print("👍 Good effort! Work on refining your responses.")
    else:
        print("⚠️ Needs improvement. Try providing more detailed answers.")

    with open("interview_results.json", "w") as file:
        json.dump(responses, file, indent=4)
    print("Results saved to interview_results.json")

# Main function to run the interview simulation
def main():
    setup_gemini()  # Initialize API

    # User input for interview setup
    role = input("Enter job role: ")
    company = input("Enter company name: ")
    experience = input("Enter experience level (Junior/Mid/Senior): ")
    difficulty = input("Choose difficulty level (Easy/Medium/Hard): ").capitalize()

    conversation_history = ""
    responses = {}

    while True:
        question = generate_interview_question(role, company, experience, difficulty, conversation_history)
        print("\nAI Interviewer:", question)
        speak_text(question, offline=True)

        print("Speak your answer or type below:")
        user_response = get_speech_input()
        print("You said:", user_response)

        if user_response.lower() in ["exit", "quit"]:
            break

        # Analyze the response
        clarity, depth, relevance, total_score, feedback = analyze_response(user_response)
        print("\n🔎 Feedback:", feedback)
        print(f"📊 Score Breakdown -> Clarity: {clarity}, Depth: {depth}, Relevance: {relevance}")

        conversation_history += f"\nAI: {question}\nCandidate: {user_response}\nFeedback: {feedback}\n"
        responses[question] = total_score

    show_performance_summary(responses)

if __name__ == "__main__":
    main()
