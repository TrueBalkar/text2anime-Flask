from flask import Blueprint, render_template, request, flash, session
from Dataframe.db import DB
from Model import model

page = Blueprint('page', __name__)
db = DB()
df, desc, char_desc, reviews, shiet, char_desc_general, reviews_general, desc_general, laser, stop = db.get_df()


@page.route('/', methods=["GET", "POST"])
def home():
    if request.method == "GET":
        if 'reset' in request.args:
            keys = [item for item in session.keys()]
            for i in keys:
                session.pop(i)
            del keys

    if 'progress' not in session:
        session['progress'] = None
        session['progress_end'] = None
        session['task_started'] = None

    if 'probabilities' not in session:
        session['probabilities'] = None

    if 'searched' not in session:
        session['searched'] = False

    if 'page_num' not in session:
        session['page_num'] = 0

    if session['searched'] is False:
        session['indexes'] = [i for i in range(150)]

    probabilities, image, title, description, themes, genres, season, url = get_info(session['page_num'],
                                                                                     session['indexes'])

    if request.method == "GET":
        filters = request.args.getlist("genres")
        text = request.args.get("text")
        context_importance = request.args.get("context_importance")
        word_importance = request.args.get("word_importance")
        weights = request.args.getlist("weights")
        if text:
            print(text)
            print(weights)
            if len(text) == 0:
                flash("Please type something to work with!", category="error")
                print("WTF?!")
            else:
                for index, item in enumerate(weights):
                    weights[index] = float(item)
                if sum(weights) == 0:
                    auto_weight = True
                else:
                    for index in range(len(weights)):
                        weights[index] /= sum(weights)
                    auto_weight = False

                session['task_started'] = True
                items = model.search_similiar_items(text, stop, shiet, char_desc_general, reviews_general, desc_general,
                                                    df, laser, char_desc, reviews, desc, word_importance,
                                                    context_importance, weights, auto_weight, filters)

                session['progress_end'] = next(items)
                session['task_started'] = False
                for item in items:
                    if item == 'STOP':
                        break
                    session['progress'] = item

                items = next(items)
                session['indexes'] = [int(item) for item in items.index]
                session['probabilities'] = [float(item) for item in items.values]
                del items
                session['page_num'] = 0
                session['searched'] = True
                probabilities, image, title, description, themes, genres, season, url\
                    = get_info(session['page_num'], session['indexes'], session['probabilities'])
                session['task_started'] = None

        if 'next' in request.args:
            if session['page_num'] < 9:
                session['page_num'] += 1
                probabilities, image, title, description, themes, genres, season, url\
                    = get_info(session['page_num'], session['indexes'], session['probabilities'])

        if 'previous' in request.args:
            if session['page_num'] > 0:
                session['page_num'] -= 1
                probabilities, image, title, description, themes, genres, season, url\
                    = get_info(session['page_num'], session['indexes'], session['probabilities'])

        if 'page' in request.args:
            session['page_num'] = int(request.args.get("page"))
            probabilities, image, title, description, themes, genres, season, url \
                = get_info(session['page_num'], session['indexes'], session['probabilities'])

    return render_template("base.html", image=image, title=title, description=description, themes=themes, genres=genres,
                           season=season, url=url, probabilities=probabilities, searched=session['searched'], zip=zip,
                           progress=session['progress'], progress_end=session['progress_end'],
                           task_started=session['task_started'])


def get_info(page_num, indexes, probabilities=None):
    first = page_num * 15
    last = (page_num + 1) * 15
    indexes = indexes[first:last]

    if probabilities is not None:
        probabilities = probabilities[first:last]

    image = []
    title = []
    description = []
    themes = []
    genres = []
    season = []
    url = []
    for index in indexes:
        image.append(df["Image"][index])
        title.append(df["Title"][index])
        if len(df["Description"][index]) > 260:
            description.append(" ".join(df["Description"][index][:260].split()[:-1]) + "...")
        else:
            description.append(df["Description"][index])
        themes.append(df["Themes"][index])
        genres.append(df["Genres"][index])
        season.append(df["Premier season"][index])
        url.append(df["Url"][index])

    return probabilities, image, title, description, themes, genres, season, url
