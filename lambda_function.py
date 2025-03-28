"""
This is the Handler for the Mental List skill for Amazon Alexa. 
The skill was built with the Amazon Alexa tool kit following the model 
of the Simple Color Picker example skill.  
The Intent Schema, Custom Slots, and Sample Utterances for this skill are stored
in the Mental List directory of Google Docs for Ralph Galantine account

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import math
import dateutil.parser
import datetime
import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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
            'content': "Mental List says:  " + output
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
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "I am the Mental List, " \
                    "the mind reading friend of magicians.  " \
                    "How can I help?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I did not understand.  What would you like to know?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you magician."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def _cardReveal(intent, session):
    """
    fulfills the cardReveal intent
    """
    card_title = "The Card Revealed"
    sessionAttributes = {}
    should_end_session = False
    """Check each slot and supply default if there is no value
    """
    if "value" in intent["slots"]["request"]:
        _request = intent["slots"]["request"]["value"]
    else:
        _request = "tell me"
    if "value" in intent["slots"]["article"]:
        _article = intent["slots"]["article"]["value"]
    else:
        _article = "the"
    if "value" in intent["slots"]["courtesy"]:
        _courtesy = intent["slots"]["courtesy"]["value"]
    else:
        _courtesy = 'nothing'
    if "value" in intent["slots"]["value"]:
        _value = intent["slots"]["value"]["value"]
    else:
        _value = "card"
    _odd_indicator = 0
    _odd_after_divide = 0
    _base_number = 2
    _card_number = 1
    
    """   
    Source Checking from Lex--May not be needed here
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_cardReveal(_article,_courtesy,_value,_request)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
    # Pass suit and value back through session attributes
    # on the bot model.
    """
    
    #Determine the suit of the card based on the request
    
    if _request.lower()=='uncover':
        sessionAttributes['Suit'] = 'Clubs'
    elif _request.lower()=='reveal' or _request.lower()=='we veal' or _request.lower()=='weevil':
        sessionAttributes['Suit'] = 'Diamonds'
    elif _request.lower()=='tell me' or _request.lower()=='tell us':
        sessionAttributes['Suit'] = 'Hearts'
    else:
        sessionAttributes['Suit'] = 'Spades'
        
    #Determine odd or even based on courtesy please--odd, no please--even
                        
    if _courtesy.lower()=='please':
        _odd_indicator=1
      
    #Determine odd or even for card value divided by 2 based on "the"  for even "His"/"Her" for odd
    
    if _article.lower()=='the':
        _odd_after_divide=0
    else:
        _odd_after_divide=1
        
    #Determine the base number after dividing by two twice and accounting for odd and even
    if _value.lower()=='card':
        _base_number=0
    elif _value.lower()=='value':
        _base_number=1
    elif _value.lower()=='choice':
        _base_number=2
    else:
        _base_number=3
     
    #Calculate the number of the card   
    _card_number=((_base_number) * 2 + _odd_after_divide) * 2 + _odd_indicator
    
    """convert _card_number to string and face card values to string names Jack, Queen, King, Ace.
    can add handling for _card_number 0, 14, and 15 later.
    """
    
    if _card_number==13:
        sessionAttributes['Number'] = 'King'
    elif _card_number==12:
        sessionAttributes['Number'] = 'Queen'
    elif _card_number==11:
        sessionAttributes['Number'] = 'Jack'
    elif _card_number==1:
        sessionAttributes['Number'] = 'Ace'
    else:
        sessionAttributes['Number'] = str(_card_number)
        
    reprompt_text = None
    
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    
    should_end_session = True
 
    if _card_number==0:
        if sessionAttributes['Suit'] == 'Spades':
            speech_output='Joker!, Joker!, Joker!'
        elif sessionAttributes['Suit'] == 'Hearts':
            speech_output='The card is a blank or the mind is a blank.'
        elif sessionAttributes['Suit'] == 'Clubs':
            speech_output='A bishop is a chess piece, I am looking for a card.'
        else:
            speech_output='There is no zero of any suit, think of a real card.'
    elif _card_number==14:
        if sessionAttributes['Suit'] == 'Hearts':
            if _article.lower() == 'her':
                speech_output='The selector is thinking about the gentleman, not the card.  ' \
                'Everyone concentrate on the card and ask Alexa to summon me again.'
            else:
                speech_output='The selector is thinking about the lady, not the card.  ' \
                'Everyone concentrate on the card and ask Alexa to summon me again.'
        else:
            speech_output='The card is not coming through clearly, I need everyone to think about the card. ' \
            'Ask Alexa to summon me again.'
    elif _card_number==15:
        speech_output='There is no 15 of ' + sessionAttributes['Suit'] + '. Ask Alexa to summon me again.'
    else:
        speech_output='The selected card is the ' + sessionAttributes['Number'] + ' of ' + sessionAttributes['Suit']

    return build_response(sessionAttributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


"""  These were the color picker specific functions
def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    # Sets the color in the session and prepares the speech to reply to the
    # user.


    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

-----End of the color picker specific

"""

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
    if intent_name == "cardReveal":
        return _cardReveal(intent, session)
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
    This statement populates the skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.0a0ee56d-143c-4857-9cfa-a722299793b7"):
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