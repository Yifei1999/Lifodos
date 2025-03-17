import lark_oapi as lark
import requests
import json
import httpx

YOUR_APP_ID = "cli_a74420afa11fd00b"
YOUR_APP_SECRET = "yXbInsBL1hiJU9Yhxhstlcs3XDQ2gQgm"

## P2ImMessageReceiveV1 为接收消息 v2.0；CustomizedEvent 内的 message 为接收消息 v1.0
# https://open.feishu.cn/document/server-docs/im-v1/message/events/receive。
def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')
    js = json.loads(lark.JSON.marshal(data, indent=4))
    open_id = js["event"]["sender"]["sender_id"]["open_id"]
    message = js["event"]["message"]
    response = requests.post(
        "http://localhost:80/feishu/send-msg",
        json={"open_id": open_id, "message": message}
    )
    return

def do_message_event(data: lark.CustomizedEvent) -> None:
    print(f'[ do_customized_event access ], type: message, data: {lark.JSON.marshal(data, indent=4)}')


event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("im.message.receive_v1", do_message_event) \
    .build()

def event_local_server():
    cli = lark.ws.Client(YOUR_APP_ID, YOUR_APP_SECRET,
                         event_handler=event_handler,
                         log_level=lark.LogLevel.DEBUG)
    cli.start()


if __name__ == "__main__":
    event_local_server()
