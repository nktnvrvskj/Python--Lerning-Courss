def clear():print("\033[H\033[J", end="")
def check(tasks, id):
    return str(id).isdigit() and 1 <= int(id) <= len(tasks)