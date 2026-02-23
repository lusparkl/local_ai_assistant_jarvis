from tools.memory import retrieve_memory
from tools.weather import get_current_weather, get_forecast
from tools.keyboard import paste_from_user_keyboard, copy_to_user_keyboard
from tools.todo import add_todo, get_todos, delete_todo

tools = {
    retrieve_memory: True,
    get_current_weather: True,
    get_forecast: True,
    paste_from_user_keyboard: True,
    copy_to_user_keyboard: True,
    add_todo: True,
    get_todos: True,
    delete_todo: True
}

def get_available_tools():
    available_tools = {}
    for key, value in tools.items():
        if value:
            available_tools[key.__name__] = key
    
    return available_tools

