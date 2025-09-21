

import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from qbackengine.emailer import SmtpEmailer
import datetime


def main() -> None:

    emailer = SmtpEmailer(
        smtp_host='smtp.163.com',
        smtp_port=465,
        username='tobeprozy@163.com',
        password='BHrMkpZZvm8frpWY',
        from_addr='tobeprozy@163.com',
        to_addrs='904762096@qq.com'
    )

    print(emailer)
    time=datetime.datetime.now()
    try:
        emailer.send(
            subject=f"this is a test email",
            body=f"hello world!!!",
        )
    except Exception:
        print(f"Email sent failed")
    pass


if __name__ == '__main__':
    main()


