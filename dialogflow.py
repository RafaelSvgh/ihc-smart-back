from google.cloud import dialogflow_v2 as dialogflow
import os


PROJECT_ID = os.getenv("PROJECT_ID")
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE")


def enviar_a_dialogflow(texto_usuario, session_id="backend-session"):
    client = dialogflow.SessionsClient()
    session = client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=texto_usuario, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)

    response = client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    fulfillment_text = response.query_result.fulfillment_text
    return fulfillment_text
