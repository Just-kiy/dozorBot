# -*- coding: utf-8 -*-
import telepot, time, sys, random, os
from pprint import pprint

BOT_TOKEN = "178002319:AAE8RLeChZH8uEPT5ooeJ-N4IsD0ZwUrmFA"
SECRET_WORD = u"TESTWORD"
SECRET_CODES = [u'TE', u'ST', u'WO', u'RD']
SECRET_COUNT = len(SECRET_CODES)
teams = []
timer = 0



class team:
    def __init__(self, name, user_id):
        self.name = name
        self.owner_id = user_id
        self.solved = 0
        self.list_of_codes = SECRET_CODES
        self.is_word = False
        self.has_ended = False


def start_quest():

    pass


def find_team(user_id):
    for t in teams:
        if user_id == t.owner_id:
            return t
    return False


def check_code(_team, code):
    for c in _team.list_of_codes:
        if code.upper() == c:
            _team.solved += 1
            _team.list_of_codes.remove(c)
            return True
    return False


def is_registered(user_id):
    for t in teams:
        if t.owner_id == user_id:
            return True
    return False


def print_teams(user):
    message = [t.name.decode('unicode_escape') for t in teams]
    bot.sendMessage(user["id"], message)


def handle_message(msg):
    user = msg["from"]
    pprint(msg)
    text = msg["text"].split()
    current_team = find_team(user['id'])
    if "/" in text[0]:
        if text[0] == "/register":
            if len(text) == 2:
                bot.sendMessage(user["id"], "Perfect name!")
                new_team = team(text[1], user['id'])
                teams.append(new_team)
            else:
                bot.sendMessage(user["id"], "Please, type /register and the name of your team!")
        elif text[0] == "/status":
            pass
        elif text[0] == "/teams":
            print_teams(user)
        elif text[0] == "/start":
            start_quest()
    elif is_registered(user['id']):
        if not current_team.is_word:
            if check_code(current_team, text[0]):
                bot.sendMessage(user["id"], "Код '{0}' принят! Вы разгадали {1} загадок!".format(text[0], current_team.solved))
                if current_team.solved == SECRET_COUNT:
                    current_team.is_word = True
                    bot.sendMessage(user['id'], 'Введите полное кодовое слово:')
            else:
                bot.sendMessage(user['id'], "Код '{}' не принят".format(text[0]))
        else:
            if text[0] != SECRET_WORD:
                bot.sendMessage(user['id'], "Код '{}' не принят, попробуйте еще раз".format(text[0]))
            else:
                bot.sendMessage(user['id'], "Поздравляем, вы прошли квест!")

    else:
        bot.sendMessage(user['id'], 'You are not registered yet!')





#====================MAIN=============================#


f = open("ReceivedMessages.log", 'w')
bot = telepot.Bot(BOT_TOKEN)
bot.notifyOnMessage(handle_message)
print 'Listening...'

while 1:
    time.sleep(10)

f.close()
