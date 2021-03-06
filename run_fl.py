from flask import Flask, request

import settings
import json
from utils import db
import telegram
from coming_bot import build_bot

app = Flask(__name__)
bot = None

@app.route("/comingbot/{0}".format(settings.TG_API_KEY), methods=['GET', 'POST'])
def post():
    body = request.json
    message = telegram.Update.de_json(body).message
    if message and message.text is not None:
        cmd = message.text.lower()
        if cmd.startswith('/new'):
            bot.new_cmd(message)
        elif cmd.startswith('/yes'):
            bot.yes_cmd(message)
        elif cmd.startswith('/no'):
            bot.no_cmd(message)
        elif cmd.startswith('/who'):
            bot.who_cmd(message)
        elif cmd.startswith('/maybe'):
            bot.maybe_cmd(message)
    return json.dumps(body)

if __name__ == "__main__":
    session = db.load_session(settings.MYSQL_ENGINE)
    bot = build_bot(session, settings.TG_API_KEY)
    app.run()
else:
    session = db.load_session(settings.MYSQL_ENGINE)
    bot = build_bot(session, settings.TG_API_KEY)
