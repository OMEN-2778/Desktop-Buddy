"""Send only an explicitly prepared completion notice to the player's mailbox."""
import json
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def main():
    ready = json.loads(Path('.github/notify-ready.json').read_text(encoding='utf-8'))
    commit = ready.get('commit', '')
    if ready.get('status') != 'complete' or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise SystemExit('完成标记无效，邮件未发送。')
    code = os.environ.get('QQ_SMTP_AUTH_CODE', '').strip()
    if not code:
        raise SystemExit('QQ_SMTP_AUTH_CODE 未配置，邮件未发送。')
    mailbox = '2694743660@qq.com'
    message = EmailMessage()
    message['From'] = mailbox
    message['To'] = mailbox
    message['Subject'] = 'Desktop Buddy 更新已完成，可以测试啦'
    message.set_content(
        '这轮 Desktop Buddy 更新已完成，并已通过网页版验证。\n\n'
        + str(ready.get('summary', '朋友同行、双人座位及对白更新已完成。'))
        + '\n\n打开游戏：\nhttps://omen-2778.github.io/Desktop-Buddy/?v='
        + commit[:12]
        + '\n\n对应提交：\nhttps://github.com/OMEN-2778/Desktop-Buddy/commit/'
        + commit
        + '\n\n入口：人脉 → 选择好友 → 出门玩。\n',
        charset='utf-8',
    )
    with smtplib.SMTP_SSL('smtp.qq.com', 465, context=ssl.create_default_context(), timeout=30) as smtp:
        smtp.login(mailbox, code)
        smtp.send_message(message)
    print('完成通知已提交给 QQ 邮箱服务器。')


if __name__ == '__main__':
    main()
