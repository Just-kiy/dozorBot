# -*- coding: utf-8 -*-
import telepot, datetime, time, sys, os, json
from pprint import pprint

BOT_TOKEN = "178002319:AAE8RLeChZH8uEPT5ooeJ-N4IsD0ZwUrmFA"
ADMIN_ID = 82691326
SECRET_WORD = u"TESTWORD"
SECRET_CODES = [u'TE', u'ST', u'WO', u'RD']
SECRET_COUNT = len(SECRET_CODES)
BAD_MSG = u": код не принят"
GOOD_MSG = u": код принят"
START_MSG = u"Внимание, команды! Квест начался! Время пошло!"
STOP_MSG = u"Внимание, команды! Квест окончен! Всем командам вернутся на базу!"


def jdefault(o):
    return o.__dict__


class Team:
    def __init__(self, name, user_id):
        self.name = name
        self.owner_id = user_id
        self.solved = 0
        self.list_of_codes = SECRET_CODES
        self.is_word = False
        self.has_ended = False
        self.timer = 0

class Game:
    def __init__(self, game_name):
        self.isGoing = False
        # self.has_ended = False
        self.teams = []
        self.timer = 0
        self.game_name = game_name
    def start_quest(self):
        if self.isGoing != True:
            self.isGoing = True
            self.timer = time.time()
            for t in self.teams:
                t.timer = time.time()
                bot.sendMessage(t.owner_id, START_MSG)
        else:
            bot.sendMessage(user_id, 'Квест уже запущен!')
    def stop_quest(self):
        self.isGoing = False
        self.timer = time.time() - self.timer()
        for t in self.teams:
            t.timer = time.time() - t.timer
            t.has_ended = True
            bot.sendMessage(t.owner_id, STOP_MSG)
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
                    if code.upper() in team.list_of_codes:
                        response += GOOD_MSG
                        bot.sendMessage(user_id, response)
                        team.solved += 1
                        team.list_of_codes.remove(code)
                        if team.solved == SECRET_COUNT:
                            team.is_word = True
                            bot.sendMessage(user_id, 'Введите полное кодовое слово:')
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
        newteam = Team(team_name, user_id)
        self.teams.append(newteam)
        # try:
            # fTeams.truncate(0)
            # for t in self.teams:
                # fTeams.write(json.dumps(t, default = jdefault))
            # fTeams.flush()
        # except Exception as e:
            # print e
    def is_registered(self, user_id):
        for t in self.teams:
            if t.owner_id == user_id:
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
                    if text[0] == '/teams':
                        self.print_teams(user)
                    elif text[0] == '/status':
                        self.print_status(user['id'])
                    elif text[0] == '/start_quest':
                        self.start_quest()
                    elif text[0] == '/stop_quest':
                        pass
                    else:
                        bot.sendMessage(user['id'], 'Введена неправильная команда!')
                else:
                    bot.sendMessage(user['id'], 'У вас нет прав для выполнения этой команды!')
            else:
                if self.isGoing == True:
                    self.check_code(team, text[0])
                else:
                    bot.sendMessage(user['id'], 'Квест еще не начался!')
        except Exception as e:
            print e



#====================MAIN=============================#
if __name__ == '__main__':
    f = open("ReceivedMessages.log", 'w')
    fTeams = open("RegisteredTeams.json", 'r+')
    quest = Game('temp quest')
    teams = json.loads(fTeams.readline())
    bot = telepot.Bot(BOT_TOKEN)
    bot.message_loop(quest.handle_message)
    print 'Listening...'
    while 1:
        time.sleep(1)
    f.close()
    fTeams.close()
