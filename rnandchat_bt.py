import json
import numpy as np
from difflib import get_close_matches
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question, questions):
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str or None:
    similar_questions = get_close_matches(question, [q["question"].lower() for q in knowledge_base["question"]], n=1, cutoff=0.6)
    if similar_questions:
        question = similar_questions[0]
    for q in knowledge_base["question"]:
        if q["question"].lower() == question:
            return q['answer']

class ChatBotApp(App):
    def build(self):
        self.knowledge_base = load_knowledge_base('mente.json') #Ruta donde esta ubicado el archivo JSON
        self.unanswered_question = None
        self.unanswered_answer = None
        self.banned_words = ["tonto", "tarado", "chela", "jonca", "idiota", "estupido", "chilindrina"]

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(0.9, 0.9))

        self.chat_history = TextInput(hint_text='Chat History', readonly=True, multiline=True, size_hint=(1, 0.8))
        user_input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        self.user_input_text = TextInput(hint_text='Hola soy tu chatbot!!\nInicia el Chat con una pregunta', multiline=False, size_hint=(0.8, 1))
        send_button = Button(text='Enviar', size_hint=(0.2, 1))
        send_button.bind(on_release=self.send_user_input)

        user_input_layout.add_widget(self.user_input_text)
        user_input_layout.add_widget(send_button)

        layout.add_widget(self.chat_history)
        layout.add_widget(user_input_layout)

        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        return layout

    def send_user_input(self, instance):
        user_input = self.user_input_text.text.strip()
        self.user_input_text.text = ""

        if self.contains_banned_word(user_input):
            return

        if user_input.lower() == "adios":
            self.add_to_chat_history(f"Usuario: {user_input}")
            self.add_to_chat_history("Bot: ¡Adiós!")
            App.get_running_app().stop()
        elif "diabetes" in user_input.lower():
            # Menciona "diabetes", mostrar un cuadro de diálogo para obtener los datos
            self.show_diabetes_dialog()
        else:
            # Se manseja en las entrads de usuario
            self.add_to_chat_history(f"Usuario: {user_input}")
            best_match = find_best_match(user_input, [q["question"] for q in self.knowledge_base["question"]])

            if best_match:
                answer = get_answer_for_question(best_match, self.knowledge_base)
                self.add_to_chat_history(f'Bot: {answer}')
            else:
                self.unanswered_question = user_input
                self.add_to_chat_history('Bot: No sé la respuesta. ¿Puede enseñármela?')

    def contains_banned_word(self, text):
        banned_word_found = any(word.lower() in text.lower() for word in self.banned_words)
        if banned_word_found:
            self.add_to_chat_history(f'Bot: Palabra prohibida detectada en: {text}')
        return banned_word_found

    def add_to_chat_history(self, text):
        current_history = self.chat_history.text
        self.chat_history.text = f'{current_history}\n{text}'

    def show_diabetes_dialog(self):
        # Cuadro de dialogo diabetes
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text='Ingrese la edad:'))
        age_input = TextInput(multiline=False)
        content.add_widget(age_input)
        content.add_widget(Label(text='Ingrese el índice de masa corporal (bmi):'))
        bmi_input = TextInput(multiline=False)
        content.add_widget(bmi_input)
        content.add_widget(Label(text='Ingrese el nivel de glucosa en la sangre:'))
        glucose_input = TextInput(multiline=False)
        content.add_widget(glucose_input)

        button = Button(text='Aceptar')
        content.add_widget(button)

        # Crear el cuadro de diálogo
        popup = Popup(title='Datos para la detección de diabetes', content=content, size_hint=(None, None), size=(400, 300))

        # Funcion que ejecutará al presionar el botonn
        def on_button_click(instance):
            age = float(age_input.text)
            bmi = float(bmi_input.text)
            glucose_level = float(glucose_input.text)

            # Ejecutar la lpgica de deteccion de diabetes
            result = self.detect_diabetes(age, bmi, glucose_level)
            self.add_to_chat_history(f'Bot: {result}')

            # Cierra cuadro de dialog
            popup.dismiss()

        button.bind(on_press=on_button_click)

        # Mostrar el cuadro de diálogo
        popup.open()

    def detect_diabetes(self, age, bmi, glucose_level):
        # Lógica de detección de diabetes
        input_data = np.array([age, bmi, glucose_level]) #age,bmi,glucosa algunos de los datos principales para detectar diabetes, 

        def step_function(x):
            return 1 if x >= 0 else 0

        def perceptron(input_data, weights):
            weighted_sum = np.dot(input_data, weights)
            output = step_function(weighted_sum)
            return output

        weights = np.array([0.5, 0.5, 0.5])

        if input_data[0] > 35 and input_data[1] >= 25.0 or input_data[2] >= 126:
            return "Es probable que tenga diabetes."
        else:
            return "Es poco probable que tenga diabetes."

if __name__ == '__main__':
    ChatBotApp().run()
