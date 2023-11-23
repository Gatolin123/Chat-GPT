const Alexa = require('ask-sdk-core');
const openai = require('openai');

// Configure your OpenAI API key
openai.api_key = "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";

const messages = [{"role": "system", "content": "Responde de manera clara y concisa en español."}];

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speakOutput = "Bienvenido al Chat GPT. ¿Qué deseas aprender?";
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const GptQueryIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GptQueryIntent';
    },
    handle(handlerInput) {
        const query = handlerInput.requestEnvelope.request.intent.slots["query"].value;
        const response = generateGptResponse(query, messages);

        return handlerInput.responseBuilder
            .speak(response)
            .reprompt("¿Tienes alguna otra pregunta o deseas continuar con el tema?")
            .getResponse();
    }
};

const CatchAllExceptionHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        console.error(`Error: ${error.message}`);
        const speakOutput = "Disculpa, no entendí tu pregunta. Intenta preguntar de otra manera.";

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};

const CancelOrStopIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
                || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
    },
    handle(handlerInput) {
        const speakOutput = "Saliendo del modo Chat GPT.";
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

function generateGptResponse(query, messages) {
    try {
        messages.push({ "role": "user", "content": query });
        const response = openai.ChatCompletion.create({
            model: "gpt-3.5",
            messages: messages,
            max_tokens: 1000,
            n: 1,
            stop: null,
            temperature: 0.5
        });
        const reply = response['choices'][0]['message']['content'].trim();
        messages.push({ "role": "assistant", "content": reply });
        return reply;
    } catch (e) {
        return `Error al generar la respuesta: ${e.toString()}`;
    }
}

exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(
        LaunchRequestHandler,
        GptQueryIntentHandler,
        CancelOrStopIntentHandler
    )
    .addErrorHandlers(CatchAllExceptionHandler)
    .lambda();
