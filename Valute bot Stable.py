import requests
import datetime
import os
import sys
import json
from time import sleep

VERSION = '1.6.5 Stable'

BOT_TOKEN = '' # Указываете токен для бота
BIO = '' # Указываете никнейм администратора

URL_BOT = 'https://api.telegram.org/bot%s/' %BOT_TOKEN
URL_MONEY = 'https://www.cbr-xml-daily.ru/'

# Cообщение помощи
HELP_MESSAGE = """Чтобы узнать цену валюты отправьте мне ее имя или код. 
Я работаю так же, как и конвертер. Например, напишите мне 100 евро.

Все данные я беру с сайта %s Курсы ЦБ РФ в XML и JSON, API

Если вы нашли ошибку или опечатку напишите мне: @%s""" %(URL_MONEY, BIO.replace('_', '\_'))

# Стартовове сообщение
START_MESSAGE = """Здравствуйте, %s!
Перед началом работы обязательно посмотрите справку. Так, на всякий случай.""" 

# Стартовове сообщение
ADMIN_COMMANDS = """    ***Рассылка*** - рассылка всем пользователям (которые есть в файле рассылок)
    ***Статистика*** - сегодняшняя статистика использования бота"""

def button(text, callback_data = None):
    return {'text': text, 'callback_data': callback_data}

MAIN_KEYBOARD = [
    [button('Список валют')],
    [button('Помощь')]
]

COMMAND_KEYBOARD = [
    [button('Вернуться в меню')]
]

ADMIN_KEYBOARD = [
    [button('Рассылка'), button('Статистика')],
    [button('Список валют')],
    [button('Помощь')]
]

def pause(message = 'Нажмите любую клавишу для продолжения...'):
    print(message)
    input()


class Money:
    update = 0
    MONEY_URL = ''
    name_list = []
    code_list = []

    def __init__(self, url):
        self.MONEY_URL = url
        self.update = self.get_updates_json()
        self.name_list = self.get_name_list()
        self.code_list = self.get_code_list()

    def get_updates_json(self):
        try:
            response = requests.get(self.MONEY_URL + 'daily_json.js')
            return response.json()
        except requests.exceptions.ConnectionError:
            print_and_log('[%s] Ошибка подключения к %s'%(get_time_date(), self.MONEY_URL))
            pause()
            sys.exit()

    def get_valute(self, valute_char_code):
        valute = self.update['Valute'][valute_char_code]
        return valute

    def get_name_list(self):
        valutes = self.update['Valute']
        self.name_list = []
        for key in valutes:
            self.name_list.append(self.update['Valute'][key]['Name'])
        v = self.name_list[3][15]
        o = self.name_list[3][14]
        i = self.name_list[3][7]
        h = self.name_list[3][8]
        e = self.name_list[1][2]
        ii = self.name_list[1][6]
        for key in range(len(self.name_list)):
            if (key != 2):
                if (key == 27):  
                   self.name_list[key] = 'Украинская гривна' 
                if (key != 25):
                    self.name_list[key] = self.name_list[key].replace(o+v, '')
                self.name_list[key] = self.name_list[key].replace(i+h, 'ий')
                if (self.name_list[key] != self.name_list[key].replace(e+v, 'ей')): 
                    self.name_list[key] = self.name_list[key].replace(e+v, 'ей')
                elif (key != 20 and key != 30):
                    self.name_list[key] = self.name_list[key].replace(e+ii, 'ь')
        return self.name_list

    def get_code_list(self):
        valutes = self.update['Valute']
        self.code_list.clear()
        for key in valutes:
            self.code_list.append(self.update['Valute'][key]['CharCode'])
        return self.code_list

    def find_code(self, name):
        buf_search = name.lower()

        usd = 'доллар сша'
        for symb in range(len(buf_search) - 2):
            if (usd.find(buf_search[0:len(buf_search)-symb]) != -1):
                return 'USD'
            
        for key in range(len(self.name_list)):
            buf_name = self.name_list[key].lower()
            buf_code = self.code_list[key].lower()
            if (buf_search == buf_name or 
                buf_search == buf_code):
                return self.code_list[key]

        for symb in range(len(buf_search) - 2):
            for key in range(len(self.name_list)):
                buf_name = self.name_list[key].lower()
                buf_code = self.code_list[key].lower()
                if (buf_name.find(buf_search[0:len(buf_search)-symb]) != -1 or 
                    buf_code.find(buf_search[0:len(buf_search)-symb]) != -1):
                    return self.code_list[key]

        return '-1' 

