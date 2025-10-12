async def get_resize_keyboard(list_value: list):
    len_list = len(list_value)
    exit_list = []

    async def func(i):
        it = [item for item in list_value[i:i + 2]]
        return it

    for j in range(len_list // 2 + len_list % 2):
        i = j * 2
        result = await func(i)
        exit_list.append(result)
    return exit_list
