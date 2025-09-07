import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '..'))
if root not in sys.path:
    sys.path.append(root)

from adapters.akshare_provider import AkshareFundProvider
from engines.backtrader_engine import BacktraderEngine
from strategies.strategy import Strategy_MACD3
from utils.emailer import SmtpEmailer


def main() -> None:
    # 配置 SMTP 环境变量或在 SmtpEmailer(...) 里传参
    # os.environ['SMTP_HOST'] = 'smtp.example.com'
    # os.environ['SMTP_PORT'] = '587'
    # os.environ['SMTP_USER'] = 'user@example.com'
    # os.environ['SMTP_PASS'] = 'password'
    # os.environ['SMTP_FROM'] = 'user@example.com'
    # os.environ['SMTP_TO'] = 'notify_to@example.com'

    emailer = SmtpEmailer(
        smtp_host='smtp.163.com',
        smtp_port=465,
        username='tobeprozy@163.com',
        password='BHrMkpZZvm8frpWY',
        from_addr='tobeprozy@163.com',
        to_addrs='904762096@qq.com'
    )

    engine = BacktraderEngine(
        data_provider=AkshareFundProvider(),
        symbol='512200',
        start_date='20220101',
        end_date='20240101',
        strategy_cls=Strategy_MACD3,
        email_on_finish=True,
        emailer=emailer,
    )

    # 运行回测
    res = engine.run()
    # 结束后邮件会自动发送（若配置完成）
    engine.print_results(res)


if __name__ == '__main__':
    main()


