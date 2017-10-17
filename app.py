# -*- coding: utf-8 -*-
import sys
sys.path.append('./vendor')

import os
import uuid

from PIL import Image
import io

from flask import Flask, request, abort, send_file

from linebot import (
    LineBotApi, WebhookHandler,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage
)

import cloudinary
import cloudinary.uploader

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):
    if event.type == "message":
        if event.message.type == "image":
            message_content = line_bot_api.get_message_content(event.message.id)

            dirname = 'tmp'
            fileName = uuid.uuid4().hex
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open("tmp/{fileName}.jpg", 'wb') as img:
                img.write(message_content.content)

            cloudinary.config(
                cloud_name = os.environ.get('CLOUDINARY_NAME'),
                api_key = os.environ.get('CLOUDINARY_KEY'),
                api_secret = os.environ.get('CLOUDINARY_SECRET')
            )
            result = cloudinary.uploader.upload("tmp/{fileName}.jpg")
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=result['secure_url'])
                ]
            )

if __name__ == "__main__":
    app.debug = True
    app.run()
