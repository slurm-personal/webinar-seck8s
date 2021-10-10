import logging
import os
from dataclasses import dataclass
from uuid import uuid4

import aiohttp.web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RequestData:
    to: str
    subject: str
    confirm_url: str
    html_template: str = "emails/email_confirm.html"
    txt_template: str = "emails/email_confirm.txt"


class ApiHandler:
    def register(self, app: aiohttp.web.Application) -> None:
        app.add_routes(
            [
                aiohttp.web.get("/ping", self.handle_ping),
                aiohttp.web.post("/send-email", self.handle_send_email),
            ]
        )

    async def handle_ping(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        return aiohttp.web.Response(text="Pong")

    async def handle_send_email(
        self, request: aiohttp.web.Request
    ) -> aiohttp.web.Response:
        params = await request.post()
        to = params.get("to_email")
        if not to:
            raise aiohttp.web.HTTPBadRequest(text="Missing parameter 'to_email'")
        subject = params.get("subject", "Email confirmation")
        confirm_url = (
            f"https://fakeemailconfirm.appspot.com/email-confirm/{uuid4().hex[:20]}/"
        )

        data = RequestData(to, subject, confirm_url)
        logger.info(f"Request received: {data}")

        return aiohttp.web.Response(status=200)


async def create_app() -> aiohttp.web.Application:
    app = aiohttp.web.Application()
    api_handler = ApiHandler()
    api_handler.register(app)
    return app


if __name__ == "__main__":
    host, port = "0.0.0.0", 8080
    logging.info(f"Starting the app on {host}:{port}")
    aiohttp.web.run_app(create_app(), host=host, port=port)
