# -*- coding: utf-8 -*-
import telepot, time, json
from pprint import pprint

class Msg():
	bad = ": код не принят!"
	good = ": код принят! Ждите следующую загадку."
	bonus = 'Бонусный код принят!'
	start = "Внимание, команды! Квест начался! Время пошло!"
	stop = "Внимание, команды, квест завершен!"
	restart = 'Внимание, команды, игра была перезапущена! Ожидайте старта!'
	last = 'Последняя локация - актовый зал. Вас ждет последнее испытание...'
	congrat = 'Поздравляем, вы прошли квест! Ожидайте окончания квеста...'



class Team(object):
    def __init__(self, d):
        self.name = ""
        self.owner_id = 0
        self.time_start = 0
        self.time_stop = 0
        self.penalty = 0
        self.loc_cur = 0
        self.loc_start = 0
        self.cnt_solved = 0
        self.cnt_bonus = 0
        self.has_ended = False
        if d is not []:
            self.fromDict(d)

    def fromDict(self, d):
        for k, v in d.items():
            setattr(self, k, v)


class Game(object):
    def __init__(self, data, teams = []):
        self.raw = data
        self.ADMIN_ID = data['ADMIN_ID']
        self.isGoing = False
        self.teams_file = data['teams']
        self.teams = teams
        self.time_start = 0
        self.riddles = data['riddles']
        pprint([t.name for t in self.teams])
        # print(self.riddles['0']['sp_riddle'] == 'текст0')
        # pprint(self.riddles)
        # pprint(self.riddles['1'])
        self.black_list = []

    def start_quest(self, isSilent):
        if not self.isGoing:
            self.isGoing = True
            self.time_start = now()
            for t in self.teams:
                t.time_start = now()
                if not isSilent:
                    bot.sendMessage(t.owner_id, Msg.start)

    def stop_quest(self):
        try:
            self.isGoing = False
            self.time_start = now() - self.time_start
            for t in self.teams:
                t.time_stop = now()
                t.has_ended = True
                bot.sendMessage(t.owner_id, Msg.stop)
        except Exception as e:
            print(e)

    def call_help(self, team):
        team.penalty+=1
        bot.sendMessage(self.ADMIN_ID, 'help {0}, location {1}'.format(team.name, team.loc_cur + 1))

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
        try:
            if not team.has_ended:
                if not team.is_word:
                    if lRid[str(team.loc_cur)]['code'].upper() == code.upper():
                        response += Msg.good
                        bot.sendMessage(user_id, response)
                        team.solved += 1
                        cur_rid = lRid[str(team.loc_cur)]['riddle']
                        team.loc_cur = (team.loc_cur + 1) % len(lRid)
                        if team.solved == len(lRid):
                            team.is_word = True
                            bot.sendMessage(user_id, Msg.last)
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
                        bot.sendMessage(user_id, Msg.congrat)
                        bot.sendMessage(self.ADMIN_ID, 'Team {0} has finished!'.format(team.name))
                self.rewrite_json(self.teams_file)
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

    def register_team(self, owner_id, name):
        new_team = Team({"owner_id":owner_id, "name":name})
        self.teams.append(new_team)
        self.rewrite_json(self.teams_file)

    def rewrite_json(self, name):
        try:
            fT = open(name, 'r+')
            fT.truncate(0)
            fT.write(json.dumps(self.teams, default=jdefault, ensure_ascii=False))
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
                self.rewrite_json(self.teams_file)
                return True
        return False

    def restart_game(self):
        self.time_start = now()
        self.isGoing = False
        self.riddles = self.raw['riddles']
        for t in self.teams:
            t.cnt_solved = 0
            t.cnt_bonus = 0
            t.loc_cur = t.loc_start
            t.has_ended = False
            t.penalty = 0
            t.time_start = now()
            t.time_stop = now()
            bot.sendMessage(t.owner_id, Msg.restart)
        self.rewrite_json(self.teams_file)

    def print_status(self):
        message = {t.name : [t.cnt_solved, t.loc_cur, t.cnt_bonus, now() - t.time_start, t.penalty
        ] for t in self.teams}
        bot.sendMessage(self.ADMIN_ID, message)

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
                elif user['id'] == self.ADMIN_ID:
                    if text[0] == '/del':
                        self.del_team(text[1])
                    elif text[0] == '/status':
                        self.print_status()
                    elif text[0] == '/send':
                        self.send_message(text[1], ' '.join(text[2:]))
                    elif text[0] == '/start_quest':
                        if len(text) > 1 and text[1] == 'y':
                            self.start_quest(True)
                        else:
                            self.start_quest(False)
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


def jdefault(o):
    return o.__dict__


def json_load(fName):
    with open(fName, "rb+") as f:
        data = f.read()
        data = json.loads(data.decode('utf8'))
    return data


def now():
    return int(time.time())

#====================MAIN=============================#


if __name__ == '__main__':
    gamedata = json_load('gamestate.json',)
    lTeams = json_load(gamedata['teams'])
    teams = [Team(t) for t in lTeams]
    pprint(teams)
    quest = Game(gamedata, teams)
    bot = telepot.Bot(gamedata['BOT_TOKEN'])
    bot.message_loop(quest.handle_message)

    print('Listening...')
    while 1:
        time.sleep(1)
