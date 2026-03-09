from flask import Blueprint, Response, current_app, request

wechat_bp = Blueprint("wechat", __name__)


@wechat_bp.route("/", methods=["GET", "POST"])
def wechat():
    # 从应用上下文中获取服务
    message_service = current_app.message_service

    if request.method == "GET":
        # 微信验证接口
        signature = request.args.get("signature", "")
        timestamp = request.args.get("timestamp", "")
        nonce = request.args.get("nonce", "")
        echostr = request.args.get("echostr", "")

        if message_service.verify_wechat_signature(signature, timestamp, nonce):
            return echostr
        else:
            return "验证失败", 400
    else:
        # 微信消息处理接口
        xml_data = request.data.decode("utf-8")
        response_xml = message_service.handle_wechat_message(xml_data)
        return Response(response_xml, mimetype="application/xml")
