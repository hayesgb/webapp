from quart import Quart, websocket
from quart import render_template

app = Quart(__name__)

@app.route('/')
async def index():
    return await render_template('base.html')

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('index')

app.run()
