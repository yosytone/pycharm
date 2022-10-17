import requests
import os
import json
import datetime
import sys

test_path = os.getcwd()
check_file = os.path.exists(test_path + '/tasks')

# Создание и проверка директории tasks.

if check_file == True:
    pass
else:
    os.mkdir("tasks")

# Получение и обработка ошибок списков users и todos связанных с сетью.

try:
    todos = requests.get('https://json.medrocket.ru/todos', timeout=3)
    users = requests.get('https://json.medrocket.ru/users', timeout=3)
    todos.raise_for_status()
    users.raise_for_status()
except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
    sys.exit()
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
    sys.exit()
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
    sys.exit()
except requests.exceptions.RequestException as err:
    print("OOps: Something Else", err)
    sys.exit()

# Запись данных в txt формат файла

with open('todos.txt', 'wb') as f:
    f.write(todos.content)
with open('users.txt', 'wb') as f:
    f.write(users.content)

# Обработка ошибок файлов users и todos

todos_path = str(test_path) + '/todos.txt'
users_path = str(test_path) + '/users.txt'
if os.path.getsize(todos_path) == 0 or os.path.getsize(users_path) == 0:
    print('Один из файлов пуст')
    sys.exit()

# Чтение файлов

with open("todos.txt") as file:
    dict_todos = file.read()

with open("users.txt") as file:
    dict_users = file.read()

try:
    data_todos = json.loads(dict_todos)
    data_users = json.loads(dict_users)
except json.decoder.JSONDecodeError:
    print('JSONDecodeError("Expecting value", s, err.value) from None')
    sys.exit('Один из файлов некорректен')


# Подсчет всех задач

def Count_task(key):
    sum = 0
    for i in range(0, len(data_todos)):
        try:
            if data_todos[i].get('userId') == key:
                sum = sum + 1
        except:
            print('Задачи некорректны' + data_users(data_todos[i].get('userId')).get('name'))
            os.remove(str(test_path) + '/tasks/' + str(data_users(data_todos[i].get('userId')).get('name')))
    return sum


# Подсчет и вывод Актуальных и Завершенных задач

def Count_resolved_task(key_1):
    sum1 = 0
    sum2 = 0
    line_2 = str()
    line_1 = str()

    def Cut(line):  # Обрезка текста
        if len(line) > 46:
            line = line[0:47] + '...'
        return line

    for i in range(0, len(data_todos)):
        if data_todos[i].get('userId') == key_1:
            if data_todos[i].get('completed') == True:
                sum1 = sum1 + 1
                line_1 = line_1 + '- ' + Cut(data_todos[i].get('title')) + '\n'
            else:
                sum2 = sum2 + 1
                line_2 = line_2 + '- ' + Cut(data_todos[i].get('title')) + '\n'
    return sum1, sum2, line_2, line_1


# Запись данных в файл.

def createFile(name_txt, j):
    with open(str(test_path) + '/tasks/' + str(name_txt), 'w', encoding='utf-8') as f:
        f.write('# Отчёт для' + ' ' + i[0].get('company')['name'] + '.' + '\n')
        f.write(i[0].get('name') + ' <' + i[0].get('email') + '> ' + now.strftime(
            "%d-%m-%Y %H:%M") + '\n')
        f.write('Всего задач: ' + str(Count_task(j)) + '\n' + '\n')
        f.write('## Актуальные задачи (' + str(Count_resolved_task(j)[0]) + '):' + '\n')
        f.write((Count_resolved_task(j)[2] + '\n'))
        f.write('## Завершённые задачи (' + str(Count_resolved_task(j)[1]) + '):' + '\n')
        f.write((Count_resolved_task(j)[3]))


# Переименование файла.

def renameFile(name_txt):
    file_oldname = os.path.join(str(test_path) + '/tasks/', name_txt)
    file_new_name = os.path.join(str(test_path) + '/tasks/', 'old_' + name_txt + str(now.today().strftime(
        "%Y-%m-%dT%H:%M")))
    if os.path.exists(file_new_name) == False:
        os.rename(file_oldname, file_new_name)


# Добавление в список всех названий текстовых файлов из директории tasks.
names = []
for filename in os.listdir("tasks"):
    with open(os.path.join("tasks", filename), 'r') as f:
        text = f.name
        names.append(text[6:])

# Добавление в список всех имен из users.txt

dates = []
j = 0
for i in range(0, len(data_users)):
    j = i + 1
    d = data_users[i]
    list = [d, 0, 0]  # 1-эл Данные юзера 2-эл Сущ. ли актуальные данные в tasks 3-эм Сущ. ли архивные данные в tasks.
    dates.append(list)

# Проверка на наличие созданных файлов в директории tasks.

for i in dates:
    name_txt = i[0].get('name')
    for c in names:
        if ((name_txt in c) & ('old' in c)):
            i[2] = 1
        if ((name_txt in c) & ('old' not in c)):
            i[1] = 1

# Если файл уже есть, то на его основе создается новый файл (старый), а текущий перезаписывается на новый.

j = 0
moscow_time = datetime.timezone(datetime.timedelta(hours=3))
now = datetime.datetime.now(moscow_time)
for i in dates:
    j = j + 1
    uid = i[0].get('id')

    if (((i[1] == 1) & (i[2] == 1)) or ((i[1] == 1) & (i[2] == 0))):
        name_txt = i[0].get('name')
        renameFile(name_txt)
        createFile(name_txt, uid)

    if (((i[1] == 0) & (i[2] == 0)) or ((i[1] == 0) & (i[2] == 1))):
        name_txt = i[0].get('name')
        createFile(name_txt, uid)