class User:
    update = 0
    message = ''
    nick = ''
    username = ''
    chat_id = 0
    data = ''
    
    def __init__(self, UPDATE):
        self.update = UPDATE
        self.data = self.get_callback_data()
        if (self.data != -1):
            self.nick = self.get_callback_nick()        
            self.username = self.get_callback_username() 
            self.chat_id = self.get_callback_chat_id()
        else:              
            self.message = self.get_message()        
            self.nick = self.get_nick()        
            self.username = self.get_username() 
            self.chat_id = self.get_chat_id()

    def get_callback_data(self):
        try:
            data = self.update['callback_query']['data']
            return data
        except KeyError:
            return -1

    def get_callback_chat_id(self):
        try:
            data = self.update['callback_query']['from']['id']
            return data
        except KeyError:
            return -1

    def get_callback_nick(self):
        try:
            data = self.update['callback_query']['from']['first_name']
            return data
        except KeyError:
            return -1

    def get_callback_username(self):
        try:
            data = self.update['callback_query']['from']['username']
            return data
        except KeyError:
            return -1


    def get_chat_id(self):
        try:
            self.chat_id = self.update['message']['chat']['id']
            return self.chat_id
        except KeyError:
            return -1

    def get_username(self):
        try:
            self.username = self.update['message']['from']['username']
            return self.username
        except KeyError:
            return -1

    def get_nick(self):
        try:
            self.nick = self.update['message']['from']['first_name']
            return self.nick
        except KeyError:
            return 'KEY_ERROR'

    def get_message(self):
        try:
            self.message = self.update['message']['text']
            return self.message
        except KeyError:
            return 'KEY_ERROR'
        except UnicodeEncodeError:
            return 'UNICODE_ERROR'
       
class Bot:
    token = ''
    url = ''
    json = 0

    def __init__(self, token, url = 'https://api.telegram.org/bot'):
        self.token = token
        self.url = url+self.token+'/'
        self.json = self.get_json()

    def get_json(self, offset = 0):
        try:
            param = {'offset': offset}
            response = requests.get(self.url + 'getUpdates', data = param)
            return response.json()
        except requests.exceptions.ConnectionError:
            print_and_log('[%s] Ошибка подключения к %s'%(get_time_date(), self.url))
            pause()
            sys.exit()

    def get_last_update(self, offset = 0):
        json = self.get_json(offset)
        try:
            result = json['result']
            total_updates = len(result) - 1
            return result[total_updates]
        except IndexError:
            return -1
        except KeyError:
            return -1

    def get_first_update(self, offset = 0):
        json = self.get_json(offset)
        try:
            result = json['result']
            return result[0]
        except IndexError:
            return -1
        except KeyError:
            return -1

    def send_message(self, chat, text):
        params = {'chat_id': chat, 'text': text}
        response = requests.post(URL_BOT + 'sendMessage', data = params)
        print_and_log('[%s] Бот: Ответ отправлен'%get_time_date())
        return response

    def distribution_to_all(self, user_list_chat_id, text):
        print_and_log('[%s]Рассылка начата'%(get_time_date()))
        for key in user_list_chat_id:
            self.send_message(key, text)
            print_and_log('[%s]Рассылка: сообщение отправлено. Идентификатор чата: %d, Текст: %s'%(get_time_date(), key, text))
        print_and_log('[%s]Рассылка завершена'%(get_time_date()))

    def show_keyboard(self, chat_id, text, keyboard):
	    params = {
	        'parse_mode': 'Markdown',
                'disable_web_page_preview': False,
	        'chat_id': chat_id, 
	        'text': text,
                'reply_markup': json.dumps({
                    'keyboard': keyboard
                })     
	    }
	    response = requests.post(URL_BOT + 'sendMessage', data = params)
	    print_and_log('[%s] Бот: Ответ отправлен'%get_time_date())
	    return response


def valute_keyboard(text_list, callback_list, menu_button = False):
    keyboard = []
    if (menu_button):
        keyboard.append([button('Вернуться в меню')]) 
    keyboard.append([button('Доллар США')])
    keyboard.append([button('Евро')])
    for key in range(len(text_list)):
        if (text_list[key] != 'Доллар США' and text_list[key] != 'Евро'):
            keyboard.append([button(text_list[key])])
    return keyboard


def get_time_date():
     now = datetime.datetime.now()
     time = '%02d.%02d.%04d %02d:%02d:%02d' %(now.day, now.month, now.year, now.hour, now.minute, now.second)
     return time

def get_date():
    now = datetime.datetime.now()
    time = '%02d.%02d.%04d' %(now.day, now.month, now.year)
    return time


def print_and_log(line, name = 'messages'):
    print(line)
    file_log = open("logs\\%s-%s.log"%(name, get_date()), 'a')
    try:
        file_log.write(line + '\n')
    except UnicodeEncodeError:
        line_bytes = line.encode()
        line_bytes = line_bytes.decode('ascii', errors = 'backslashreplace')
        line = ''
        for key in line_bytes:
            line += key
        file_log.write(line + '\n')
    file_log.close()

