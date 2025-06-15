import asyncio
import pickle
import random
from collections import defaultdict

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from pathlib import Path

tik_tak_toe_router = Router()

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


AGENT_DIR = Path(__file__).resolve().parent.parent.parent / "agent"
AGENT_DIR.mkdir(parents=True, exist_ok=True)  # создаёт папку, если её нет

def load_agent(user_id):
    agent_path = AGENT_DIR / f"{user_id}_agent.pkl"
    try:
        with open(agent_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return QLearningAgent()

def save_agent(user_id, agent):
    agent_path = AGENT_DIR / f"{user_id}_agent.pkl"
    with open(agent_path, 'wb') as f:
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

@tik_tak_toe_router.message(Command("cubic"))
async def start_game(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    state = initial_state()
    agent = load_agent(user_id)

    GAMES[chat_id] = {
        'state': state,
        'agent': agent,
        'owner_id': user_id
    }

    await send_board(chat_id, "Ваш ход!", bot)


async def send_board(chat_id, text, bot: Bot, message: types.Message = None):
    state = GAMES[chat_id]['state']
    builder = InlineKeyboardBuilder()
    for i in range(9):
        label = state[i] if state[i] != ' ' else str(i + 1)
        builder.button(text=label, callback_data=str(i))
    builder.adjust(3)

    board_text = text + '\n' + render_board(state)
    if message:
        try:
            await message.edit_text(board_text, reply_markup=builder.as_markup())
        except Exception:
            msg = await bot.send_message(chat_id, board_text, reply_markup=builder.as_markup())
            GAMES[chat_id]['message_id'] = msg.message_id
    else:
        msg = await bot.send_message(chat_id, board_text, reply_markup=builder.as_markup())
        GAMES[chat_id]['message_id'] = msg.message_id


@tik_tak_toe_router.callback_query(lambda c: c.data and c.data.isdigit())
async def handle_move(callback_query: types.CallbackQuery, bot: Bot):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    data = GAMES.get(chat_id)

    if not data:
        await callback_query.answer("Начните новую игру командой /cubic", show_alert=True)
        return

    if data['owner_id'] != user_id:
        await callback_query.answer("Вы мешаете другому игроку", show_alert=True)
        return

    idx = int(callback_query.data)
    state = data['state']

    if state[idx] != ' ':
        await callback_query.answer("Недопустимый ход!")
        return

    state[idx] = 'X'
    winner = check_winner(state)
    if winner:
        await end_game(chat_id, winner, callback_query, bot)
        return

    agent = data['agent']
    action = agent.choose_action(tuple(state), available_actions(state))
    next_state = state.copy()
    next_state[action] = 'O'
    agent.learn(tuple(state), action, 0, tuple(next_state), available_actions(next_state))
    state[action] = 'O'
    winner = check_winner(state)
    if winner:
        await end_game(chat_id, winner, callback_query, bot)
        return

    await send_board(chat_id, "Ваш ход!", bot, message=callback_query.message)
    await callback_query.answer()


async def end_game(chat_id, winner, callback_query, bot: Bot):
    if winner == 'Draw':
        msg = "Ничья!"
        reward = 0.5
    elif winner == 'X':
        msg = "Вы победили!"
        reward = -1
    else:
        msg = "ИИ победил!"
        reward = 1

    data = GAMES[chat_id]
    agent = data['agent']
    user_id = data['owner_id']
    state = tuple(data['state'])
    agent.learn(state, None, reward, None, [])
    save_agent(user_id, agent)

    await bot.send_message(chat_id, msg + '\n' + render_board(state))
    del GAMES[chat_id]
    await callback_query.answer()
