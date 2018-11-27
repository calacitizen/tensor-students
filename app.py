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
from flask_cors import CORS

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
cors = CORS(app, resources={r"/game/*": {"origins": "*"}})
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


mock = {
 "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2": {
     "turn":True,
     "possibleMoves":[{"mate":None,"move":"Nf3","score":0.42},{"mate":None,"move":"Nc3","score":0.3},{"mate":None,"move":"Ne2","score":0.07},{"mate":None,"move":"Na3","score":-0.31},{"mate":None,"move":"Nh3","score":-0.37}],
     'answer': 'Посмотри на картинку, я отметила для возможные ходы обоих коней.',
     'bestMoves': []
 },
 "r1bqkb1r/ppp2ppp/2n2n2/3Pp3/8/P1N2N2/1PPP1PPP/R1BQKB1R b KQkq - 0 5": {
     "turn":False,
     "bestMoves":[{"mate":None,"move":"Nxd5","score":-0.04},{"mate":None,"move":"Nd4","score":-0.5},{"mate":None,"move":"Ne7","score":-1.5},{"mate":None,"move":"Nb8","score":-1.71},{"mate":None,"move":"e4","score":-1.82},{"mate":None,"move":"Na5","score":-2.92},{"mate":None,"move":"Bd6","score":-3.8},{"mate":None,"move":"Bc5","score":-4.05},{"mate":None,"move":"Nb4","score":-4.2},{"mate":None,"move":"Be7","score":-4.26},{"mate":None,"move":"a6","score":-4.36},{"mate":None,"move":"Bxa3","score":-4.44},{"mate":None,"move":"Rb8","score":-4.56},{"mate":None,"move":"Ne4","score":-4.56},{"mate":None,"move":"h6","score":-4.6},{"mate":None,"move":"Qe7","score":-4.67},{"mate":None,"move":"Nd7","score":-4.67},{"mate":None,"move":"Qd6","score":-4.81},{"mate":None,"move":"g6","score":-4.86},{"mate":None,"move":"h5","score":-4.87},{"mate":None,"move":"Bb4","score":-4.95},{"mate":None,"move":"a5","score":-4.95},{"mate":None,"move":"Ng4","score":-5.07},{"mate":None,"move":"Bd7","score":-5.24},{"mate":None,"move":"Be6","score":-5.3},{"mate":None,"move":"Bg4","score":-5.32},{"mate":None,"move":"Bf5","score":-5.39},{"mate":None,"move":"Nh5","score":-5.39},{"mate":None,"move":"b6","score":-5.5},{"mate":None,"move":"Qd7","score":-5.61},{"mate":None,"move":"Ng8","score":-5.75},{"mate":None,"move":"g5","score":-5.95},{"mate":None,"move":"Rg8","score":-6.12},{"mate":None,"move":"Bh3","score":-6.13},{"mate":None,"move":"b5","score":-6.71},{"mate":None,"move":"Ke7","score":-7.01},{"mate":None,"move":"Kd7","score":-7.04},{"mate":None,"move":"Qxd5","score":-8.01}],
     'answer': 'Я бы предложила съесть пешку на d5.',
     'possibleMoves': []
 },
 'r1bqkb1r/ppp2ppp/2n5/3np3/8/P1N2N2/1PPP1PPP/R1BQKB1R w KQkq - 0 6': {
     'bestMoves': [],
     'possibleMoves': [],
     'turn': False,
     'answer': 'Ты только что спрашивал, в этот раз подумай сам. Ты же хочешь научиться играть.',
 },   
 "r1bqkb1r/ppp2ppp/2n5/8/4Nn2/P4N2/1PPPBPPP/R1BQK2R w KQkq - 1 8": {
     "turn":True,
     "bestMoves":[{"mate":None,"move":"O-O","score":1.25},{"mate":None,"move":"Bf1","score":0.8},{"mate":None,"move":"Rg1","score":0.73},{"mate":None,"move":"Kf1","score":0.28},{"mate":None,"move":"g3","score":0.26},{"mate":None,"move":"h4","score":0.19},{"mate":None,"move":"d4","score":-0.07},{"mate":None,"move":"h3","score":-0.25},{"mate":None,"move":"d3","score":-0.32},{"mate":None,"move":"Bc4","score":-0.48},{"mate":None,"move":"c3","score":-0.49},{"mate":None,"move":"Rb1","score":-0.81},{"mate":None,"move":"c4","score":-0.84},{"mate":None,"move":"b4","score":-0.86},{"mate":None,"move":"Ng3","score":-0.9},{"mate":None,"move":"Nfg5","score":-1.12},{"mate":None,"move":"g4","score":-1.14},{"mate":None,"move":"a4","score":-1.16},{"mate":None,"move":"b3","score":-1.2},{"mate":None,"move":"Neg5","score":-1.32},{"mate":None,"move":"Bd3","score":-1.32},{"mate":None,"move":"Ra2","score":-1.46},{"mate":None,"move":"Nc3","score":-1.47},{"mate":None,"move":"Bb5","score":-1.48},{"mate":None,"move":"Ng1","score":-1.63},{"mate":None,"move":"Ne5","score":-2.84},{"mate":None,"move":"Ba6","score":-3.19},{"mate":None,"move":"Nf6+","score":-3.92},{"mate":None,"move":"Nd6+","score":-4.07},{"mate":None,"move":"Nh4","score":-4.15},{"mate":None,"move":"Nd4","score":-4.44},{"mate":None,"move":"Nc5","score":-4.79},{"mate":-1,"move":"Rf1","score":-9999}],
     'answer': 'Пожалуй стоит сделать рокировку.',
     'possibleMoves': []
 },
 "r1bqkb1r/ppp2ppp/2n5/8/4N3/P4N2/1PPPnPPP/R1BQ1RK1 w kq - 0 9": {
     "turn":True,
     "bestMoves":[],     
     'answer': 'Кажется вам поставили шах.',
     'possibleMoves': []
 },
 "r2qkb1r/ppp2ppp/2n5/8/4N1b1/P4N2/1PPPQPPP/R1B2RK1 w kq - 1 10": {
     "turn":True,
     "bestMoves":[{"mate":1,"move":"Nf6#","score":9999},{"mate":None,"move":"Nd6+","score":4.92},{"mate":None,"move":"h3","score":2.09},{"mate":None,"move":"d4","score":1.41},{"mate":None,"move":"Re1","score":1.32},{"mate":None,"move":"Rd1","score":1.23},{"mate":None,"move":"c3","score":1.2},{"mate":None,"move":"b4","score":1.2},{"mate":None,"move":"a4","score":1.07},{"mate":None,"move":"b3","score":1.03},{"mate":None,"move":"d3","score":1},{"mate":None,"move":"Qe3","score":0.95},{"mate":None,"move":"Rb1","score":0.87},{"mate":None,"move":"Ng3+","score":0.73},{"mate":None,"move":"Neg5+","score":0.69},{"mate":None,"move":"Nc3+","score":0.52},{"mate":None,"move":"Qd1","score":0.5},{"mate":None,"move":"Nc5+","score":0.46},{"mate":None,"move":"Kh1","score":0.46},{"mate":None,"move":"h4","score":0.41},{"mate":None,"move":"Ra2","score":0.4},{"mate":None,"move":"Qc4","score":0.37},{"mate":None,"move":"Qe1","score":0.28},{"mate":None,"move":"c4","score":0.1},{"mate":None,"move":"Qb5","score":-0.11},{"mate":None,"move":"g3","score":-0.36},{"mate":None,"move":"Qd3","score":-1.44},{"mate":None,"move":"Nd4","score":-6.7},{"mate":None,"move":"Ne5","score":-10},{"mate":None,"move":"Nfg5","score":-10.68},{"mate":None,"move":"Qa6","score":-11.1},{"mate":None,"move":"Nh4","score":-11.41},{"mate":None,"move":"Ne1","score":-12.37}],
     'answer': 'Если сходишь правильно, можешь поставить мат.',
     'possibleMoves': []
 }
}