def user_log(user_list):
    name = 'users'
    file_log = open("logs\\%s-%s.log"%(name, get_date()), 'w')
    file_log.write('Users at %s:'%get_date())
    for key in user_list:
        file_log.write('\n  ' + key)
    file_log.close()
    print_and_log('[%s] Файл (logs\\%s-%s.log) с пользователями успешно записан' %(get_time_date(), name, get_date()))

def write_distribution_log(user_id_list, name = 'for-distribution'):
    file_log = open('%s.dat'%(name), 'w')
    file_log.truncate()
    for key in user_id_list:
        file_log.write(str(key))
        if (key != user_id_list[len(user_id_list) - 1]):
            file_log.write('\n')
    file_log.close()
    print_and_log('[%s] Файл (%s.dat) с идентификаторами чатов успешно записан' %(get_time_date(), name))

def read_distribution_log(name = 'for-distribution'):
    try:
        file_log = open('%s.dat'%(name), 'r')
    except FileNotFoundError:
        file_log = open('%s.dat'%(name), 'w')
        file_log.close()
        file_log = open('%s.dat'%(name), 'r')
    user_id_list = []
    user_id_list_str = file_log.read()
    user_id_list_str = user_id_list_str.split()
    for key in user_id_list_str:
        user_id_list.append(int(key))
    file_log.close()
    return user_id_list


def create_dir(dirrectory):
    try:
        os.mkdir(dirrectory)
    except FileExistsError:
        return -1

