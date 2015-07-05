import telegram.botapi.botbuilder as botbuilder
from models import *
from datetime import datetime
from sqlalchemy import desc
from collections import defaultdict

def build_bot(session, apikey):
    coming_bot = ComingBot(session)
    return botbuilder.BotBuilder(apikey) \
        .send_message_when("new", coming_bot.new_cmd) \
        .send_message_when("yes", coming_bot.yes_cmd) \
        .send_message_when("no", coming_bot.no_cmd) \
        .send_message_when("maybe", coming_bot.maybe_cmd) \
        .send_message_when("view", coming_bot.view_cmd) \
        .build()

class ComingBot(object):

    def __init__(self, session):
        self.session = session

    def _get_chat_tuple(self, update):
        if not hasattr(update, 'chat'):
            return (None, False)
        chat_id = int(update.chat.id)
        chat_name = update.chat.title
        chat = self.session.query(Chat).get(chat_id)
        return (chat, True)

    def _get_from_tuple(self, update):
        fr = getattr(update, 'from')
        return (fr.id, fr.first_name)

    def new_cmd(self, update):
        if len(update.text) >= 6:
            try:
                now = datetime.now()
                event_name = update.text[5:].replace('\n', ' ')
                chat, chat_ok = self._get_chat_tuple(update)
                if not chat_ok:
                    return 'Sorry! this is a group bot'

                if not chat:
                    chat = Chat(id=chat_id, name=chat_name, created=now)
                    self.session.add(chat)

                event = Event(name=event_name, chat=chat, created=now)
                self.session.add(event)

                self.session.commit()

                return '"{0}" event created!'.format(event_name)
            except Exception:
                self.session.rollback()

            return ""
        else:
            return "Pick up a name: /new event_name"

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
            event_attendant = None
            if not attendant:
                attendant = Attendant(id=fr[0], name=fr[1].replace('\n',' '), created=now)
                self.session.add(attendant)
            else:
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

    def _print_summary(self, event_name, attendant_name, summary):
        yes_str = no_str = maybe_str = ''
        if len(summary[1]) > 0:
            yes_str = '\n\U0001F44D {0} coming:\n- {1}'.format(str(len(summary[1])), '\n- '.join(summary[1]))
        if len(summary[0]) > 0:
            no_str = '\n\U0001F44E {0} not coming:\n- {1}'.format(str(len(summary[0])), '\n- '.join(summary[0]))
        if len(summary[2]) > 0:
            maybe_str = '\n:point_right: {0} maybe coming:\n- {1}'.format(str(len(summary[2])), '\n- '.join(summary[2]))
        return 'Who is coming to "{0}" event?{1}{2}{3}' \
                .format(event_name, yes_str, no_str, maybe_str)

    def yes_cmd(self, update):
        res = self._attend(update, 1)
        return self._print_summary(res[0].name, res[1], res[2])
    def no_cmd(self, update):
        res = self._attend(update, 0)
        return self._print_summary(res[0].name, res[1], res[2])
    def maybe_cmd(self, update):
        res = self._attend(update, 2)
        return self._print_summary(res[0].name, res[1], res[2])
    def view_cmd(self, update):
        chat, chat_ok = self._get_chat_tuple(update)
        if not chat_ok:
            return 'Sorry! this is a group bot'

        event = self.session.query(Event).filter_by(chat_id=chat.id) \
                .order_by(desc(Event.created)).first()

        if not event:
            return 'Sorry, there is no event to attend, create one: "/new event_name"'

        summary = self._get_summary(event)
        return self._print_summary(event.name, None, summary)
