import logging
import ask_sdk_core.utils as ask_utils
import openai
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Configura tu clave de API de OpenAI
openai.api_key = "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"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

messages = [{"role": "system", "content": "Responde de manera clara y concisa en español."}]

class LaunchRequestHandler(AbstractRequestHandler):
    """Manejador para el inicio de la habilidad."""
    def can_handle(self, handler_input):
        # tipo: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # tipo: (HandlerInput) -> Response
        speak_output = "Bienvenido al Chat GPT. ¿Qué deseas aprender?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    """Manejador para la intención de consulta de GPT."""
    def can_handle(self, handler_input):
        # tipo: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # tipo: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = generate_gpt_response(query, messages)

        return (
                handler_input.response_builder
                    .speak(response)
                    .ask("¿Tienes alguna otra pregunta o deseas continuar con el tema?")
                    .response
            )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Manejo genérico de errores para capturar cualquier error de sintaxis o enrutamiento."""
    def can_handle(self, handler_input, exception):
        # tipo: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # tipo: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Disculpa, no entendí tu pregunta. Intenta preguntar de otra manera."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Manejador único para la intención de Cancelar y Detener."""
    def can_handle(self, handler_input):
        # tipo: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # tipo: (HandlerInput) -> Response
        speak_output = "Saliendo del modo Chat GPT."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def generate_gpt_response(query, messages):
    try:
        messages.append(
            {"role": "user", "content": query},
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5",
            messages=messages,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5
        )
        reply = response['choices'][0]['message']['content'].strip()
        messages.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"Error al generar la respuesta: {str(e)}"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
