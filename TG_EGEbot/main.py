from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import data.db_session as db_session
from data.users import User
from flask import Flask
from test import Test
import threading
import logging


logging.basicConfig(filename="logs/bot_logs.txt", filemode="a", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
TOKEN = '5172000917:AAEBKo51H6COgUFJ76cbBq4yB2iUbc1f3pg'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class Bot:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dp = self.updater.dispatcher
        self.authorized = False
        self.just_finished = False
        self.user = User()
        self.sql_app()
        self.mark_translator_link = 'https://4ege.ru/novosti-ege/4023-shkala-perevoda-ballov-ege.html'
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("help", self.help))
        self.dp.add_handler(CommandHandler("stat_view", self.stat_view))
        self.dp.add_handler(CommandHandler('begin_exam', self.begin_exam))
        self.dp.add_handler(CommandHandler('next_problem', self.next_problem))
        self.dp.add_handler(CommandHandler('previous_problem', self.previous_problem))
        self.dp.add_handler(CommandHandler('finish_the_exam', self.finish_the_exam))
        self.dp.add_handler(CommandHandler('home', self.home))
        self.reg_handler = ConversationHandler(
            entry_points=[CommandHandler('registration', self.registration)],
            states={
                1: [MessageHandler(Filters.text & ~Filters.command, self.reg_get_nickname)]
            },
            fallbacks=[CommandHandler('stop', self.stop)]
        )
        self.auth_handler = ConversationHandler(
            entry_points=[CommandHandler('authorization', self.authorization)],
            states={
                1: [MessageHandler(Filters.text & ~Filters.command, self.auth_get_nickname)]
            },
            fallbacks=[CommandHandler('stop', self.stop)]
        )
        self.write_an_answer_handler = ConversationHandler(
            entry_points=[CommandHandler('write_an_answer', self.write_an_answer)],
            states={
                1: [MessageHandler(Filters.text & ~Filters.command, self.save_answer)]
            },
            fallbacks=[CommandHandler('stop', self.stop)]
        )
        self.start_keyboard = [['/registration', '/authorization'],
                    ['/help']]
        self.choice_keyboard = [['/stat_view', '/begin_exam'],
                    ['/help']]
        self.tasks_keyboard = [['/previous_problem', '/next_problem'],
                    ['/write_an_answer'], ['/finish_the_exam']]
        self.finish_keyboard = [['/home'], ['/stat_view', '/help']]
        self.dp.add_handler(self.reg_handler)
        self.dp.add_handler(self.auth_handler)
        self.dp.add_handler(self.write_an_answer_handler)
        self.db_sess = db_session.create_session()
        print('bot_init is done.')
        self.updater.start_polling()
        self.updater.idle()

    def start(self, update, context):
        self.test = Test('inf', update.message.chat.id) 
        markup = ReplyKeyboardMarkup(self.start_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(
            "Добрый день!", reply_markup=markup)

    def help(self, update, context):
        if self.authorized:
            if self.just_finished:
                markup = ReplyKeyboardMarkup(self.finish_keyboard, resize_keyboard=True)
            else:
                markup = ReplyKeyboardMarkup(self.choice_keyboard, resize_keyboard=True)
        else:
            markup = ReplyKeyboardMarkup(self.start_keyboard, resize_keyboard=True)
        with open('help.txt', 'r', encoding='utf-8') as help_data:
            help_text = ' '.join(help_data.readlines())
        update.message.reply_text(
            help_text,
            reply_markup=markup)

    def stop(self, update, context):
        update.message.reply_text(
            "Всего доброго!", 
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    def home(self, update, context):
        markup = ReplyKeyboardMarkup(self.choice_keyboard, resize_keyboard=True)
        update.message.reply_text(
            "Вы пришли к истокам.",
            reply_markup=markup
        )
        self.just_finished = False
    
    def finish_the_exam(self, update, context):
        markup = ReplyKeyboardMarkup(self.finish_keyboard, resize_keyboard=True)
        result = 'result'
        self.db_sess.commit()
        update.message.reply_text(
            f"Экзамен завершен. Результаты: {result}",
            reply_markup=markup
        )
        self.just_finished = True
        return ConversationHandler.END

    def registration(self, update, context):
        update.message.reply_text(
            "Пожалуйста, введите свой никнейм:", 
            reply_markup=ReplyKeyboardRemove()
        )
        return 1

    def reg_get_nickname(self, update, context):
        nickname = update.message.text
        user_id = update.message.chat.id
        self.existing_users = [elem.nickname for elem in self.db_sess.query(User).all()]
        if nickname in self.existing_users:
            markup = ReplyKeyboardMarkup(self.start_keyboard, one_time_keyboard=True, resize_keyboard=True)
            update.message.reply_text(
                "Пользователь с таким никнеймом уже существует.",
                reply_markup=markup
            )
        else:
            update.message.reply_text(
                f"Ваш никнейм: {nickname}", 
            )
            self.user.nickname = nickname
            self.user.chat_id = user_id
            self.db_sess.add(self.user)
            self.db_sess.commit()
            markup = ReplyKeyboardMarkup(self.start_keyboard, one_time_keyboard=True, resize_keyboard=True)
            update.message.reply_text(
                "Поздравляем, Вы зарегистрировались!",
                reply_markup=markup
            )
        return ConversationHandler.END

    def authorization(self, update, context):
        update.message.reply_text(
            "Пожалуйста, введите свой никнейм:", 
            reply_markup=ReplyKeyboardRemove()
        )
        return 1
    
    def auth_get_nickname(self, update, context):
        nickname = update.message.text
        existing_users = [elem.nickname for elem in self.db_sess.query(User).all()]
        if nickname not in existing_users:
            markup = ReplyKeyboardMarkup(self.start_keyboard, one_time_keyboard=True, resize_keyboard=True)
            update.message.reply_text(
                "Пользователь с таким никнеймом не существует.",
                reply_markup=markup
            )
            return ConversationHandler.END
        else:
            update.message.reply_text(
                "Вы успешно авторизовались."
            )
            self.authorized = True
            markup = ReplyKeyboardMarkup(self.choice_keyboard, one_time_keyboard=True, resize_keyboard=True)
            update.message.reply_text(
                "Выберите действие", 
                reply_markup=markup
            )
            return ConversationHandler.END
    
    def begin_exam(self, update, context):
        task = self.test.get_task()
        markup = ReplyKeyboardMarkup(self.tasks_keyboard, resize_keyboard=True)
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=f"Задание {self.test.actual_task + 1}\n {task}",
            reply_markup=markup
        )
    
    def next_problem(self, update, context):
        changer_response = self.test.next_task()
        if changer_response:
            task = self.test.get_task()
            markup = ReplyKeyboardMarkup(self.tasks_keyboard, resize_keyboard=True)
            context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Задание {self.test.actual_task + 1}\n {task}",
                reply_markup=markup
            )
    
    def previous_problem(self, update, context):
        changer_response = self.test.previous_task()
        if changer_response:
            task = self.test.get_task()
            markup = ReplyKeyboardMarkup(self.tasks_keyboard, resize_keyboard=True)
            context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Задание {self.test.actual_task + 1}\n {task}",
                reply_markup=markup
            )
    
    def write_an_answer(self, update, context):
        self.answer = update.message.text
        return 1
    
    def save_answer(self, update, context):
        self.answer = update.message.text
        update.message.reply_text(
            f"Ваш ответ <<{self.answer}>> сохранён."
        )
        return ConversationHandler.END

    def stat_view(self, update, context):
        if self.just_finished:
            markup = ReplyKeyboardMarkup(self.finish_keyboard, one_time_keyboard=True, resize_keyboard=True)
        else:
            markup = ReplyKeyboardMarkup(self.choice_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(
            "Здесь будет статистика решений",
            reply_markup=markup
        )
        self.just_finished = False
    
    def sql_app(self):
        db_session.global_init("db/blogs.db")
        self.sql_thread = threading.Thread(target=app.run)
        self.sql_thread.start()


if __name__ == '__main__':
    bot = Bot()
