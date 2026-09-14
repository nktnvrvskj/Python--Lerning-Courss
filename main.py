task = []
is_start = True
# 
def clear():
    print("\033[H\033[J", end="")
def task_print():
    i = 0
    for key in task:
        i +=1
        print(i,"задача:",key)
while(is_start):
    clear()
    print("менеджер задач")
    print("1 - посмотреть задачи")
    print("2 - добавить задачи")
    print("3 - редоктировать задачу")
    print("4 - удалить задачу")
    print("5 - выйти из приложени")
    a = input(">>> ")
    if a == "1":
        task_print()
        input("нажмите Enter чтобы продолжить")
    elif a == "2":
        print("ведите задачу")
        task.append(input(">>> "))
        task_print()
        input("нажмите Enter чтобы продолжить")
    elif a == "3":
        task_print()
        print("ведите номер")
        a = int(input(">>> "))
        print("ведите задачу")
        b = input(">>> ")
        task[a -1] = b
        task_print()
        input("нажмите Enter чтобы продолжить")
    elif a == "4":
        print("ведите номер задачи")
        task_print()
        task.pop(1-int(input(">>> ")))
        task_print()
        input("нажмите Enter чтобы продолжить")
    elif a == "5":
        is_start = False
    else:print("такого пункта нет");input("нажмите Enter чтобы продолжить")