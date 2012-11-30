# coding: utf8


def open_page():
    import webbrowser
    webbrowser.open('http://127.0.0.1:8000/teste/default/index')
    
from gluon.scheduler import Scheduler
Scheduler(db, dict(func=open_page))
