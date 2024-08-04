from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from dotenv import load_dotenv
from telegram import Update
from pathlib import Path
import re
import os
import psycopg2
import paramiko
import logging

# Настройка логирования
logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', encoding="utf-8")
logger = logging.getLogger(__name__)

logger.debug('Отладочная информация.')
logger.info('Работает модуль logging.')
logger.warning('Риск получения сообщения об ошибке.')
logger.error('Произошла ошибка.')
logger.critical('Программа не может выполняться.')

# Функция для удаленного доступа к машине с которой будет собираться информация о работе:
def remote_command(ssh_client, hostname, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info(f"Connecting to {hostname}:{port} as {username}")
        client.connect(hostname=hostname, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        result = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            logger.error(f"Error executing command on {hostname}: {error}")
            return error
        return result
    except Exception as e:
        logger.error(f"Error connecting to {hostname}: {e}")
        return str(e)
    finally:
        client.close()

# Пример использования функции для нескольких хостов
hosts = [
    {'HOST': os.getenv('HOST1'), 'PORT': os.getenv('PORT1'), 'USER': os.getenv('USER1'), 'PASSWORD': os.getenv('PASSWORD1')},
    {'HOST': os.getenv('HOST2'), 'PORT': os.getenv('PORT2'), 'USER': os.getenv('USER2'), 'PASSWORD': os.getenv('PASSWORD2')}
]

# Функция для поиска телефонных номеров в тексте
def find_phone_numbers(text):
    phone_pattern = re.compile(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
    return phone_pattern.findall(text)

# Функция для обработки команды /find_phone_numbers
def find_phone_numbers_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Отправьте текст, в котором вы хотите найти телефонные номера.")

# Функция для поиска адресов электронной почты в тексте
def find_emails(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return email_pattern.findall(text)

# Функция для обработки команды /find_emails
def find_emails_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Отправьте текст, в котором вы хотите найти адреса электронных почт.")

# Функция для проверки сложности пароля
def verify_password(password):
    if len(password) < 8:
        return "Слабый пароль: пароль должен содержать не менее 8 символов"
    if not re.search(r'\d', password):
        return "Слабый пароль: пароль должен содержать хотя бы одну цифру"
    if not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password):
        return "Слабый пароль: пароль должен содержать буквы в разных регистрах"
    if not re.search(r'[@_!#$%^&*()<>?/\|}{~:]', password):
        return "Слабый пароль: пароль должен содержать хотя бы один специальный символ"
    return "Надежный пароль"

# Функция для обработки команды /verify_password
def verify_password_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Отправьте пароль, который вы хотите проверить на надежность.")

# Функция для получения информации о релизе
def get_release(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'cat /etc/os-release')
    update.message.reply_text(result)

# Функция для получения информации о системе
def get_uname(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'uname -a')
    update.message.reply_text(result)

# Функция для получения времени работы системы
def get_uptime(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'uptime')
    update.message.reply_text(result)

# Функция для получения информации о состоянии файловой системы
def get_df(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'df -h')
    update.message.reply_text(result)

# Функция для получения информации о состоянии оперативной памяти
def get_free(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'free -m')
    update.message.reply_text(result)

# Функция для получения информации о производительности системы
def get_mpstat(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'mpstat')
    update.message.reply_text(result)

# Функция для получения информации о работающих пользователях
def get_w(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'w')
    update.message.reply_text(result)

# Функция для получения последних входов в систему
def get_auths(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'last -n 10')
    update.message.reply_text(result)

# Функция для получения последних критических событий
def get_critical(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'journalctl -p crit -n 5')
    update.message.reply_text(result)

# Функция для получения запущенных процессах
def get_ps(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'ps')
    update.message.reply_text(result)

# Функция для получения информации о используемых портах
def get_ss(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'ss -tulwnH')
    update.message.reply_text(result)

# Функция для получения информации о используемых сервисах
def get_services(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'ps -e -o comm=')
    services = result.split('\n')[:30]
    formatted_services = "\n".join([f"• {service}" for service in services if service])
    update.message.reply_text(f"Список сервисов:\n{formatted_services}")

# Функция для получения информации о установленном пакете
def get_apt_list(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'dpkg-query -f \'${binary:Package}\n\' -W')
    if result:
        packages = result.split('\n')[:50]
        update.message.reply_text('\n'.join(packages))
        update.message.reply_text("Нажмите на кнопку /search_in_apt_list и отправьте название пакета (через пробел), который вы хотите найти в списке. Важно указать правильное название, например: blt/kali-rolling,now 2.5.3+dfsg-7 amd64 [installed,automatic].")

# Функция для обработки команды /search_in_apt_list
def search_in_apt_list(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    search_text = user_message.split(maxsplit=1)[1] if ' ' in user_message else None

    if not search_text:
        update.message.reply_text('Пожалуйста, укажите название пакета для поиска через ПРОБЕЛ после команды /search_in_apt_list')
        return

    apt_list_result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'dpkg-query -f \'${binary:Package}\n\' -W')
    if apt_list_result:
        if search_text in apt_list_result:
            update.message.reply_text(f'Пакет "{search_text}" установлен на удаленной машине.')
        else:
            update.message.reply_text(f'Пакет "{search_text}" не найден в списке установленных пакетов.')
    else:
        update.message.reply_text('Не удалось получить список установленных пакетов.')

# Команда для выполнения на удаленной машине
def execute_command(update: Update, context: CallbackContext) -> None:
    password = os.getenv('PGPASSWORD')  # Получение пароля из переменных окружения
    if not password:
        update.message.reply_text('Пароль не был предоставлен. Пожалуйста, попробуйте снова.')
        return

    command = f'bash backup.sh {password}'
    hostname = os.getenv('HOST2')
    port = int(os.getenv('PORT2'))
    username = os.getenv('USER2')
    ssh_password = os.getenv('PASSWORD2')
    
    result = remote_command(paramiko.SSHClient(), hostname, port, username, ssh_password, command)
    update.message.reply_text(f"Command result:\n{result}")

#Функция для получения логов репликации базы данных с удаленной машины: 
def get_repl_logs(update: Update, context: CallbackContext) -> None:
    result = remote_command(paramiko.SSHClient(), os.getenv('HOST1'), os.getenv('PORT1'), os.getenv('USER1'), os.getenv('PASSWORD1'), 'tail -n 20 /var/log/postgresql/postgresql-13-main.log')
    update.message.reply_text(result)

# Функция для подключения к базе данных и поиску информации (телефонов или адресов почт):
def get_from_db(dbname=None, user=None, password=None, host=None, port=None):
    dbname = dbname or os.getenv('DB_NAME')
    user = user or os.getenv('DB_USER')
    password = password or os.getenv('DB_PASSWORD')
    host = host or os.getenv('DB_HOST')
    port = port or os.getenv('DB_PORT')

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()
    cursor.execute("SELECT * FROM phone_numbers")
    phone_numbers = cursor.fetchall()
    conn.close()
    return emails, phone_numbers

# Обработчик команды /get_emails
def get_emails(update: Update, context: CallbackContext):
    emails, _ = get_from_db()
    if emails:
        response = "Список электронных писем:\n"
        for email in emails:
            response += f"{email[0]} {email[1]}\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text("Записей не найдено.")

# Обработчик команды /get_phone_numbers
def get_phone_numbers(update: Update, context: CallbackContext):
    _, phone_numbers = get_from_db()
    if phone_numbers:
        response = "Список телефонных номеров:\n"
        for phone_number in phone_numbers:
            response += f"{phone_number[0]} {phone_number[1]}\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text("Записей не найдено.")

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    commands1 = "Доступные команды:\n/find_phone_numbers - для поиска телефонных номеров\n/find_emails - для поиска адресов электронных почт\n/verify_password - для проверки надежности пароля"
    commands2 = "Доступные команды для получения информации о удаленной машине:\n/get_release - получение информации о релизе\n/get_uname - получение информации о системе\n/get_uptime - получение времени работы системы\n/get_df - получение информации о состоянии файловой системы\n/get_free - получение информации о состоянии оперативной памяти\n/get_mpstat - получение информации о производительности системы\n/get_w - получение информации о работающих пользователях\n/get_auths - получение последних входов в систему\n/get_critical - получение последних критических событийы\n/get_ps - получение информации о запущенных процессах\n/get_ss - получение информации о используемых портах\n/get_apt_list - получение информации об установленных пакетах\n/search_in_apt_list - поиск пакета в списке установленных\n/get_services - получение информации о используемых сервисах\n/get_repl_db - создание репликации базы данных\n/get_repl_logs - получение логов о репликации базы данных\n/get_emails - получение информации о имеющихся записях в базе данных с адресами электронных почт\n/get_phone_numbers - получение логов о репликации базы данных"
    update.message.reply_text(commands1)
    update.message.reply_text(commands2)

#Функция в которой обрабатываются слова и предложения отправленные пользователем
def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    result = is_word_or_sentence(text)
    if result == "предложение":
        emails = find_emails(text)
        phone_numbers = find_phone_numbers(text)
# Функция которая обрабатывает сообщения в случае, если в тексте присутствуют адреса электронных почт
        if emails:
            update.message.reply_text("Найденные адреса электронной почты:\n" + "\n".join(emails))
            context.user_data['emails'] = emails
            update.message.reply_text("Хотите ли вы добавить эти адреса в базу данных? Ответьте 'да'.")
            # Ожидание ответа пользователя
            def wait_for_reply(update: Update, context: CallbackContext):
                reply = update.message.text.lower()
                if reply == "да":
                    insert_emails(update, context)
                else:
                    update.message.reply_text("Операция отменена.")

            # Сохраняем старые обработчики
            old_handlers = context.dispatcher.handlers[0].copy()
            # Удаляем все предыдущие обработчики, чтобы избежать дублирования
            context.dispatcher.handlers[0].clear()
            context.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, wait_for_reply))
            # Восстанавливаем старые обработчики после работы функции
            def restore_handlers(context: CallbackContext):
                context.dispatcher.handlers[0].clear()
                for handler in old_handlers:
                    context.dispatcher.add_handler(handler)

            # Планируем восстановление обработчиков после 5 секунд
            context.job_queue.run_once(lambda _: restore_handlers(context), 5)
            def insert_emails(update: Update, context: CallbackContext):
                emails = context.user_data.get('emails', [])
                if not emails:
                    update.message.reply_text("Не указаны адреса электронной почты.")
                    return

                conn = psycopg2.connect(
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT")
                )

                cursor = conn.cursor()
                check_query = "SELECT id FROM emails WHERE emals = %s;"
                insert_query = "INSERT INTO emails (emals) VALUES (%s) RETURNING id;"
                try:
                    for emals in emails:
                        cursor.execute(check_query, (emals,))
                        result = cursor.fetchone()
                        if result:
                            update.message.reply_text(f"Адреса {emals} уже существует с id: {result[0]}")
                        else:
                            cursor.execute(insert_query, (emals,))
                            emals_id = cursor.fetchone()[0]
                            conn.commit()
                            update.message.reply_text(f'Адреса {emals} успешно добавлен в базу данных с id: {emals_id}')
                except Exception:
                    conn.rollback()
                finally:
                    cursor.close()
                    conn.close()

# Функция которая обрабатывает сообщения в случае, если в тексте присутствуют номера телефонов
        if phone_numbers:
            update.message.reply_text("Найденные телефонные номера:\n" + "\n".join(phone_numbers))
            context.user_data['phone_numbers'] = phone_numbers
            update.message.reply_text("Хотите ли вы добавить эти номера в базу данных? Ответьте 'да'.")
            # Ожидание ответа пользователя
            def wait_for_reply(update: Update, context: CallbackContext):
                reply = update.message.text.lower()
                if reply == "да":
                    insert_phone_number(update, context)
                else:
                    update.message.reply_text("Операция отменена.")

            # Сохраняем старые обработчики
            old_handlers = context.dispatcher.handlers[0].copy()
            # Удаляем все предыдущие обработчики, чтобы избежать дублирования
            context.dispatcher.handlers[0].clear()
            context.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, wait_for_reply))
            # Восстанавливаем старые обработчики после работы функции
            def restore_handlers(context: CallbackContext):
                context.dispatcher.handlers[0].clear()
                for handler in old_handlers:
                    context.dispatcher.add_handler(handler)

            # Планируем восстановление обработчиков после 5 секунд
            context.job_queue.run_once(lambda _: restore_handlers(context), 5)
            def insert_phone_number(update: Update, context: CallbackContext):
                phone_numbers = context.user_data.get('phone_numbers', [])
                if not phone_numbers:
                    update.message.reply_text("Не указаны адреса электронной почты.")
                    return

                conn = psycopg2.connect(
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT")
                )                
                cursor = conn.cursor()
                check_query = "SELECT id FROM phone_numbers WHERE phone = %s;"
                insert_query = "INSERT INTO phone_numbers (phone) VALUES (%s) RETURNING id;"
                try:
                    for phone in phone_numbers:
                        cursor.execute(check_query, (phone,))
                        result = cursor.fetchone()
                        if result:
                            update.message.reply_text(f"Номера {phone} уже существует с id: {result[0]}")
                        else:
                            cursor.execute(insert_query, (phone,))
                            phone_id = cursor.fetchone()[0]
                            conn.commit()
                            update.message.reply_text(f'Номер {phone} успешно добавлен в базу данных с id: {phone_id}')
                except Exception:
                    conn.rollback()
                finally:
                    cursor.close()
                    conn.close()
                          
        elif not emails and not phone_numbers:
            update.message.reply_text("В этом тексте не найдено адресов электронной почты и телефонных номеров, а также пароля")
    elif result == "слово":            
            password = text
            result = verify_password(password)
            update.message.reply_text(result)


