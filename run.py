
from utils import db
import settings

from coming_bot import build_bot
from requests.packages import urllib3

if __name__ == "__main__":
    urllib3.disable_warnings()
    
    session = db.load_session(settings.MYSQL_ENGINE)

    bot = build_bot(session, settings.TG_API_KEY)
    bot.start()


