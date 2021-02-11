#!/usr/bin/env python3
import asyncio
import aiohttp
from aiohttp.web import Application, Response, HTTPOk, run_app


async def index(request):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:410/') as resp:
            print(resp.status)
            print(await resp.text())
            return Response(status=200, text='test')

async def init(loop):
    app = Application()
    app.router.add_get('/', index)
    return app


loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))
run_app(app, port=8080)