###  ГЛАВНАЯ ФУНКЦИЯ ВЫЗОВА БОТА ###
def main():
    global MAIN_KEYBOARD
    global ADMIN_KEYBOARD
    global COMMAND_KEYBOARD

    create_dir('logs')

    print ('Бот курса валют. Версия %s \n(с) Черная кепка (The Black Cap), 2018. Все права защищены'%VERSION)

    print_and_log('\n\n[%s] Ожидаение подключения к сети...'%get_time_date())
    money = Money(URL_MONEY)
    bot = Bot(BOT_TOKEN)
    print_and_log('[%s] Подключено'%get_time_date())

    time = datetime.datetime.now()
    lst_update_id = 0

    print_and_log('[%s] Бот запущен'%get_time_date())
    lst_update = bot.get_last_update()
    while (lst_update == -1):
        lst_update = bot.get_last_update()

    lst_update_id = lst_update['update_id']       
    last_day = time.day

    count = 0
    user_chat_id_list = []
    active_users = []
    waiting_for_message = False

    
    while True:
        time = datetime.datetime.now()
        if (time.hour % 2 == 0 and time.hour != 0):
            money = Money(URL_MONEY)
    
        if (last_day < time.day):
            last_day = time.day
            active_users = []
        
        #Проверяем - есть ли запросы у сервера
        if (bot.get_last_update()['update_id'] > lst_update_id):
            
            current_update = bot.get_first_update(lst_update_id + 1)
            user = User(current_update)
            user_chat_id_list = read_distribution_log()

            summ = 0
            valute_str = ''
            message = 0

            #Счётчик обработанных сообщений
            if (user.username != BIO):
            #if (True):
                count += 1
                was_today = False
                user_in_list = False
                for key in active_users:
                    if (('%s (%s) - %d'%(user.username, user.nick, user.chat_id)) == key):
                        was_today = True
                if (not was_today):
                    print_and_log('[%s] Сообщение от нового пользователя (сегодня): %s (%s) - %d'%(get_time_date(), user.username, user.nick, user.chat_id))
                    active_users.append('%s (%s) - %d'%(user.username, user.nick, user.chat_id))
                    user_log(active_users)
                #Дополнение пользователя в рассылку
                for key in user_chat_id_list:
                    if (user.chat_id == key):
                        user_in_list = True
                if (not user_in_list):
                    print_and_log('[%s] Сообщение от нового пользователя (за все время): %s (%s) - %d'%(get_time_date(), user.username, user.nick, user.chat_id))
                    user_chat_id_list.append(user.chat_id)
                    write_distribution_log(user_chat_id_list)
            else:
                MAIN_KEYBOARD = ADMIN_KEYBOARD

            #Вывод запроса пользователя
            try: 
                print_and_log('[%s] %s (%s): %s'%(get_time_date(), user.username, user.nick, user.message))
            except UnicodeEncodeError:
                user.message = 'UNICODE_ERROR'
                print_and_log('[%s] %s (%s): %s'%(get_time_date(), user.username, user.nick, user.message))

            #Обработка для админа
            if (user.username == BIO and waiting_for_message):
                if (user.message != '0' and user.message != 'Отмена' and user.message != 'UNICODE_ERROR'):
                    bot.distribution_to_all(user_chat_id_list, user.message)
                    message = 'Я завершил рассылку. \n\nСообщений отправил: %d сооб.'%len(user_chat_id_list)
                elif(user.message == 'UNICODE_ERROR'):
                    message = 'Я отменил рассылку. :( \nЯ не понял ваш текст (ошибка Юникода).'
                else:
                    message = 'Я отменил рассылку.'
                bot.send_message(user.chat_id, message)                
                waiting_for_message = False
                bot.show_keyboard(user.chat_id, '**Главное меню**', MAIN_KEYBOARD)
            elif (user.username == BIO and user.message.lower() == 'статистика'):
                message = 'Пожалуйста, статистика на %s.\n'%get_time_date()
                message += '\nЗапросов обработано: \n  %s зап.\n' %count
                message += '\nПользователи, написавшие мне сегодня: '
                for key in active_users:
                    message += '\n  ' + key
                if not active_users:
                    message += '\n  Пользователи мне еще не писали'
                bot.send_message(user.chat_id, message)
            elif (user.username == BIO and user.message.lower() == 'рассылка'):
                message = 'Отправьте мне сообщение, а я разошлю его пользователям.\nЕсли вы хотите отменить рассылку, то отправьте мне ноль'
                bot.show_keyboard(user.chat_id, message, [[button('Отмена')]])
                waiting_for_message = True

            #Обработка запроса пользователя
            elif (user.message.lower() == '/start'):
                message = START_MESSAGE %user.nick.replace('_', '\_')
                bot.show_keyboard(user.chat_id, 'Сечас вы в главном меню, ***%s***'%user.nick, MAIN_KEYBOARD)
            elif (user.message.lower() == 'вернуться в меню'):
                bot.show_keyboard(user.chat_id, 'Сечас вы в главном меню, ***%s***'%user.nick, MAIN_KEYBOARD)
            elif (user.message.lower() == 'помощь' or user.message.lower() == '/help'):
                message = HELP_MESSAGE
                if (user.username == BIO):
                    message += '\n\nОу! Я вижу, что вы администратор. У вас есть доступ к дополнительным командам: \n' + ADMIN_COMMANDS
                    bot.show_keyboard(user.chat_id, message, COMMAND_KEYBOARD)
                else:
                    bot.show_keyboard(user.chat_id, message, MAIN_KEYBOARD)                   
            elif (user.message.lower() == 'список валют'):
                bot.show_keyboard(user.chat_id, 'Посмотрите валюты, которые я знаю ' + u'\U0001F60C', valute_keyboard(money.name_list, None, True))
            elif (user.message == 'UNICODE_ERROR' or user.message == 'KEY_ERROR'):
                message = 'Мне кажется или это не валюта? Напшите /help или нажмите \"Меню\" -> \"Помощь\" для справки.'
                bot.send_message(user.chat_id, message) 
            else:
                #Разбиение запроса на сумму и валюту
                try:
                    user.message = user.message.replace('/', '')
                    user_message_words = user.message.split(" ", 2)
        
                    if (len(user_message_words) >= 2):
                        if (user_message_words[1].isalpha()):
                            summ = float(user_message_words[0])
                            valute_str = user_message_words[1]
                            for key in range(2, len(user_message_words)):
                                valute_str += ' ' + user_message_words[key]
                            valute_str = money.find_code(valute_str)
                    else: 
                        valute_str = money.find_code(user.message) 
                except UnicodeEncodeError:
                    summ = 0
                    valute_str = money.find_code(user.message) 
                except ValueError:
                    summ = 0
                    valute_str = money.find_code(user.message)
                
                #Формирование ответа пользователю
                try:
                    valute = money.get_valute(valute_str.upper())
                    
                    message = valute['Name'] + ' (%s)' %valute['CharCode']
                    if (summ != 0 and summ != 1):
                        message += '\nЦена: ' + str(summ) + ' ' + valute['CharCode'] + str(' = %.3f' %((valute['Value']/valute['Nominal'])*summ)) + ' RUB'
                    else:
                        message += '\nЦена: ' + str('%.3f' %(valute['Value']/valute['Nominal'])) + ' RUB'
                        if (valute['Previous'] >= valute['Value']):
                            message += ' (-%.3f)' %((valute['Previous'] - valute['Value'])/valute['Nominal'])
                        else:
                            message += ' (+%.3f)' %((valute['Value'] - valute['Previous'])/valute['Nominal'])
                    bot.send_message(user.chat_id, message)                        
                except KeyError:
                    message = 'Хм... Такой валюты я не знаю.'
                    message += '\nНажмите \"Меню\" -> \"Помощь\" для справки.'
                    bot.send_message(user.chat_id, message)

            #Отправка ответа пользователю       
            lst_update_id += 1 #Переход к следующему пользователю
        else:
            sleep(1)
    
if (__name__ == '__main__'):
    main()
