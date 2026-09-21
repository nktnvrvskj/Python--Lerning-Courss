import json
import os
task = []
name_file = "task.json"
def load():
    global task
    if not os.path.exists(name_file):
        save()
        return
    with open(name_file, "r", encoding="utf-8") as f:
        task = json.load(f)
def save():
    global task
    with open(name_file, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=4, ensure_ascii=False)
def clear():print("\033[H\033[J", end="")
def check(tasks, id):
    return str(id).isdigit() and 1 <= int(id) <= len(tasks)
def task_print(tasks,pause=True):
    for i, key in enumerate(tasks, 1):
        print(i, "задача:", key)
    if pause:input("нажмите Enter чтобы продолжить")

def task_add(tasks):
    print("ведите задачу")
    tasks.append(input(">>> "))
    task_print(tasks)
def task_red(tasks):
    task_print(tasks)
    print("ведите номер")
    a = input(">>> ")
    print("ведите задачу")
    if check(task, a):
        tasks[int(a) - 1] = input(">>> ")
        task_print(tasks)
        return
    print("неправельный номер");input("нажмите Enter чтобы продолжить")
def task_delete(tasks):
    print("ведите номер задачи")
    task_print(tasks,False)
    a = input(">>> ")
    if check(task, a):
        tasks.pop(1 - int(a))
        task_print(tasks)
        return
    print("неправельный номер");input("нажмите Enter чтобы продолжить")
def main():
    global task
    load()
    is_start = True
    while is_start:
        clear()
        save()
        print("менеджер задач")
        print("1 - посмотреть задачи")
        print("2 - добавить задачи")
        print("3 - редоктировать задачу")
        print("4 - удалить задачу")
        print("5 - выйти из приложени")
        a = input(">>> ")
        match a:
            case "1":
                task_print(task)
            case "2":
                task_add(task)
            case "3":
                task_red(task)
            case "4":
                task_delete(task)
            case "5":
                is_start = False
            case _:
                print("такого пункта нет");input("нажмите Enter чтобы продолжить")
if __name__ == '__main__':
    main()