@app.route('/game/ask', methods=['POST'])
def api_ask():
    game = request.get_json(force=True)
    moves = {}
    moves['variants'] = []
    if  'type' in game:
        if game['type'] == 'n':
            return jsonify(mock["rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"])
    if  'state' in game:
        #board = chess.Board(game['game_set'])
        #handler = chess.uci.InfoHandler()
        #engine = chess.uci.popen_engine(os.getcwd() + '/stockfish-9-mac/Mac/stockfish-9-64')
        #engine.info_handlers.append(handler)
        #engine.position(board)
        #moves['turn'] = board.turn
        #for el in board.legal_moves:
        #    engine.go(searchmoves=[el],movetime=1000)
        #    if (handler.info["score"][1].cp is None or isinstance(handler.info["score"][1].cp, float) ):
        #        if handler.info["score"][1].mate == 1:
        #            moves['variants'].append({"move": board.san(el), "score": 9999, "mate": handler.info["score"][1].mate})
        #        elif handler.info["score"][1].mate == -1:
        #            moves['variants'].append({"move": board.san(el), "score": -9999, "mate": handler.info["score"][1].mate})
        #        else:
        #            moves['variants'].append({"move": board.san(el), "score": -9999, "mate": handler.info["score"][1].mate})
        #    else:
        #        moves['variants'].append({"move": board.san(el), "score": round(handler.info["score"][1].cp/100.0,2), "mate": handler.info["score"][1].mate}) 
        #    moves['variants'].sort(key=operator.itemgetter('score'), reverse=True)
        return jsonify(mock[game['state']])
        #return jsonify(moves)
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
