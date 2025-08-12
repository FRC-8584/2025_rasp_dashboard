from modules import Gemini

gemini = Gemini()

while True:
    print(gemini.get_current_status().depth)