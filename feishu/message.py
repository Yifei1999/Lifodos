import json

import lark_oapi as lark
from lark_oapi.api.im.v1 import *


YOUR_APP_ID = "cli_a74420afa11fd00b"
YOUR_APP_SECRET = "yXbInsBL1hiJU9Yhxhstlcs3XDQ2gQgm"

# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development

def main():
    # 创建client
    client = lark.Client.builder() \
        .app_id(YOUR_APP_ID) \
        .app_secret(YOUR_APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 构造请求对象
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("user_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id("3df96g5b")
            .msg_type("text")
            .content("{\"text\":\"hello world\"}")
            .uuid("a0d69e20-1dd1-458b-k525-dfeca2015204")
            .build()) \
        .build()

    # 发起请求
    response: CreateMessageResponse = client.im.v1.message.create(request)

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


if __name__ == "__main__":
    main()