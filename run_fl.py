from flask import Flask, request

import settings
from utils import db
import telegram
from coming_bot import build_bot

app = Flask(__name__)
bot = None

@app.route("/comingbot/{0}".format(settings.TG_API_KEY), methods=['GET', 'POST'])
def post():
    message = request.json.message
    if message.text.startswith('/new'):
        bot.new_cmd(message)

if __name__ == "__main__":
    session = db.load_session(settings.MYSQL_ENGINE)
    bot = build_bot(session, settings.TG_API_KEY)
    app.run()
