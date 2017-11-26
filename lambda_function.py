from __future__ import print_function
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-8187642a-d207-11e7-91cc-2ef9da9e0d0e'
pnconfig.secure_key = 'sec-c-ODRkZmI4NzUtMmRjZi00Y2M2LWExM2UtMGZhYjM3ZTZlMjUy'
pnconfig.publish_key = 'pub-c-3f7415bc-3090-4b10-ba90-1e27ee928302'

pubnub = PubNub(pnconfig)

def my_publish_callback(envelope, status):
   # Check whether request successfully completed or not
   if not status.is_error():
       pass  # Message successfully published to specified channel.
   else:
       pass  # Handle message publish error. Check ‘category’ property to find out possible issue
       # because of which request did fail.
       # Request can be resent using: [status retry];

class MySubscribeCallback(SubscribeCallback):
   def presence(self, pubnub, presence):
       pass  # handle incoming presence data

   def status(self, pubnub, status):
       if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
           pass  # This event happens when radio / connectivity is lost

       elif status.category == PNStatusCategory.PNConnectedCategory:
           # Connect event. You can do stuff like publish, and know you’ll get it.
           # Or just use the connected event to confirm you are subscribed for
           # UI / internal notifications, etc
           pubnub.publish().channel("photo").message("hello!!").async(my_publish_callback)
       elif status.category == PNStatusCategory.PNReconnectedCategory:
           pass
           # Happens as part of our regular operation. This event happens when
           # radio / connectivity is lost, then regained.
       elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
           pass
           # Handle message decryption error. Probably client configured to
           # encrypt messages and on live data feed it received plain text.

   def message(self, pubnub, message):
       print(message.message)
       pass  # Handle new message stored in message.message

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Oxford Hackathon Personal Therapist. Tell me how you feel today!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can say thinks like 'I am Emotion great', 'My day is going terrible' or other variations of the text."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_health_status_intent(intent, session):
    session_attributes = {}
    card_title = "Welcome"
    should_end_session = False

    if 'Emotion' in intent['slots']:
        favorite_color = intent['slots']['Emotion']['value']
        session_attributes = {}
        speech_output = "Okay, I have noted your feeling as " + favorite_color + " and taken a picture. I will add this to your online log."
        reprompt_text = "I didn't quite get that, please repeat!"

        pubnub.publish().channel('photo').message(favorite_color).async(my_publish_callback)
    else:
        speech_output = "I'm not sure how you are Emotion. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "Tell me how you feel by saying I feel great."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

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
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SubmitHealthIntent":
        return get_health_status_intent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