#Функция для определения предложений и слов:
def is_word_or_sentence(text):
    if len(text.split()) == 1:
        return "слово"
    else:
        return "предложение"   

# Пусть к файлу .env
dotenv_path = Path('user.env')
load_dotenv(dotenv_path=dotenv_path)

WAIT_FOR_REPLY = 1

def main() -> None:
    # Создаем объект Updater и передаем ему токен вашего бота
    bot_token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(bot_token)
    # Получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher
    # Регистрируем обработчики команд и сообщений
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dispatcher.add_handler(CommandHandler("find_emails", find_emails_command))
    dispatcher.add_handler(CommandHandler("find_phone_numbers", find_phone_numbers_command))
    dispatcher.add_handler(CommandHandler("verify_password", verify_password_command))
    dispatcher.add_handler(CommandHandler("get_release", get_release))
    dispatcher.add_handler(CommandHandler("get_uname", get_uname))
    dispatcher.add_handler(CommandHandler("get_uptime", get_uptime))
    dispatcher.add_handler(CommandHandler("get_df", get_df))
    dispatcher.add_handler(CommandHandler("get_free", get_free))
    dispatcher.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dispatcher.add_handler(CommandHandler("get_w", get_w))
    dispatcher.add_handler(CommandHandler("get_auths", get_auths))
    dispatcher.add_handler(CommandHandler("get_critical", get_critical))
    dispatcher.add_handler(CommandHandler("get_ps", get_ps))
    dispatcher.add_handler(CommandHandler("get_ss", get_ss))
    dispatcher.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dispatcher.add_handler(CommandHandler("search_in_apt_list", search_in_apt_list))
    dispatcher.add_handler(CommandHandler("get_services", get_services))
    dispatcher.add_handler(CommandHandler("get_repl_db", execute_command))
    dispatcher.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dispatcher.add_handler(CommandHandler('get_emails', get_emails))
    dispatcher.add_handler(CommandHandler('get_phone_numbers', get_phone_numbers))

    updater.start_polling()
    gif_path = 'bot_ask.gif'
    updater.bot.send_animation(chat_id='1031374406', animation=open(gif_path, "rb"))
    updater.bot.send_message(chat_id=os.getenv("CHAT_ID"), text="Чего надо хозяин! Я твой бот. Я могу выполнять различные действия. Попробуй команду /start, чтобы узнать больше.")

    updater.idle()

if __name__ == '__main__':
    main()

logger.debug('Конец программы')