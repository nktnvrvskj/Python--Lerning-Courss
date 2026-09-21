import proceses
task = []
is_start = True
def clear():print("\033[H\033[J", end="")
def check(tasks, id):
    return str(id).isdigit() and 1 <= int(id) <= len(tasks)
def task_print(tasks):
    for i, key in enumerate(tasks, 1):
        print(i, "задача:", key)
def task_add(tasks):
    print("ведите задачу")
    tasks.append(input(">>> "))
    task_print(tasks)
    input("нажмите Enter чтобы продолжить")
def task_red(tasks):
    task_print(tasks)
    print("ведите номер")
    a = input(">>> ")
    print("ведите задачу")
    if check(task, a):
        tasks[int(a) - 1] = input(">>> ")
        task_print(tasks)
        input("нажмите Enter чтобы продолжить")
        return
    print("неправельный номер");input("нажмите Enter чтобы продолжить")
def task_delete(tasks):
    print("ведите номер задачи")
    task_print(tasks)
    a = input(">>> ")
    if check(task, a):
        tasks.pop(1 - int(a))
        task_print(tasks)
        input("нажмите Enter чтобы продолжить")
        return
    print("неправельный номер");input("нажмите Enter чтобы продолжить")
while is_start:
    clear()
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
            input("нажмите Enter чтобы продолжить")
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