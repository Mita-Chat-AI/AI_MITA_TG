import time
from aiogram.types import Message
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.enums.chat_type import ChatType
from aiogram_i18n import I18nContext

# from .mita import mita


ask_router = Router()

# memory_time = {}
# last_bot_message = {}


# @ask_router.message(Command("ask"), F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
# async def ask(message: Message, i18n: I18nContext, bot: Bot) -> None:
#     await message.reply(text=i18n.get("waiting_for_message_neural"))
#     user_id = message.from_user.id
#     bot_response = await mita(message, bot, i18n)

#     last_bot_message[user_id] = bot_response.message_id
#     memory_time[user_id] = time.time()


# @ask_router.message(F.reply_to_message, F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
# async def handle_reply_to_bot(message: Message, bot: Bot) -> None:
#     user_id = message.from_user.id

#     if user_id in last_bot_message and message.reply_to_message.message_id == last_bot_message[user_id]:
#         bot_response = await mita(message, bot)
#         last_bot_message[user_id] = bot_response.message_id



import asyncio
import pickle
import random
from collections import defaultdict

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Q-Learning Agent
class QLearningAgent:
    def __init__(self, epsilon=0.2, alpha=0.3, gamma=0.9):
        self.q = defaultdict(float)
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def get_q(self, state, action):
        return self.q[(state, action)]

    def choose_action(self, state, available_actions):
        if random.random() < self.epsilon:
            return random.choice(available_actions)
        qs = [self.get_q(state, a) for a in available_actions]
        max_q = max(qs)
        max_actions = [a for a, q_val in zip(available_actions, qs) if q_val == max_q]
        return random.choice(max_actions)

    def learn(self, state, action, reward, next_state, next_actions):
        future_q = 0
        if next_actions:
            future_q = max([self.get_q(next_state, a) for a in next_actions])
        old_q = self.get_q(state, action)
        self.q[(state, action)] = old_q + self.alpha * (reward + self.gamma * future_q - old_q)

# Save/load agent per user

def load_agent(user_id):
    try:
        with open(f'{user_id}_agent.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return QLearningAgent()

def save_agent(user_id, agent):
    with open(f'{user_id}_agent.pkl', 'wb') as f:
        pickle.dump(agent, f)

# Game state
GAMES = {}

def initial_state():
    return [' '] * 9

# Helpers

def check_winner(state):
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for i, j, k in wins:
        if state[i] == state[j] == state[k] and state[i] != ' ':
            return state[i]
    if ' ' not in state:
        return 'Draw'
    return None

def render_board(state):
    return '\n'.join([' | '.join(state[i:i+3]) for i in range(0,9,3)])

def available_actions(state):
    return [i for i, val in enumerate(state) if val == ' ']

# Telegram handlers

@ask_router.message(Command("cubic"))
async def start_game(message: types.Message, bot: Bot):
    state = initial_state()
    agent = load_agent(message.from_user.id)
    GAMES[message.from_user.id] = {'state': state, 'agent': agent, 'history': []}
    await send_board(message.from_user.id, "Ваш ход!", bot)

async def send_board(user_id, text, bot: Bot):
    state = GAMES[user_id]['state']
    builder = InlineKeyboardBuilder()
    for i in range(9):
        label = state[i] if state[i] != ' ' else str(i+1)
        builder.button(text=label, callback_data=str(i))
    builder.adjust(3)
    await bot.send_message(user_id, text + '\n' + render_board(state), reply_markup=builder.as_markup())

@ask_router.callback_query(lambda c: c.data and c.data.isdigit())
async def handle_move(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    data = GAMES.get(user_id)
    if not data:
        await callback_query.answer("Начните новую игру командой /start")
        return
    idx = int(callback_query.data)
    state = data['state']

    if state[idx] != ' ':
        await callback_query.answer("Недопустимый ход!")
        return

    state[idx] = 'X'
    winner = check_winner(state)
    if winner:
        await end_game(user_id, winner, callback_query, bot)
        return

    agent = data['agent']
    action = agent.choose_action(tuple(state), available_actions(state))
    next_state = state.copy()
    next_state[action] = 'O'
    agent.learn(tuple(state), action, 0, tuple(next_state), available_actions(next_state))
    state[action] = 'O'
    winner = check_winner(state)
    if winner:
        await end_game(user_id, winner, callback_query, bot)
        return

    await send_board(user_id, "Ваш ход!", bot)
    await callback_query.answer()  # ответить, чтобы убрать "часики" в клиенте

async def end_game(user_id, winner, callback_query, bot: Bot):
    if winner == 'Draw':
        msg = "Ничья!"
        reward = 0.5
    elif winner == 'X':
        msg = "Вы победили!"
        reward = -1
    else:
        msg = "ИИ победил!"
        reward = 1

    data = GAMES[user_id]
    agent = data['agent']
    state = tuple(data['state'])
    agent.learn(state, None, reward, None, [])  # финальное обновление
    save_agent(user_id, agent)
    await bot.send_message(user_id, msg + '\n' + render_board(state))
    del GAMES[user_id]
    await callback_query.answer()

