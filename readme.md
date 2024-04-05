# FastAPI Books Project

## A book inventory system built with FastAPI (Python), HTMX, Jinja 2 and Tailwind CSS

**Please note:** Running this app requires the installation of Tailwind CSS and Python Requirements (requirements.txt)

## How to run the application locally:
1. Have Python installed. If not installed, follow the installation steps for your OS. [Python Install](https://www.python.org/downloads/)
2. Create a .venv by running `python -m venv .venv`
3. Activate the .venv
    ```
    .venv\Scripts\activate
    ```
4. Install the requirements.txt `pip install -r requirements.txt`
5. Install tailwind css, then `cd tailwindcss/` and run `npx tailwindcss -i ./styles/app.css -o ../static/css/app.css --watch`
5. Run the app at localhost:8000