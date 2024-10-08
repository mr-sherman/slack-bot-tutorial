import os
from dotenv import load_dotenv
from pathlib import Path
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import random

# Load Environment Vars -- Uncomment out for local debug.
#env_path = Path('./') / '.env'
#load_dotenv(dotenv_path=env_path)

slack_bot_token = os.environ['SLACK_BOT_TOKEN']
slack_app_token = os.environ['SLACK_APP_TOKEN']
app = App(token=slack_bot_token)

responses = [   "It is certain"
             ,  "It is decidedly so"
             ,  "Without a doubt"
             ,  "Yes definitely"
             ,  "You may rely on it"
             ,  "As I see it, yes"
             ,  "Most likely"
             ,  "Outlook good"
             ,  "Yes"
             ,  "Signs point to yes"
             ,  "Reply hazy, try again"
             ,  "Ask again later"
             ,  "Better not tell you now"
             ,  "Cannot predict now"
             ,  "Concentrate and ask again"
             ,  "Don't count on it"
             ,  "My reply is no"
             ,  "My sources say no"
             ,  "Outlook not so good"
             ,  "Very doubtful" ]

response_template = ":8ball: {user} has asked the Magic 8-Ball: `{question}`\nMy answer is: `{response}`"

def get_random_response(response_list):
    return response_list[random.randint(0,len(response_list)-1)]

def get_answer_from_question(user, question):
    return response_template.format(user=user, question=question, response=get_random_response(response_list = responses) )

@app.command('/magic-eightball')
def eightball_command(ack, body, client):
    ack('Asking the Magic 8-Ball')
    user_id = body["user_name"]
    channel_id = body ["channel_id"]
    text = body["text"]
    eightball_response = get_answer_from_question(user=user_id, question=text)
    resp = client.chat_postMessage(channel = channel_id, text = eightball_response, mrkdwn=True )

# MAIN
if __name__ == "__main__":
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()
