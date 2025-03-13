import json
import uuid
import lark_oapi as lark
from lark_oapi.api.im.v1 import *


YOUR_APP_ID = "cli_a74420afa11fd00b"
YOUR_APP_SECRET = "yXbInsBL1hiJU9Yhxhstlcs3XDQ2gQgm"

client = lark.Client.builder() \
        .app_id(YOUR_APP_ID) \
        .app_secret(YOUR_APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

def feishu_send_msg(message, user_id="3df96g5b"):
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("user_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(user_id)
            .msg_type("text")
            .content(f"""
            {{"text": "{message}"}}
            """)
            .uuid(str(uuid.uuid4()))
            .build()) \
        .build()

    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    feishu_send_msg("hello")