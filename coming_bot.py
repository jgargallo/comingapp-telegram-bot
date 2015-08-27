from models import *
from datetime import datetime
from sqlalchemy import desc
from collections import defaultdict
import logging
import telegram
import random

logger = logging.getLogger(__name__)

def build_bot(session, apikey):
    bot = telegram.Bot(apikey)
    bot.setWebhook('https://golean.do/comingbot/{0}'.format(apikey))
    return ComingBot(session, bot)

class ComingBot(object):

    yes_responses = (u'ok', u'nice', u'okay', u'cool', u'alright', u'yeah', u'see you there',)
    no_responses = (u'next time', u'oops', u'ouch',)
    maybe_responses = (u'no hurries', u'take your time',)

    def __init__(self, session, bot):
        self.session = session
        self.bot = bot

    def _get_chat_tuple(self, update):
        if not hasattr(update, 'chat'):
            return (None, False)
        chat_id = int(update.chat.id)
        chat_name = update.chat.title
        chat = self.session.query(Chat).get(chat_id)

        if not chat:
            chat = Chat(id=chat_id, name=chat_name, created=datetime.now())
            self.session.add(chat)

        return (chat, True)

    def _get_from_tuple(self, update):
        fr = update.from_user
        return (fr.id, fr.first_name)

    def new_cmd(self, update):
        if len(update.text) >= 6:
            try:
                now = datetime.now()
                event_name = update.text[5:].replace('\n', ' ')
                chat, chat_ok = self._get_chat_tuple(update)
                if not chat_ok:
                    return 'Sorry! this is a group bot'

                event = Event(name=event_name, chat=chat, created=now)
                self.session.add(event)

                self.session.commit()
                
                self.bot.sendMessage(chat_id=update.chat.id, 
                    text=u'\U0001F4C6 "{0}" created!'.format(event_name).encode('utf-8'))
            except Exception as ex:
                self.session.rollback()
                logger.error('new cmd: {0}'.format(ex))
        else:
            self.bot.sendMessage(chat_id=update.chat.id, 
                    text=u"Pick up a name: /new event_name")

    def _attend(self, update, status):
        try:
            now = datetime.now()
            chat, chat_ok = self._get_chat_tuple(update)
            if not chat_ok:
                return 'Sorry! this is a group bot'

            event = self.session.query(Event).filter_by(chat_id=chat.id) \
                    .order_by(desc(Event.created)).first()

            if not event:
                return 'Sorry, there is no event to attend, create one: "/new event_name"'

            fr = self._get_from_tuple(update)

            attendant = self.session.query(Attendant).get(fr[0])
            name = fr[1].replace('\n',' ')
            event_attendant = None
            if not attendant:
                attendant = Attendant(id=fr[0], name=name, created=now)
                self.session.add(attendant)
            else:
                if name != attendant.name:
                    attendant.name = name
                    self.session.add(attendant)
                event_attendant = self.session.query(EventAttendant) \
                        .filter_by(event_id=event.id, attendant_id=attendant.id) \
                        .first()

            if not event_attendant:
                event_attendant = EventAttendant(event=event, attendant=attendant)
                self.session.add(event_attendant)

            event_attendant.last_updated = now
            event_attendant.status = status

            self.session.commit()

            summary = self._get_summary(event)

            return (event, fr[1], summary)
        except Exception:
            self.session.rollback()

        return ""

    def _get_summary(self, event):
        atts = self.session.query(EventAttendant).filter_by(event_id=event.id) \
                .join(EventAttendant.attendant).all()
        summary = defaultdict(list)
        for ev_att in atts:
            summary[ev_att.status].append(ev_att.attendant.name)

        return summary

    def _print_summary(self, event_name, attendant_name, summary, chat_id):
        yes_str = no_str = maybe_str = nobody = ''
        if len(summary[1]) > 0:
            yes_str = u'\n\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\n\U0001F604 {0} coming:\n   \U0001F44D {1}'.format(str(len(summary[1])), 
                    u'\n   \U0001F44D '.join(summary[1]))
        if len(summary[0]) > 0:
            no_str = u'\n\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\n\U0001F61E {0} not coming:\n   \U0001F44E {1}'.format(str(len(summary[0])), 
                    u'\n   \U0001F44E '.join(summary[0]))
        if len(summary[2]) > 0:
            maybe_str = u'\n\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\U00003030\n\U0001F614 {0} maybe coming:\n   \U0001F449 {1}'.format(str(len(summary[2])), 
                    u'\n   \U0001F449 '.join(summary[2]))
        if len(summary[0]) == 0 and len(summary[1]) == 0 and len(summary[2]) == 0:
            nobody = u'\n\U0001F648 nobody answered yet'

        txt = u'\U0001F4C6 {0}{1}{2}{3}{4}' \
                .format(event_name, yes_str, no_str, maybe_str, nobody)
        self.bot.sendMessage(chat_id=chat_id, text=txt.encode('utf-8'))

    def yes_cmd(self, update):
        res = self._attend(update, 1)
        if not type(res) == str:
            #return self._print_summary(res[0].name, res[1], res[2], update.chat.id)
            self.bot.sendMessage(chat_id=update.chat.id, 
                    text=self.yes_responses[random.randrange(len(self.yes_responses))].encode('utf-8'))
        else:
            return res
    def no_cmd(self, update):
        res = self._attend(update, 0)
        if not type(res) == str:
            #return self._print_summary(res[0].name, res[1], res[2], update.chat.id)
            self.bot.sendMessage(chat_id=update.chat.id, 
                    text=self.no_responses[random.randrange(len(self.no_responses))].encode('utf-8'))
        else:
            return res
    def maybe_cmd(self, update):
        res = self._attend(update, 2)
        if not type(res) == str:
            #return self._print_summary(res[0].name, res[1], res[2], update.chat.id)
            self.bot.sendMessage(chat_id=update.chat.id, 
                    text=self.maybe_responses[random.randrange(len(self.maybe_responses))].encode('utf-8'))
        else:
            return res
    def who_cmd(self, update):
        chat, chat_ok = self._get_chat_tuple(update)
        if not chat_ok:
            return 'Sorry! this is a group bot'

        event = self.session.query(Event).filter_by(chat_id=chat.id) \
                .order_by(desc(Event.created)).first()

        if not event:
            return 'Sorry, there is no event to attend, create one: "/new event_name"'

        summary = self._get_summary(event)
        return self._print_summary(event.name, None, summary, update.chat.id)
