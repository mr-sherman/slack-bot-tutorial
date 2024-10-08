# Magic 8 Ball Slack Bot Tutorial
This is a fun Slack Bot to help you learn how to write slack bots and deploy them in a flexible way using Docker containers.
This tutorial uses Python.  If you prefer to use Javascript, there are other tutorials on the web to do that, but the set up for the bot is the same regardless of programming language.

## Setup
The first step is to create the app.
Go to https://api.slack.com/apps and click the "Create App" button.  
We don't have a manifest, so we'll be creating the app from scratch.

Give your app a name and select in which workspace you'll be creating the app.
Some information will be automatically created for you, such as the App ID, Client ID, Client Secret, Singing Secret, and verification token.

Next, this tutorial uses a bot in socket mode, meaning the bot makes a connection to the Slack service and not the other way around.  The default mode of a Slack bot is to wait for HTTP requests from Slack, validate that they're comming from the appropriate app and workspace, and then execute the desired action.  This means that you have to open up a port for traffic on your laptop through something like NGROK to debug, or allow public traffic in your cloud environment.  It's easier and more secure to have the bot initiate the connection, authenticate to the Slack environment, and then wait for messages and commands from Slack. 

If you want to distribute your bot to beyond your organization or Slack workspace, then it's not recommended to use socket mode, but this is a tutorial and meant for internal bots for your organization or company.

On the left-hand menu, click ``Socket Mode`` under ``Settings``.
Click the little slide button next to ``Enable Socket Mode``

You do have to give your bot permissions, or scopes, so scroll down to the section labeled ``App-Level Tokens`` and click ``Generate Token and Scopes``
Give it a name, i.e. ``magic_8_ball_token`` and select ``connections:write`` for its scope.
Copy the resulting token to a temporary text file somewhere, as you will need it when you start writing the actual code for the bot.  This will be refered to as your ``app token`` later.  

You'll get prompted to install the app to the Slack workspace.  Copy the bot user OAuth token and keep it in that temporary text file.  If at any point you need to retrieve this token again, you can find it on the left-hand menu under ``Features`` -> ``OAuth & Permissions``.  This will be referred to as your ``bot token`` later

Next, we have to create a command for users to ask the Magic 8 Ball Questions.  Under ``Features`` click ``Slash Commands``
Click the ``Create New Command`` button and fill out the command name, usage hints, and description, and then save the command.  For this tutorial, I used ``/magic-eightball``

Now you're ready to write code.


## Developing the Magic EightBall
This tutorial assumes you have a Python installation.  If you don't, that's a whole different tutorial.


### Dependencies
Create your ``requirements.txt`` file and the following two entries:
```
slack-bolt
python-dotenv

```
Save that, then do ``pip install -f requirement.txt``

### Setting up environment variables:
Create a file called ``.env`` with the following information in it.  Notice the no spaces in between the variable name and = and value
```
SLACK_BOT_TOKEN="<your slack bot token, starts with xoxb>"
SLACK_APP_TOKEN="<your slack app token, starts with xapp>"
```

### Implementation
Now create your bot file.  In my example, I called it ``magic-eightball.py``

First import some packages we will need.  
```
import os
from dotenv import load_dotenv
from pathlib import Path
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import random
```

Then set up how we will get our tokens.  Notice the comment about commenting those lines out before deployment.  Right now they're there so we can locally debug.

```
# Load Environment Vars -- Comment out the next two lines for deployment, uncomment for local debug
env_path = Path('./') / '.env'
load_dotenv(dotenv_path=env_path)
slack_bot_token = os.environ['SLACK_BOT_TOKEN']
slack_app_token = os.environ['SLACK_APP_TOKEN']
app = App(token=slack_bot_token)
```

Now let's create our responses and set up some helper functions to format the responses.  
Feel free to add or modify more responses.  I went with the original toy's list of possible responses
```
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

```

Now that we've set that up, let's tie everything together. First, we need to implement the slash command:

```
@app.command('/magic-eightball')
def eightball_command(ack, body, client):
    ack('Asking the Magic 8-Ball')
    user_id = body["user_name"]
    channel_id = body ["channel_id"]
    text = body["text"]
    eightball_response = get_answer_from_question(user=user_id, question=text)
    resp = client.chat_postMessage(channel = channel_id, text = eightball_response, mrkdwn=True )

```

Then, make your bot run, connect to slack and listen for when users type ``/magic-eightball``
```
# MAIN
if __name__ == "__main__":
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()
```

Now run or debug your magic-eightball.py file.  Go into slack, add the magic-eightball app to your channel and type:
``/magic-eightball does this work?``
If you get an answer, then it works!

## Deploying the magic eightball
We're going to create a container that can be used anywhere.  It can be run by a container service like AWS ECS, or Google Container Service.  It won't matter because we're not using anything proprietary from those providers.  

Create your Dockerfile:
```
FROM python:3.12

WORKDIR /python-docker

COPY ./magic-eightball.py magic-eightball.py
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python3", "-u" , "magic-eightball.py"]%
```

Notice that I didn't copy the .env file.  We don't want to copy it because it's for local debugging.  Copying that file would cause all those secret tokens to be in the actual image file, and that means anyone with access to that image would be able to view your tokens.  This is not a good security practice at all.

To be even more careful with your tokens you'll actually want to create a ``.gitignore`` file with:
```
.env
.venv
```
This will make it so your secrets don't end up in your source control if you ever do something like ``git add *``

Next, comment out the lines in ``magic-eightball.py`` that load the envrionment variables from the .env file:
```
# Load Environment Vars -- Comment out the next two lines for deployment, uncomment for debug
# env_path = Path('./') / '.env'
# load_dotenv(dotenv_path=env_path)
```

Save it, and let's build the docker image:

``docker build --tag magic-eightball .``

Since we don't include the .env file in the image, we have to pass the environment variables into the container when we run it.

``docker run magic-eightball -e SLACK_BOT_TOKEN="<slack bot token (starts with xoxb)>" -e SLACK_APP_TOKEN="<slack app token (starts with xapp)>"``

# Usage of the bot from Slack
Ask the Magic 8 Ball slack bot a question, and let it predict your fate.
**Warning**:  you may not like the answer
**Another Warning**:  you may have to ask it again

Usage:
``/magic-eightball <question>``


# Further exercises:
To really make this bot your own, here are some ideas that you may wish to explore on your own.
  * Add different responses, make them more relevant to your company or group, i.e. ``I don't know. Ask CEO Bob.``
  * Change the format of the response.  Use different emojies, different text styles
  * Instead of a slash command, make it so you can ask the bot with an @-mention, i.e. ``@magic-eightball am I able to do this exercise?``

For more information, you can find anything on the Slack API documentation.
Have fun, and use Slack bots to help your company and co-workers get stuff done!

