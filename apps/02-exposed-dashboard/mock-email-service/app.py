import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import aiohttp_jinja2
import jinja2
from aiohttp import web
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).parent
TEMPLATES_DIR = CURRENT_DIR / "templates"

DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']


@dataclass
class RequestData:
    to: str
    subject: str
    confirm_url: str
    html_template: str = "emails/email_confirm.html"
    txt_template: str = "emails/email_confirm.txt"


class ApiHandler:
    def register(self, app: web.Application) -> None:
        app.add_routes(
            [
                web.get("/", self.handle_index, name="index"),
                web.post("/register", self.handle_register),
                web.get("/success", self.handle_success),
            ]
        )

    @aiohttp_jinja2.template("index.html")
    async def handle_index(self, request):
        pass

    async def handle_register(self, request):
        params = await request.post()
        to = params.get("to_email")
        if not to:
            raise web.HTTPBadRequest(text="Missing parameter 'to_email'")
        subject = params.get("subject", "Email confirmation")
        confirm_url = (
            f"https://fakeemailconfirm.appspot.com/email-confirm/{uuid4().hex[:20]}/"
        )

        data = RequestData(to, subject, confirm_url)
        logger.info(f"Request received: {data}")
        return web.HTTPFound("/success")

    @aiohttp_jinja2.template("success.html")
    async def handle_success(self, request):
        pass


async def create_app() -> web.Application:
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES_DIR))
    db = await create_connection(user=DB_USERNAME, password=DB_PASSWORD)
    app['db'] = db
    api_handler = ApiHandler()
    api_handler.register(app)
    return app


if __name__ == "__main__":
    host, port = "0.0.0.0", 8080
    logging.info(f"Starting the app on {host}:{port}")
    web.run_app(create_app(), host=host, port=port)
