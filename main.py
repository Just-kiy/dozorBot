# -*- coding: utf-8 -*-
import telepot, datetime, time, sys, os, json, collections
from pprint import pprint

class Msg():
	bad = ": код не принят"
	good = ": код принят! Ждите следующую загадку"
	bonus = 'Бонусный код принят'
	start = "Внимание, команды! Квест начался! Время пошло!"
	stop = "Внимание, команды, квест завершен!"
	restart = ''
	last = 'Последняя локация - актовый зал. Вас ждет последнее испытание'
	congart = 'Поздравляем, вы прошли квест! Ожидайте окончания квеста остальными участниками'

class Team(Object):
    def __init__(self, name, user_id, offset = 0):
        self.name = name
        self.owner_id = user_id
        self.solved = 0
        self.solved_bonus = 0
        self.is_word = False
        self.has_ended = False
        self.time_start = 0
        self.time_stop = 0
        self.start_position = offset
        self.cur_position = offset

    def now(self):
        tt = time.gmtime()
        __time = tt.tm_hour * 60 + tt.tm_min
        return __time

class Game(object):
    def __init__(self, game_name, riddles, teams = []):
        self.game_name = game_name
        self.isGoing = False
        self.teams = teams
        self.time_start = 0
        self.riddles = riddles
        self.black_list = []

    def start_quest(self):
        if not self.isGoing:
            self.isGoing = True
            self.time_start = time.time()
            for t in self.teams:

                bot.sendMessage(t.owner_id, start)

    def stop_quest(self):
        try:
            self.isGoing = False
            self.time_start = time.time() - self.time_start
            for t in self.teams:
               # t.timer = t.now() - t.timer
                t.has_ended = True
                bot.sendMessage(t.owner_id, stop)
        except Exception as e:
            print(e)

    def call_help(self, team):
        bot.sendMessage(ADMIN_ID, 'help {0}, location {1}'.format(team.name, team.cur_position + 1))

    def find_team(self, user_id):
        for t in self.teams:
            if user_id == t.owner_id:
                return t
        return False

    def check_code(self, team, code):
        user_id = team.owner_id
        response = code
        code = code.upper()
        lRid = self.riddles['riddles']
        # pprint(lRid)
        try:
            if not team.has_ended:
                if not team.is_word:
                    if lRid[str(team.cur_position)]['code'].upper() == code.upper():
                        response += Msg.good
                        bot.sendMessage(user_id, response)
                        team.solved += 1
                        cur_rid = lRid[str(team.cur_position)]['riddle']
                        team.cur_position = (team.cur_position + 1) % len(lRid) 
                        if team.solved == len(lRid):
                            team.is_word = True
                            bot.sendMessage(user_id, Msg.last)
                            # team.
                        else:
                            bot.sendMessage(user_id, cur_rid)
                    elif code.upper() in self.riddles['bonus']:
                        bot.sendMessage(user_id, Msg.bonus)
                        team.solved_bonus += 1
                        self.riddles['bonus'].remove(code.upper())
                        pprint(self.riddles['bonus'])
                    else:
                        response += Msg.bad
                        bot.sendMessage(user_id, response)
                else:
                    if code.upper() != self.riddles['secret'].upper():
                        response += Msg.bad
                        bot.sendMessage(user_id, response)
                    else:
                        team.time_stop = team.now()
                        team.has_ended = True
                        bot.sendMessage(user_id, Msg.congart)
                        bot.sendMessage(ADMIN_ID, 'Team {0} has finished!'.format(team.name))
                self.json_sync()
            else:
                bot.sendMessage(team.owner_id, 'Вы уже прошли квест!')
        except Exception as e:
            print(e)

    def __register(self, user_id, text):
        if not (user_id in self.black_list):
            if len(text) >= 2:
                if not self.is_registered(user_id):
                    if not self.isGoing:
                        self.register_team(user_id, '_'.join(text[1:]))
                        bot.sendMessage(user_id, 'Вы успешно зарегестрированы!')
                    else:
                        bot.sendMessage(user_id, 'Квест уже идет!')
                else:
                    bot.sendMessage(user_id, 'Вы уже зарегестрированы на квест!')
            else:
                bot.sendMessage(user_id, 'Пожалуйста, введите /register и название команды')

    def register_team(self, user_id, team_name):
        new_team = Team(team_name, user_id, offset=len(self.teams))
        self.teams.append(new_team)
        self.json_sync()

    def json_sync(self):
        try:
            fT = open('RegisteredTeams.json', 'r+')
            fT.truncate(0)
            fT.write(json.dumps(self.teams, default=jdefault))
            fT.flush()
            fT.close()
        except Exception as e:
            print(e)

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
                self.json_sync()
                return True
        return False

    # TODO
    # def ban_team(self, name, __time):
    #     for t in self.team:
    #         if t.name == name:
    #             bot.sendMessage(t.owner_id, 'Banned for {0} seconds'.format(__time))

    def restart_game(self):
        self.time_start = 0
        self.isGoing = False
        self.riddles = json_load('Riddles.json')
        for t in self.teams:

           # t.timer = time.gmtime()
            t.solved = 0
            t.cur_position = t.start_position
            t.is_word = False
            t.has_ended = False
            bot.sendMessage(t.owner_id, 'Игра была перезапущена. Ждите старта!')
        self.json_sync()

    def print_status(self, user_id):
        message = {t.name : [t.solved, t.cur_position, t.solved_bonus, t.now() - t.time_start] for t in self.teams}
        bot.sendMessage(user_id, message)

    def send_message(self, to_name, text):
        for t in self.teams:
            if t.name.upper() == to_name.upper():
                bot.sendMessage(t.owner_id, text)
                return True
        return False

    def handle_message(self, msg):
        try:
            user = msg['from']
            text = msg['text'].split()
            pprint(msg)
            team = self.find_team(user['id'])
            if text == '/start':
                pass
            elif 'entities' in msg:
                pprint(msg['entities'][0]['type'])
                if text[0] == '/register':
                    self.__register(user['id'], text)
                elif text[0] == '/help':
                    self.call_help(self.find_team(user['id']))
                elif user['id'] == ADMIN_ID:
                    if text[0] == '/del':
                        self.del_team(text[1])
                    elif text[0] == '/status':
                        self.print_status(user['id'])
                    elif text[0] == '/send':
                        self.send_message(text[1], ' '.join(text[2:]))
                    elif text[0] == '/start_quest':
                        self.start_quest()
                    elif text[0] == '/stop_quest':
                        self.stop_quest()
                    elif text[0] == '/restart':
                        self.restart_game()
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
            print(e)

def dictToTeam(d):
    team = Team(d['name'], d['owner_id'])
    team.solved = d['solved']
    team.is_word = d['is_word']
    team.has_ended = d['has_ended']
    team.time_start = d['time_start']
    team.time_stop = d['time_stop']
    team.start_position = d['start_position']
    team.cur_position = d['cur_position']
    return team

def jdefault(o):
    return o.__dict__

def json_load(fName):
    with open(fName, "r+") as f:
       data = f.read().replace('\n', '')
       data = json.loads(data)
    return data

#====================MAIN=============================#


if __name__ == '__main__':
    riddles = json_load('Riddles.json')
    lTeams = json_load('RegisteredTeams.json')
    teams = [dictToTeam(t) for t in lTeams]
    quest = Game('Hogwarts quest', riddles=riddles, teams = teams)
    bot = telepot.Bot(BOT_TOKEN)
    bot.message_loop(quest.handle_message)

    print('Listening...')
    while 1:
        time.sleep(1)
