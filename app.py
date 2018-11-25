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


@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/game')
def game():
    return render_template('pages/game.html')

@app.route('/game/ask', methods=['POST'])
def api_ask():
    game = request.get_json(force=True)
    if  game['game_set']:
        board = chess.Board(game['game_set'])
        handler = chess.uci.InfoHandler()
        engine = chess.uci.popen_engine('/Users/mraz/Projects/stockfish-9-mac/Mac/stockfish-9-64')
        engine.info_handlers.append(handler)
        engine.position(board)
        moves = {}
        moves['turn'] = board.turn
        moves['variants'] = []
        for el in board.legal_moves:
            engine.go(searchmoves=[el],movetime=1000)
            if (handler.info["score"][1].cp is None or isinstance(handler.info["score"][1].cp, float) ):
                if handler.info["score"][1].mate == 1:
                    moves['variants'].append({"move": board.san(el), "score": 9999, "mate": handler.info["score"][1].mate})
                elif handler.info["score"][1].mate == -1:
                    moves['variants'].append({"move": board.san(el), "score": -9999, "mate": handler.info["score"][1].mate})
                else:
                    moves['variants'].append({"move": board.san(el), "score": -9999, "mate": handler.info["score"][1].mate})
            else:
                moves['variants'].append({"move": board.san(el), "score": round(handler.info["score"][1].cp/100.0,2), "mate": handler.info["score"][1].mate}) 
            moves['variants'].sort(key=operator.itemgetter('score'), reverse=True)
        return jsonify(moves)
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
