from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from postgresql import DB
import uvicorn

app = FastAPI()
database = DB()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("shutdown")
def shutdown_event():
    database.db.close()


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/about")
async def main(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/sing_up")
async def main(request: Request):
    return templates.TemplateResponse("sing_up.html", {"request": request})


@app.post("/sing_up")
async def sing_up(request: Request, nick: str = Form(...), password: str = Form(...)):
    r = database.sing_up(nick, password)

    if not r:
        return templates.TemplateResponse("sing_up.html", {
            "request": request, "status": 1,
            "message": "Пользователь с таким именем уже зарегистрирован"
        })

    return RedirectResponse(f'/user/{nick}')


@app.get("/sing_in")
async def search(request: Request):
    return templates.TemplateResponse("sing_in.html", {"request": request})


@app.post("/sing_in")
async def sing_up(request: Request, nick: str = Form(...), password: str = Form(...)):
    r = database.search(nick)

    if not r:
        return templates.TemplateResponse("sing_in.html", {"request": request, "status": 1,
                                                           "message": "Пользователь с таким именем нету"})

    elif r[0][1] != password:
        return templates.TemplateResponse("sing_in.html",
                                          {"request": request, "status": 1, "message": "Пароли не совпадают"})

    return RedirectResponse(f'/user/{nick}')


@app.post("/search")
async def search(request: Request, name: str = Form(...)):
    us = database.search(name)
    if us:
        return RedirectResponse(f'/user/{name}')

    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/search")
async def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/user/{nick}")
@app.post("/user/{nick}")
async def user(request: Request, nick: str, userID: Optional[str] = Cookie(None)):
    us = database.search(nick)
    if not us:
        return RedirectResponse(f'/search')

    cook = userID.split(",")
    if us[0][1] == cook[1] and us[0][0] == cook[0]:
        return templates.TemplateResponse("my_profile.html", {"request": request, "name": nick, "status": us[0][2]})

    else:
        return templates.TemplateResponse("no_my_proifle.html",
                                          {"request": request, "name": nick, "status": us[0][2]})


@app.get("/edit/{nick}")
async def edit(request: Request, nick: str, userID: Optional[str] = Cookie(None)):
    r = database.search(nick)
    us = userID.split(",")

    if not r:
        return RedirectResponse('/')

    elif nick == us[0] and r[0][1] == us[1]:
        return templates.TemplateResponse("edit.html", {"request": request, "nick": us[0], "status": r[0][2]})

    return RedirectResponse('/')


@app.post("/editor")
async def edit(status: str = Form(...), nick: str = Form(...),
    userID: Optional[str] = Cookie(None)):
    name = userID.split(",")

    if name[0] != nick:
        if not database.search(nick):
            response = RedirectResponse(f"/user/{nick}")
            response.set_cookie(key="userID", value=f"{nick},{name[1]}")
            database.update(name[0], nick, status)

            return response

    else:
        database.update(name[0], nick, status)

    return RedirectResponse(f"/user/{name[0]}")
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=443)
