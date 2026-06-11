import os
from dotenv import load_dotenv

try:
    import google.generativeai as gai
except Exception:
    gai = None

load_dotenv()


def main():
    if not gai:
        print('google.generativeai not installed; skipping Gemini test')
        return

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print('GEMINI_API_KEY not set; skipping Gemini test')
        return

    try:
        gai.configure(api_key=api_key)

        print("Listing available Gemini models:")
        available_models = []
        for m in gai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"  - {m.name} (supports generateContent)")
        
        desired_model = 'gemini-2.0-flash-lite'
        if desired_model not in available_models and f"models/{desired_model}" not in available_models:
            print(f"\nWarning: '{desired_model}' or 'models/{desired_model}' was not explicitly found in your available models.")
            print("Please review the list above and update 'self.model_name' in 'services/gemini_assistant.py' and 'services/analyzer.py' to an available model that supports 'generateContent'.")
            # Attempt with gemini-2.5-flash-lite as a common fallback
            if 'gemini-2.5-flash-lite' in available_models or 'models/gemini-2.5-flash-lite' in available_models:
                desired_model = 'gemini-2.5-flash-lite'
                print(f"Attempting to use 'gemini-2.5-flash-lite' as a fallback for the test.")
            else:
                print("No suitable fallback model ('gemini-2.5-flash-lite') found. Skipping content generation test.")
                return # Exit if no suitable model is found for testing
        
        gai.configure(api_key=api_key)
        model = gai.GenerativeModel(desired_model)
        response = model.generate_content(
            "Say hello in one sentence.",
            generation_config=gai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=50,
            )
        )
        print(response.text)
    except Exception as e:
        print(f'Error calling Gemini API: {e}')
        print("Please ensure your GEMINI_API_KEY is correct, the model is available in your region, and you have sufficient quota.")

if __name__ == "__main__":
    main()
