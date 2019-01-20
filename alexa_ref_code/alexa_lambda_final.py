"""
Code regarding integration with Amazon Alexa
"""

from __future__ import print_function
import http.client, json, sys


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- API call functions -------------------------------------------
def api_call(question_text):
    host = "qna-amazon.azurewebsites.net"
    endpoint_key = "b30d0328-c4c5-4720-98d1-ef59d5844382"
    route = "/qnamaker/knowledgebases/6e80dd6f-807a-45ce-ab70-dd4a2cf0ea92/generateAnswer"

    # question_text = "terms and conditions"

    question_to_kb = "{'question': '" + question_text + "','top': 1}"

    try:
        headers = {'Authorization': 'EndpointKey ' + endpoint_key,
                   'Content-Type': 'application/json'}
        conn = http.client.HTTPSConnection(host, port=443)
        conn.request("POST", route, question_to_kb, headers)
        response = conn.getresponse()
        kb_reply = response.read()
        kb_reply = json.loads(kb_reply)
        kb_reply = kb_reply['answers'][0]['answer']
        # print(json.dumps(kb_reply, indent=4))
        if kb_reply != 'No good match found in KB.':
            return (kb_reply)
        else:
            return ('No matching section found in agreement. Please try again.')

    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("Unexpected error:", sys.exc_info()[1])


# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Privacy Expert, your one-stop guide to complex service agreements. " \
                    "What is your question?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your query"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Privacy Expert. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def handle_fallback():
    session_attributes = {}
    card_title = "Fallback"
    speech_output = "The Privacy Expert skill can't help with that, but I can help you review the data policy uploaded on our website."
    should_end_session = False
    reprompt_text = "Please tell me your query"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def answer_question(intent, session):
    session_attributes = {}

    question_text = intent["slots"]["question"]["value"]

    reprompt_text = "What other questions about the data policy can I help you with?"
    speech_output = api_call(question_text) + ". " + reprompt_text  # Automatically followup with a reprompt
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "QuestionIntent":
        return answer_question(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "AMAZON.FallbackIntent":
        return handle_fallback()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.d466a9a2-b81c-4933-ba4c-87927283793d"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])