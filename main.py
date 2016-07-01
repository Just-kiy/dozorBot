# -*- coding: utf-8 -*-
import telepot, time, json
from pprint import pprint


class Msg:
    bad = '{0}: код не принят!'
    good = '{0}: код принят! Ждите следующую загадку.'
    bonus = '{0}: онусный код принят!'
    spolier = '{0}: код спойлера принят, следующие координаты {1}'
    start = "Внимание, команды! Квест начался! Время пошло!"
    stop = "Внимание, команды, квест завершен!"
    restart = 'Внимание, команды, игра была перезапущена! Ожидайте старта!'
    last = 'Последняя локация - актовый зал. Вас ждет последнее испытание...'
    congrat = 'Поздравляем, вы прошли квест! Ожидайте окончания квеста...'
    has_ended = 'Вы уже прошли квест'
    welcome = ''


class Team(object):
    def __init__(self, d):
        self.name = ""
        self.owner_id = 0
        self.time_start = 0
        self.time_stop = 0
        self.penalty = []
        self.loc_cur = 0
        self.loc_start = 0
        self.cnt_solved = 0
        self.cnt_bonus = 0
        self.has_ended = False
        if d is not []:
            self.from_dict(d)

    def from_dict(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def solved(self, code, is_bonus=False, is_spoiler=False, coord=''):
        if is_bonus:
            self.cnt_bonus += 1
            bot.sendMessage(self.owner_id, Msg.bonus.format(code))
            return
        elif is_spoiler:
            bot.sendMessage(self.owner_id, Msg.spolier.format(code, coord))
        else:
            self.cnt_solved += 1
            if self.cnt_solved == len(quest.riddles):
                self.has_ended = True
                self.time_stop = now()
                bot.sendMessage(self.owner_id, Msg.congrat)
            else:
                bot.sendMessage(self.owner_id, Msg.good.format(code))
                self.loc_cur = (self.loc_cur + 1) % len(quest.riddles)
                self.send_riddle(quest.riddles[str(self.loc_cur)])
        return

    def send_riddle(self, r):
        bot.sendMessage(self.owner_id, r['sp_riddle'])
        return


class Game(object):
    def __init__(self, data, t=[]):
        self.raw = data
        self.ADMIN_ID = data['ADMIN_ID']
        self.isGoing = False
        self.log_file = data['log']
        self.teams_file = data['teams']
        self.teams = t
        self.time_start = 0
        self.riddles = data['riddles']
        self.black_list = []

    def start_quest(self, is_silent):
        if not self.isGoing:
            self.isGoing = True
            self.time_start = now()
            for t in self.teams:
                t.penalty = [0 for r in range(len(self.riddles) - 1)]
                t.time_start = now()
                if not is_silent:
                    bot.sendMessage(t.owner_id, Msg.start)
                    t.send_riddle(self.riddles[str(t.loc_cur)])

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
        team.penalty[team.loc_cur] += 1
        bot.sendMessage(self.ADMIN_ID, 'help {0}, location {1}'.format(team.name, team.loc_cur + 1))

    def find_team(self, user_id):
        for t in self.teams:
            if user_id == t.owner_id:
                return t
        return False

    def check_code(self, team, code):
        code = code.upper()
        riddle = self.riddles[str(team.loc_cur)]
        try:
            if not team.has_ended:
                if code == riddle['sp_ans'].upper():
                    team.solved(code, is_spoiler=True, coord=riddle['loc_coord'])
                elif code == riddle['code'].upper():
                    team.solved(code)
                elif code in self.riddles['bonus']:
                    self.riddles['bonus'].remove(code)
                    team.solved(code, is_bonus=True)
                else:
                    bot.sendMessage(team.owner_id, Msg.bad.format(code))
            else:
                bot.sendMessage(team.owner_id, Msg.has_ended)
            rewrite_json(self.teams_file, self.teams)
        except Exception as e:
            print(e)
        return

    def __register(self, user_id, text):
        msg = ''
        if not (user_id in self.black_list):
            if len(text) >= 2:
                if not self.is_registered(user_id):
                    if not self.isGoing:
                        self.register_team(user_id, '_'.join(text[1:]))
                        msg = 'Вы успешно зарегестрированы!'
                    else:
                        msg = 'Квест уже идет!'
                else:
                    msg = 'Вы уже зарегестрированы на квест!'
            else:
                msg = 'Пожалуйста, введите /register и название команды'
        bot.sendMessage(user_id, msg)

    def register_team(self, owner_id, name):
        new_team = Team({"owner_id": owner_id, "name": name})
        self.teams.append(new_team)
        rewrite_json(self.teams_file, self.teams)

    def is_registered(self, user_id):
        for t in self.teams:
            if t.owner_id == user_id:
                return True
        return False

    def ban_team(self, name):
        for t in self.teams:
            if t.name == name:
                bot.sendMessage(t.owner_id, 'Ваша команда была исключена! Обратитесь к организаторам!')
                self.black_list.append(t.owner_id)
                self.teams.remove(t)
                rewrite_json(self.teams_file, self.teams)
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
            t.penalty = [0 for r in range(len(self.riddles) - 1)]
            t.time_start = now()
            t.time_stop = now()
            bot.sendMessage(t.owner_id, Msg.restart)
        rewrite_json(self.teams_file, self.teams)

    def print_status(self):
        message = []
        for t in self.teams:
            message.append({
                'name': t.name,
                'solved': t.cnt_solved,
                'bonuses': t.cnt_bonus,
                'penalty': t.penalty,
                'location': t.loc_cur,
            })
        bot.sendMessage(self.ADMIN_ID, message)

    def send_message(self, to_name, text):
        for t in self.teams:
            if t.name.upper() == to_name.upper():
                bot.sendMessage(t.owner_id, text)
                return True
        return False

    def handle_message(self, msg):
        try:
            log(msg, self.log_file)
            user = msg['from']
            text = msg['text'].split()
            team = self.find_team(user['id'])
            if text == '/start':
                bot.sendMessage(user['id'], Msg.welcome)
            elif 'entities' in msg:
                pprint(msg['entities'][0]['type'])
                if text[0] == '/register':
                    self.__register(user['id'], text)
                elif text[0] == '/help':
                    self.call_help(self.find_team(user['id']))
                elif user['id'] == self.ADMIN_ID:
                    if text[0] == '/del':
                        self.ban_team(text[1])
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


def rewrite_json(file_name, data):
    try:
        ft = open(file_name, 'r+')
        ft.truncate(0)
        ft.write(json.dumps(data, default=jdefault, ensure_ascii=False, sort_keys=True,
                            indent=4, separators=(',', ': ')))
        ft.flush()
        ft.close()
    except Exception as e:
        print(e)


def jdefault(o):
    return o.__dict__


def json_load(file_name):
    with open(file_name, "rb+") as f:
        data = f.read()
        data = json.loads(data.decode('utf8'))
    return data


def log(msg, file_name):
    try:
        data = msg['from']
        data['text'] = msg['text']
        pprint(data)
        with open(file_name, 'a') as f:
            f.write(json.dumps(data, indent=4, separators=(',', ': ')) + '\n')
    except Exception as e:
        print(e)
    return


def now():
    return int(time.time())


# ====================MAIN=============================#


if __name__ == '__main__':
    gamedata = json_load('gamestate.json', )
    Msg.welcome = gamedata['brief']
    lTeams = json_load(gamedata['teams'])
    teams = [Team(t) for t in lTeams]
    pprint(teams)
    quest = Game(gamedata, teams)
    bot = telepot.Bot(gamedata['BOT_TOKEN'])
    bot.message_loop(quest.handle_message)

    print('Listening...')
    while 1:
        time.sleep(1)
