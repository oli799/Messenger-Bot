# Python libraries that we need to import for our bot
import random
import os
import pyowm
import wikiquotes
from flask import Flask, request
from pymessenger.bot import Bot

# Variables
commands = "You can use the following commands in this bot:\n\n1. Hi - The bot greet you \n2. Weather - the bot displays the current weather\n3. help/menu - The bot displays the commands\n4. Quote- the bot display a random quote"

# Variables

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        msg = message['message'].get('text')

                        response_sent_text = ""
                        response_sent_text = choose_response_text(msg)

                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

# chooses a random message to send to the user


def get_message():
    sample_responses = ["Hey!", "Hello!",
                        "How are you?"]
    # return selected item to the user
    return random.choice(sample_responses)

# uses PyMessenger to send response to user


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

# get the water data from OWM api


def get_weather(city):
    # TODO: handling wrong city input from the user
    try:
        owm = pyowm.OWM('1a4b6b94818486e559a01ec1fb90bfba')
        observation = owm.weather_at_place(city)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')

        weather = ("The temperature in (" +
                   str(city) + ") is : " + str(temp['temp']) + " °C")
        return weather
    except:
        return "This city is not available!"


def get_quote():
    quote = wikiquotes.random_quote("Aristotle", "english")
    return quote


def choose_response_text(msg):

    # TODO: create a funtion for sending news to users
    response_text = ""

    if(len(str(msg).split(" ")) == 2):
        key, city = msg.split(" ")
    if key.lower() == "weather":
        response_text = get_weather(city)
    elif msg.lower() == 'hi':
        response_text = "Yo!"
    elif msg.lower() == "help" or msg.lower() == "menu":
        response_text = commands
    elif msg.lower() == "quote":
        response_text = get_quote()
    else:
        response_text = get_message()

    return response_text


if __name__ == "__main__":
    app.run()
