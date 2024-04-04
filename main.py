from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from contextlib import closing
from typing import Optional
from fastapi.staticfiles import StaticFiles

import sqlite3

SEARCH_PARAMETERS = ('author', 'published', 'title')


class Book(BaseModel):
    """Model for book in database"""
    published: int
    author: str
    title: str
    first_sentence: str


class Settings(BaseSettings):
    database: str
    model_config = SettingsConfigDict(env_file='.env')


# Init settings and app
settings = Settings()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='templates')


def get_db():
    with closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


@app.get('/index/', response_class=HTMLResponse)
def index(request: Request):
    
    context = {
        'request': request
    }

    return templates.TemplateResponse(
       "index.html", context
    )


@app.get('/books/', response_class=HTMLResponse)
def all_books(request: Request, db: sqlite3.Connection = Depends(get_db)):
    cur = db.cursor()
    query = """SELECT * FROM books;"""
    res = cur.execute(query)
    books = res.fetchall()

    # return {'books': res.fetchall()}

    context = {
        'books': books, 
        'request': request
    }

    return templates.TemplateResponse(
        'books.html', context
    )

@app.get('/search/', response_class=HTMLResponse)
def search(request: Request):
    context = {
        'request': request
    }

    return templates.TemplateResponse(
        'search.html', context
    )

@app.post('/books/', status_code=201)
def create_book(
    book: Book,
    db: sqlite3.Connection = Depends(get_db)
):
    book_dict = book.model_dump()
    cur = db.cursor()
    try:
        query = """
        INSERT INTO books(published, author, title, first_sentence)
        VALUES(:published, :author, :title, :first_sentence);
        """
        cur.execute(query, book_dict)
        db.commit()
    except sqlite3.Error as err:
        raise HTTPException(
            status_code=409,
            detail={
                'error': str(err)
            }
        )

    book_dict['id'] = cur.lastrowid
    
    return book_dict


@app.delete('/books/{id}', status_code=200)
def delete_book(
    id: int,
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()
    try:
        query = """
        DELETE FROM books
        WHERE id = :id;
        """
        cur.execute(query, (id,))
        db.commit()
    except sqlite3.Error as err:
        raise HTTPException(
            status_code=409,
            detail={
                'error': str(err)
            }
        )

    return {'message': 'Item deleted'}


@app.post('/search/', response_class=HTMLResponse, status_code=201)
def search_book(
    request: Request,
    published: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    db: sqlite3.Connection = Depends(get_db)
):
    cur = db.cursor()

    query = """
    SELECT * FROM books
    """

    conditions: list[str] = []
    values: list[str] = []
    arguments = locals()

    # Construct the query string
    for parameter in SEARCH_PARAMETERS:
        if arguments[parameter]:
            value = arguments[parameter]
            conditions.append(f"{parameter} LIKE ?")
            values.append(f"%{value}%")

    if conditions:
        query += " WHERE "
        query += " AND ".join(conditions)

    query += ";"
    res = cur.execute(query, values)

    books = res.fetchall()

    context = {
        'request': request,
        'books': books
    }

    return templates.TemplateResponse(
        'partials/search_results.html', context
    )


@app.put('/books/{id}', status_code=200)
def update_book(
    id: int,
    book: Book,
    db: sqlite3.Connection = Depends(get_db)
):
    book_dict = book.model_dump()
    book_dict['id'] = id
    cur = db.cursor()
    try:
        validation_query = """
        SELECT * FROM books
        WHERE id = :id;
        """

        res = cur.execute(validation_query, (id, )).fetchone()

        if res is None:
            raise Exception(f"Book with id: {id} not found.")

        query = """
        UPDATE books
        SET published = :published, author = :author, title = :title, first_sentence = :first_sentence
        WHERE id = :id;
        """
        cur.execute(query, book_dict)
        db.commit()
    except sqlite3.Error as err:
        raise HTTPException(
            status_code=400,
            detail={
                'error': str(err)
            }
        )
    except Exception as err:
        raise HTTPException(
            status_code=400,
            detail={
                'error': str(err)
            }
        )

    return book_dict
