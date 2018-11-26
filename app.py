# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import chess
import chess.uci
import operator

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

question_types = {
    'show_best_move': [
        'Как мне лучше сходить',
        'Куда можно сходить'
    ]
}

question_by_piece = {
    'p': ['пешкой', 'пешка'],
    'k': ['король', 'королем', 'королём'],
    'q': ['королева', 'королевой', 'ферзь', 'ферзём', 'ферзем'],
    'r': ['ладья', 'ладьей', 'ладьёй'],
    'b': ['слон', 'слоном', 'офицером', 'офицер'],
    'n': ['конь', 'конем', 'конём', 'кобыла', 'кобылой']
}

answer_types = {
   'mate': 'Если сходишь правильно, можешь поставить мат.',
   'check': 'Не робей. Сделай шах!',
   'danger_check': 'Кажется вам поставили шах.',
   'you_done': 'Игра окончена вам поставили мат.',
   'castling': 'Пожалуй стоит сделать рокировку.', 
   'best_move': 'Вот лучшие ходы в данный момент.',
   'capture': 'Я бы предложила съесть'
}

whereby = {
    'p': 'пешкой',
    'k': 'королём',
    'q': 'ферзём',
    'r': 'ладьёй',
    'b': 'слоном',
    'n': 'конём'
}

what = {
    'p': 'пешку',
    'k': 'короля',
    'q': 'ферзя',
    'r': 'ладью',
    'b': 'слона',
    'n': 'коня'
}

def init_board(fen_string):
    board = chess.Board(fen_string)
    handler = chess.uci.InfoHandler()
    engine = chess.uci.popen_engine(os.getcwd() + '/stockfish-9-mac/Mac/stockfish-9-64')
    engine.info_handlers.append(handler)
    engine.position(board)
    moves = {}
    moves['turn'] = board.turn
    moves['bestMoves'] = []
    moves['possibleMoves'] = []
    moves['answer'] = ''
    return {'board': board, 'engine': engine, 'moves': moves, 'handler': handler}

def get_cp(handler):
    return handler.info["score"][1].cp

def get_move(board, el):
    return board.san(el)

def get_mate(handler):
    return handler.info["score"][1].mate

def fill_best_moves(moves, board, mate, score, el):
    moves['bestMoves'].append({"move": get_move(board, el), "score": score, "mate": mate})

def is_question_asked(game):
    return 'state' in game and 'question' in game

def is_best_castling(best_moves):
    return len(best_moves)and (best_moves[0]['move'] == "O-O" or best_moves[0]['move'] == "O-O-O") 

def is_best_checkmate(best_moves):
    return len(best_moves) and ("#" in best_moves[0]['move'])

def is_best_check(best_moves):
    return len(best_moves) and ("+" in best_moves[0]['move'])

def is_best_capture(best_moves):
    return len(best_moves) and ("x" in best_moves[0]['move'])

def capture_answer(best_moves, board):
    capture_split = best_moves[0]['move'].split('x')
    piece = capture_split[0].lower()
    piece_place = capture_split[1].capitalize()
    piece_to_kill = board.piece_at(getattr(chess, piece_place)).symbol()
    if piece not in whereby:
        piece = 'p'
    return answer_types['capture'] + ' ' + what[piece_to_kill] + ' на ' + piece_place + ' ' + whereby[piece] + '.'

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/game')
def game():
    return render_template('pages/game.html')

@app.route('/game/ask', methods=['POST'])
def api_ask():
    game = request.get_json(force=True)
    if is_question_asked(game):
        settings = init_board(game['state'])

        for el in settings['board'].legal_moves:
            settings['engine'].go(searchmoves=[el],movetime=10)
            mate = get_mate(settings['handler'])
            if (get_cp(settings['handler']) is None or isinstance(get_cp(settings['handler']), float) ):
                if mate == 1:
                    fill_best_moves(settings['moves'], settings['board'], mate, 9999, el)
                else:
                    fill_best_moves(settings['moves'], settings['board'], mate, -9999, el)
            else:
                fill_best_moves(settings['moves'], settings['board'], mate, round(get_cp(settings['handler'])/100.0,2), el)
            settings['moves']['bestMoves'].sort(key=operator.itemgetter('score'), reverse=True)
        

        if is_best_capture(settings['moves']['bestMoves']):
            settings['moves']['answer'] = capture_answer(settings['moves']['bestMoves'], settings['board'])

        elif settings['board'].is_checkmate():
            settings['moves']['answer'] = answer_types['you_done']
            
        elif settings['board'].is_check():
            settings['moves']['answer'] = answer_types['danger_check']

        elif is_best_castling(settings['moves']['bestMoves']):
            settings['moves']['answer'] = answer_types['castling']

        elif is_best_checkmate(settings['moves']['bestMoves']):
            settings['moves']['answer'] = answer_types['mate']

        elif is_best_check(settings['moves']['bestMoves']):
            settings['moves']['answer'] = answer_types['check']
    
        else:
            settings['moves']['answer'] = answer_types['best_move']

        return jsonify(settings['moves'])
    else:
        return jsonify({'error': 'no params entered'})


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	app.run(host='0.0.0.0', port=port,debug=True)
