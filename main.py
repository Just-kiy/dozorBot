# -*- coding: utf-8 -*-
import telepot, datetime, time, sys, os, json
from pprint import pprint

BOT_TOKEN = "178002319:AAE8RLeChZH8uEPT5ooeJ-N4IsD0ZwUrmFA"
ADMIN_ID = 82691326
SECRET_WORD = u"TESTWORD"
SECRET_CODES = [u'TE', u'ST', u'WO', u'RD']
SECRET_COUNT = len(SECRET_CODES)
BAD_MSG = u": код не принят"
GOOD_MSG = u": код принят! Ждите следующую загадку"
START_MSG = u"Внимание, команды! Квест начался! Время пошло!"
STOP_MSG = u"Внимание, команды! Квест окончен! Всем командам вернутся на базу!"


def jdefault(o):
    return o.__dict__


class Team:
    def __init__(self, name, user_id, solved = 0, riddles = SECRET_CODES, is_word = False, has_ended = False, timer = 0, offset = 0):
        self.name = name
        self.owner_id = user_id
        self.solved = solved
        self.riddles = riddles
        self.is_word = is_word
        self.has_ended = has_ended
        self.timer = timer
        self.position = offset


class Game:
    def __init__(self, game_name, riddles, teams = []):
        self.game_name = game_name
        self.isGoing = False
        self.teams = teams
        self.timer = 0
        self.riddles = riddles
        self.black_list = []
        # self.has_ended = False

    def start_quest(self):
        if not self.isGoing:
            self.isGoing = True
            self.timer = time.time()
            for t in self.teams:
                t.timer = time.time()
                bot.sendMessage(t.owner_id, START_MSG)

    def stop_quest(self):
        try:
            self.isGoing = False
            self.timer = time.time() - self.timer
            for t in self.teams:
                t.timer = time.time() - t.timer
                t.has_ended = True
                bot.sendMessage(t.owner_id, STOP_MSG)
        except Exception as e:
            print e

    def find_team(self, user_id):
        for t in self.teams:
            if user_id == t.owner_id:
                return t
        return False

    def check_code(self, team, code):
        user_id = team.owner_id
        response = code
        code = code.upper()
        if not team.has_ended:
            if not team.is_word:
                if team.riddles.keys()[team.position].upper() == code.upper():
                    response += GOOD_MSG
                    bot.sendMessage(user_id, response)
                    team.solved += 1
                    team.position = (team.position + 1) % len(riddles)
                    self.sync_json()
                    if team.solved == len(riddles):
                        team.is_word = True
                        bot.sendMessage(user_id, 'Введите полное кодовое слово:')
                    else:
                        bot.sendMessage(user_id, team.riddles[code.upper()])
                else:
                    response += BAD_MSG
                    bot.sendMessage(user_id, response)
            else:
                if code != SECRET_WORD:
                    response += BAD_MSG
                    bot.sendMessage(user_id, response)
                else:
                    team.timer = time.time() - team.timer
                    team.has_ended = True
                    bot.sendMessage(user_id, "Поздравляем, вы прошли квест!\nВаше время: {0} секунд".format(team.timer))
        else:
            bot.sendMessage(team.owner_id, 'Вы уже прошли квест!')

    def __register(self, user_id, text):
        if not (user_id in self.black_list):
            if len(text) == 2:
                if not self.is_registered(user_id):
                    if not self.isGoing:
                        self.register_team(user_id, text[1])
                        bot.sendMessage(user_id, 'Вы успешно зарегестрированы!')
                    else:
                        bot.sendMessage(user_id, 'Квест уже идет!')
                else:
                    bot.sendMessage(user_id, 'Вы уже зарегестрированы на квест!')
            else:
                bot.sendMessage(user_id, 'Пожалуйста, введите /register и название команды')

    def register_team(self, user_id, team_name):
        new_team = Team(team_name, user_id, riddles=self.riddles, offset=len(self.teams))
        self.teams.append(new_team)
        self.sync_json()

    def sync_json(self):
        try:
            fT = open('RegisteredTeams.json', 'r+', encoding='utf8')
            fT.truncate(0)
            for t in self.teams:
                fT.write(json.dumps(t, default=jdefault))
            fT.flush()
            fT.close()
        except Exception as e:
            print e

    def is_registered(self, user_id):
        for t in self.teams:
            if t.owner_id == user_id:
                return True
        return False

    def del_team(self, name):
        for t in self.teams:
            if t.name == name:
                bot.sendMessage(t.owner_id, 'Ваша команда была исключена! Обратитесь к организаторам!')
                self.black_list.append(t.owner_id)
                self.teams.remove(t)
                self.sync_json()
                return True
        return False

    def print_teams(self, user):
        message = [t.name for t in self.teams]
        bot.sendMessage(user["id"], message)

    def print_status(self, user_id):
        message = {t.name : t.solved for t in self.teams}
        bot.sendMessage(user_id, message)

    def handle_message(self, msg):
        try:
            user = msg['from']
            text = msg['text'].split()
            pprint(msg)
            team = self.find_team(user['id'])
            if msg.has_key('entities'):
                pprint(msg['entities'][0]['type'])
                if text[0] == '/register':
                    self.__register(user['id'], text)
                elif user['id'] == ADMIN_ID:
                    if text[0] == '/del':
                        self.del_team(text[1])
                    elif text[0] == '/status':
                        self.print_status(user['id'])
                    elif text[0] == '/start_quest':
                        self.start_quest()
                    elif text[0] == '/stop_quest':
                        self.stop_quest()
                    else:
                        bot.sendMessage(user['id'], 'Введена неправильная команда!')
                else:
                    bot.sendMessage(user['id'], 'У вас нет прав для выполнения этой команды!')
            else:
                if self.isGoing:
                    self.check_code(team, text[0])
                else:
                    bot.sendMessage(user['id'], 'Квест еще не начался!')
        except Exception as e:
            print e


#====================MAIN=============================#


if __name__ == '__main__':
    f = open("ReceivedMessages.log", 'w')
    #fTeams = open("RegisteredTeams.json", 'r+')
    fRid = open('Riddles.json', 'r+')
    riddles = json.loads(fRid.readline())
    #teams = json.loads(fTeams.readline())
    # pprint(teams)
    pprint(riddles)
    print(type(riddles))
   # fTeams.close()
    quest = Game('Hogwarts quest', riddles=riddles)
    bot = telepot.Bot(BOT_TOKEN)
    bot.message_loop(quest.handle_message)
    f.close()

    print 'Listening...'
    while 1:
        time.sleep(1)

