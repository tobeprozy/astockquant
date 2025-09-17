
import numpy as np
import pandas as pd
import talib

class StockTAIndicatorsCalculator:
    # https://github.com/HuaRongSAO/talib-document?tab=readme-ov-file
    def __init__(self, df):
        """
        初始化StockTAIndicatorsCalculator类。
        
        参数:
        df -- 包含股票数据的pandas.DataFrame对象，必须包含'High', 'Low', 'Close', 'Volume'列。
        """
        self.df = df.copy()
        self.df = self.df.reset_index()

    def calculate_all_indicators(self):
        """
        计算所有技术指标。
        """
        self.calculate_ma(5)
        self.calculate_ema(5)
        self.calculate_rsi(14)
        self.calculate_bbands(5, 2, 2)
        self.calculate_macd(12, 26, 9)

    def calculate_ma(self, timeperiod=5):
        """
        计算移动平均线（MA）。
        
        参数:
        timeperiod -- MA的周期，默认为5。
        """
        self.df['MA{}'.format(timeperiod)] = talib.MA(self.df['close'], timeperiod=timeperiod)

    def calculate_ema(self, timeperiod=5):
        """
        计算指数移动平均线（EMA）。
        
        参数:
        timeperiod -- EMA的周期，默认为5。
        """
        self.df['EMA{}'.format(timeperiod)] = talib.EMA(self.df['close'], timeperiod=timeperiod)

    def calculate_rsi(self, timeperiod=14):
        """
        计算相对强弱指数（RSI）。
        
        参数:
        timeperiod -- RSI的周期，默认为14。
        """
        self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=timeperiod)

    def calculate_bbands(self, timeperiod=5, nbdevup=2, nbdevdn=2):
        """
        计算布林带（Bollinger Bands）。
        
        参数:
        timeperiod -- 布林带的周期，默认为5。
        nbdevup -- 上轨偏差，默认为2。
        nbdevdn -- 下轨偏差，默认为2。
        """
        self.df['BB_UPPER'], self.df['BB_MIDDLE'], self.df['BB_LOWER'] = talib.BBANDS(self.df['close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)

    def calculate_macd(self, fastperiod=12, slowperiod=26, signalperiod=9):
        """
        计算MACD。
        
        参数:
        fastperiod -- MACD的快速EMA周期，默认为12。
        slowperiod -- MACD的慢速EMA周期，默认为26。
        signalperiod -- MACD信号线的周期，默认为9。
        """
        macd, macd_signal, macd_hist = talib.MACD(self.df['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        self.df['MACD'] = macd
        self.df['MACD_SIGNAL'] = macd_signal
        self.df['MACD_HIST'] = macd_hist

    def get_data(self):
        """
        返回计算结果的DataFrame。
        """
        return self.df
    
    # 重叠指标
    def cal_bbands(self, timeperiod=5, nbdevup=2, nbdevdn=2):
        """
        计算布林带（Bollinger Bands）。
        名称： 布林线指标
        简介：其利用统计原理，求出股价的标准差及其信赖区间，从而确定股价的波动范围及未来走势，利用波带显示股价的安全高低价位，因而也被称为布林带。
        参数:
        timeperiod -- 布林带的周期，默认为5。
        nbdevup -- 上轨偏差，默认为2。
        nbdevdn -- 下轨偏差，默认为2。
        """
        self.df['BB_UPPER'], self.df['BB_MIDDLE'], self.df['BB_LOWER'] = talib.BBANDS(self.df['close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
    
    def cal_dema(self, timeperiod=30):
        """
        计算双指数移动平均线（DEMA）。
        名称： 双移动平均线
        简介：两条移动平均线来产生趋势信号，较长期者用来识别趋势，较短期者用来选择时机。正是两条平均线及价格三者的相互作用，才共同产生了趋势信号。

        参数:
        timeperiod -- DEMA的周期，默认为30。
        """
        self.df['DEMA{}'.format(timeperiod)] = talib.DEMA(self.df['close'], timeperiod=timeperiod)

    def cal_ema(self, timeperiod=30):
        """
        计算指数移动平均线（EMA）。
        名称： 指数平均数
        简介：是一种趋向类指标，其构造原理是仍然对价格收盘价进行算术平均，并根据计算结果来进行分析，用于判断价格未来走势的变动趋势。

        参数:
        timeperiod -- EMA的周期，默认为30。
        """
        self.df['EMA{}'.format(timeperiod)] = talib.EMA(self.df['close'], timeperiod=timeperiod)

    def cal_ht_trendline(self):
        """
        计算HT_TRENDLINE。
        名称： 希尔伯特瞬时变换
        简介：是一种趋向类指标，其构造原理是仍然对价格收盘价进行算术平均，并根据计算结果来进行分析，用于判断价格未来走势的变动趋势。
        """
        self.df['HT_TRENDLINE'] = talib.HT_TRENDLINE(self.df['close'])

    def cal_kama(self, timeperiod=30):
        """
        计算KAMA。
        名称： 考夫曼的自适应移动平均线
        简介：短期均线贴近价格走势，灵敏度高，但会有很多噪声，产生虚假信号；长期均线在判断趋势上一般比较准确 ，但是长期均线有着严重滞后的问题。我们想得到这样的均线，当价格沿一个方向快速移动时，短期的移动 平均线是最合适的；当价格在横盘的过程中，长期移动平均线是合适的。

        参数:
        timeperiod -- KAMA的周期，默认为30。
        """
        self.df['KAMA'] = talib.KAMA(self.df['close'], timeperiod=timeperiod)

    def cal_ma(self, timeperiod=30):
        """
        计算移动平均线（MA）。
        名称： 简单移动平均线
        简介：移动平均线，Moving Average，简称MA，原本的意思是移动平均，由于我们将其制作成线形，所以一般称之为移动平均线，简称均线。它是将某一段时间的收盘价之和除以该周期。 比如日线MA5指5天内的收盘价除以5 。

        参数:
        timeperiod -- MA的周期，默认为30。
        """
        self.df['MA{}'.format(timeperiod)] = talib.MA(self.df['close'], timeperiod=timeperiod,matype=0)

    def cal_mama(self, fastlimit=0, slowlimit=0):
        """
        计算MAMA。
        名称： 对称指数移动平均线
        简介：对称指数移动平均线，MAMA，是一种趋势跟踪指标，它结合了指数移动平均线和对称移动平均线，以提供更准确的趋势跟踪。

        参数:
        fastlimit -- 快速限制，默认为0.5。
        slowlimit -- 慢速限制，默认为0.05。
        """
        self.df['MAMA'], self.df['FAMA'] = talib.MAMA(self.df['close'], fastlimit=fastlimit, slowlimit=slowlimit)

    def cal_mavp(self, periods, minperiod=2, maxperiod=30, matype=0):
        """
        计算移动平均线变量周期（MAVP）。
        名称： 移动平均线变量周期
        简介：根据给定的周期范围计算移动平均线。

        参数:
        periods -- 计算平均数的序列。
        minperiod -- 最小周期，默认为2。
        maxperiod -- 最大周期，默认为30。
        matype -- 计算平均线方法，默认为0。
        """
        self.df['MAVP'] = talib.MAVP(self.df['close'], periods, minperiod, maxperiod, matype)

    def cal_midpoint(self, timeperiod=14):
        """
        计算周期中点（MIDPOINT）。
        名称： 周期中点
        简介：计算给定周期的中点价格。

        参数:
        timeperiod -- 周期，默认为14。
        """
        self.df['MIDPOINT'] = talib.MIDPOINT(self.df['close'], timeperiod=timeperiod)

    def cal_midprice(self, timeperiod=14):
        """
        计算周期中点价格（MIDPRICE）。
        名称： 周期中点价格
        简介：计算给定周期的最高价和最低价的中点价格。

        参数:
        timeperiod -- 周期，默认为14。
        """
        self.df['MIDPRICE'] = talib.MIDPRICE(self.df['high'], self.df['low'], timeperiod=timeperiod)

    def cal_sar(self, acceleration=0, maximum=0):
        """
        计算抛物线指标（SAR）。
        名称： 抛物线指标
        简介：抛物线转向也称停损点转向，是利用抛物线方式，随时调整停损点位置以观察买卖点。由于停损点（又称转向点SAR）以弧形的方式移动，故称之为抛物线转向指标。

        参数:
        acceleration -- 加速因子，默认为0。
        maximum -- 极点价，默认为0。
        """
        self.df['SAR'] = talib.SAR(self.df['high'], self.df['low'], acceleration=acceleration, maximum=maximum)

    def cal_sarext(self, startvalue=0, offsetonreverse=0, accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0):
        """
        计算抛物线指标扩展（SAREXT）。
        名称： 抛物线指标扩展
        简介：扩展的抛物线转向指标。

        参数:
        startvalue -- 起始值，默认为0。
        offsetonreverse -- 反转偏移，默认为0。
        accelerationinitlong -- 初始长加速因子，默认为0。
        accelerationlong -- 长加速因子，默认为0。
        accelerationmaxlong -- 最大长加速因子，默认为0。
        accelerationinitshort -- 初始短加速因子，默认为0。
        accelerationshort -- 短加速因子，默认为0。
        accelerationmaxshort -- 最大短加速因子，默认为0。
        """
        self.df['SAREXT'] = talib.SAREXT(self.df['high'], self.df['low'], startvalue=startvalue, offsetonreverse=offsetonreverse, accelerationinitlong=accelerationinitlong, accelerationlong=accelerationlong, accelerationmaxlong=accelerationmaxlong, accelerationinitshort=accelerationinitshort, accelerationshort=accelerationshort, accelerationmaxshort=accelerationmaxshort)

    def cal_sma(self, timeperiod=30):
        """
        计算简单移动平均线（SMA）。
        名称： 简单移动平均线
        简介：移动平均线，Moving Average，简称MA，原本的意思是移动平均，由于我们将其制作成线形，所以一般称之为移动平均线，简称均线。它是将某一段时间的收盘价之和除以该周期。比如日线MA5指5天内的收盘价除以5。

        参数:
        timeperiod -- SMA的周期，默认为30。
        """
        self.df['SMA{}'.format(timeperiod)] = talib.SMA(self.df['close'], timeperiod=timeperiod)

    def cal_t3(self, timeperiod=5, vfactor=0):
        """
        计算三重指数移动平均线（T3）。
        名称： 三重指数移动平均线
        简介：TRIX长线操作时采用本指标的讯号，长时间按照本指标讯号交易，获利百分比大于损失百分比，利润相当可观。

        参数:
        timeperiod -- T3的周期，默认为5。
        vfactor -- 变异因子，默认为0。
        """
        self.df['T3'] = talib.T3(self.df['close'], timeperiod=timeperiod, vfactor=vfactor)

    def cal_tema(self, timeperiod=30):
        """
        计算三重指数移动平均线（TEMA）。
        名称： 三重指数移动平均线
        简介：TEMA是一种趋势跟踪指标。

        参数:
        timeperiod -- TEMA的周期，默认为30。
        """
        self.df['TEMA'] = talib.TEMA(self.df['close'], timeperiod=timeperiod)

    def cal_trima(self, timeperiod=30):
        """
        计算三角移动平均线（TRIMA）。
        名称： 三角移动平均线
        简介：TRIMA是一种趋势跟踪指标。

        参数:
        timeperiod -- TRIMA的周期，默认为30。
        """
        self.df['TRIMA'] = talib.TRIMA(self.df['close'], timeperiod=timeperiod)

    def cal_wma(self, timeperiod=30):
        """
        计算加权移动平均线（WMA）。
        名称： 加权移动平均线
        简介：移动加权平均法是指以每次进货的成本加上原有库存存货的成本，除以每次进货数量与原有库存存货的数量之和，据以计算加权平均单位成本，以此为基础计算当月发出存货的成本和期末存货的成本的一种方法。

        参数:
        timeperiod -- WMA的周期，默认为30。
        """
        self.df['WMA'] = talib.WMA(self.df['close'], timeperiod=timeperiod)

    # 动量指标
    def cal_adx(self, timeperiod=14):
            """
            计算平均趋向指数（ADX）。
            名称： 平均趋向指数
            简介：使用ADX指标，指标判断盘整、振荡和单边趋势。

            参数:
            timeperiod -- 计算周期，默认为14。
            """
            self.df['ADX'] = talib.ADX(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_adxr(self, timeperiod=14):
        """
        计算平均趋向指数的趋向指数（ADXR）。
        名称： 平均趋向指数的趋向指数
        简介：使用ADXR指标，指标判断ADX趋势。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['ADXR'] = talib.ADXR(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_apo(self, fastperiod=12, slowperiod=26, matype=0):
        """
        计算绝对价格振荡器（APO）。
        名称： 绝对价格振荡器
        简介：APO是收盘价的两个不同周期EMA之间的差值。

        参数:
        fastperiod -- 快速EMA周期，默认为12。
        slowperiod -- 慢速EMA周期，默认为26。
        matype -- 计算平均线方法，默认为0。
        """
        self.df['APO'] = talib.APO(self.df['close'], fastperiod=fastperiod, slowperiod=slowperiod, matype=matype)

    def cal_aroon(self, timeperiod=14):
        """
        计算阿隆指标（AROON）。
        名称： 阿隆指标
        简介：该指标是通过计算自价格达到近期最高值和最低值以来所经过的期间数，阿隆指标帮助你预测价格趋势到趋势区域（或者反过来，从趋势区域到趋势）的变化。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        aroondown, aroonup = talib.AROON(self.df['high'], self.df['low'], timeperiod=timeperiod)
        self.df['AROON_DOWN'] = aroondown
        self.df['AROON_UP'] = aroonup

    def cal_aroonosc(self, timeperiod=14):
        """
        计算阿隆振荡（AROONOSC）。
        名称： 阿隆振荡
        简介：阿隆振荡是阿隆指标的变体，计算阿隆上升和下降之间的差值。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['AROONOSC'] = talib.AROONOSC(self.df['high'], self.df['low'], timeperiod=timeperiod)
    
    def cal_bop(self):
        """
        计算均势指标（BOP）。
        名称： 均势指标
        简介：均势指标是通过比较开盘价和收盘价与最高价、最低价的关系，来观察多空双方力量的对比。

        参数:
        无
        """
        self.df['BOP'] = talib.BOP(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cci(self, timeperiod=14):
        """
        计算顺势指标（CCI）。
        名称： 顺势指标
        简介：CCI指标专门测量股价是否已超出常态分布范围。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['CCI'] = talib.CCI(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_cmo(self, timeperiod=14):
        """
        计算钱德动量摆动指标（CMO）。
        名称： 钱德动量摆动指标
        简介：与其他动量指标摆动指标如相对强弱指标（RSI）和随机指标（KDJ）不同，钱德动量指标在计算公式的分子中采用上涨日和下跌日的数据。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['CMO'] = talib.CMO(self.df['close'], timeperiod=timeperiod)

    def cal_dx(self, timeperiod=14):
        """
        计算动向指标或趋向指标（DX）。
        名称： 动向指标或趋向指标
        简介：通过分析股票价格在涨跌过程中买卖双方力量均衡点的变化情况，即多空双方的力量的变化受价格波动的影响而发生由均衡到失衡的循环过程，从而提供对趋势判断依据的一种技术指标。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['DX'] = talib.DX(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_macd(self, fastperiod=12, slowperiod=26, signalperiod=9):
        """
        计算平滑异同移动平均线（MACD）。
        名称： 平滑异同移动平均线
        简介：利用收盘价的短期（常用为12日）指数移动平均线与长期（常用为26日）指数移动平均线之间的聚合与分离状况，对买进、卖出时机作出研判的技术指标。

        参数:
        fastperiod -- 快速EMA周期，默认为12。
        slowperiod -- 慢速EMA周期，默认为26。
        signalperiod -- 信号线周期，默认为9。
        """
        # Talib.MACD返回三个值，分别是macd, signal, hist，三个返回值分别对应上面的计算指标DIF、DEA、BAR。即macd=DIF，signal=DEA，hist=BAR。
        macd, macd_signal, macd_hist = talib.MACD(self.df['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        self.df['MACD'] = macd
        self.df['MACD_SIGNAL'] = macd_signal
        self.df['MACD_HIST'] = macd_hist

    def cal_macdext(self, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0):
        """
        计算平滑异同移动平均线（可控制移动平均算法）（MACDEXT）。
        名称： 平滑异同移动平均线（可控制移动平均算法）
        简介：同MACD函数，并提供参数控制计算DIF, DEM时使用的移动平均算法。

        参数:
        fastperiod -- 快速周期，默认为12。
        fastmatype -- 快速MA类型，默认为0。
        slowperiod -- 慢速周期，默认为26。
        slowmatype -- 慢速MA类型，默认为0。
        signalperiod -- 信号线周期，默认为9。
        signalmatype -- 信号线MA类型，默认为0。
        """
        macd, macd_signal, macd_hist = talib.MACDEXT(self.df['close'], fastperiod=fastperiod, fastmatype=fastmatype, slowperiod=slowperiod, slowmatype=slowmatype, signalperiod=signalperiod, signalmatype=signalmatype)
        self.df['MACD_EXT'] = macd
        self.df['MACD_EXT_SIGNAL'] = macd_signal
        self.df['MACD_EXT_HIST'] = macd_hist

    def cal_macdfix(self, signalperiod=9):
        """
        计算平滑异同移动平均线（固定快慢均线周期为12/26）（MACDFIX）。
        名称： 平滑异同移动平均线（固定快慢均线周期为12/26）
        简介：同MACD函数，固定快均线周期fastperiod=12, 慢均线周期slowperiod=26。

        参数:
        signalperiod -- 信号线周期，默认为9。
        """
        macd, macd_signal, macd_hist = talib.MACDFIX(self.df['close'], signalperiod=signalperiod)
        self.df['MACD_FIX'] = macd
        self.df['MACD_FIX_SIGNAL'] = macd_signal
        self.df['MACD_FIX_HIST'] = macd_hist

    def cal_mfi(self, timeperiod=14):
        """
        计算资金流量指标（MFI）。
        名称： 资金流量指标
        简介：属于量价类指标，反映市场的运行趋势。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['MFI'] = talib.MFI(self.df['high'], self.df['low'], self.df['close'], self.df['vol'], timeperiod=timeperiod)

    def cal_minus_di(self, timeperiod=14):
        """
        计算负方向指标（MINUS_DI）。
        名称： 下升动向值
        简介：通过分析股票价格在涨跌过程中买卖双方力量均衡点的变化情况，即多空双方的力量的变化受价格波动的影响而发生由均衡到失衡的循环过程，从而提供对趋势判断依据的一种技术指标。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['MINUS_DI'] = talib.MINUS_DI(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_minus_dm(self, timeperiod=14):
        """
        计算上升动向值（MINUS_DM）。
        名称： 上升动向值
        简介：通过分析股票价格在涨跌过程中买卖双方力量均衡点的变化情况，即多空双方的力量的变化受价格波动的影响而发生由均衡到失衡的循环过程，从而提供对趋势判断依据的一种技术指标。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['MINUS_DM'] = talib.MINUS_DM(self.df['high'], self.df['low'], timeperiod=timeperiod)

    def cal_mom(self, timeperiod=10):
        """
        计算动量（MOM）。
        名称： 上升动向值
        简介：投资学中意思为续航，指股票(或经济指数)持续增长的能力。

        参数:
        timeperiod -- 计算周期，默认为10。
        """
        self.df['MOM'] = talib.MOM(self.df['close'], timeperiod=timeperiod)

    def cal_plus_di(self, timeperiod=14):
        """
        计算正方向指标（PLUS_DI）。
        名称： 正方向指标
        简介：是趋向指标（DMI）中的一个组成部分，用于衡量市场趋势。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['PLUS_DI'] = talib.PLUS_DI(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_plus_dm(self, timeperiod=14):
        """
        计算正方向运动（PLUS_DM）。
        名称： 正方向运动
        简介：是趋向指标（DMI）中的一个组成部分，用于衡量市场趋势。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['PLUS_DM'] = talib.PLUS_DM(self.df['high'], self.df['low'], timeperiod=timeperiod)

    def cal_ppo(self, fastperiod=12, slowperiod=26, matype=0):
        """
        计算价格震荡百分比指数（PPO）。
        名称： 价格震荡百分比指数
        简介：价格震荡百分比指标（PPO）是一个和MACD指标非常接近的指标。

        参数:
        fastperiod -- 快速周期，默认为12。
        slowperiod -- 慢速周期，默认为26。
        matype -- 计算平均线方法，默认为0。
        """
        self.df['PPO'] = talib.PPO(self.df['close'], fastperiod=fastperiod, slowperiod=slowperiod, matype=matype)

    def cal_roc(self, timeperiod=10):
        """
        计算变动率指标（ROC）。
        名称： 变动率指标
        简介：ROC是由当天的股价与一定的天数之前的某一天股价比较，其变动速度的大小,来反映股票市变动的快慢程度。

        参数:
        timeperiod -- 计算周期，默认为10。
        """
        self.df['ROC'] = talib.ROC(self.df['close'], timeperiod=timeperiod)

    def cal_rocp(self, timeperiod=10):
        """
        计算变动率百分比指标（ROCP）。
        名称： 变动率百分比指标
        简介：(price-prevPrice)/prevPrice。

        参数:
        timeperiod -- 计算周期，默认为10。
        """
        self.df['ROCP'] = talib.ROCP(self.df['close'], timeperiod=timeperiod)

    def cal_rocr(self, timeperiod=10):
        """
        计算变动率比率指标（ROCR）。
        名称： 变动率比率指标
        简介：(price/prevPrice)。

        参数:
        timeperiod -- 计算周期，默认为10。
        """
        self.df['ROCR'] = talib.ROCR(self.df['close'], timeperiod=timeperiod)

    def cal_rocr100(self, timeperiod=10):
        """
        计算变动率比率指标100刻度（ROCR100）。
        名称： 变动率比率指标100刻度
        简介：(price/prevPrice)*100。

        参数:
        timeperiod -- 计算周期，默认为10。
        """
        self.df['ROCR100'] = talib.ROCR100(self.df['close'], timeperiod=timeperiod)

    def cal_rsi(self, timeperiod=14):
        """
        计算相对强弱指数（RSI）。
        名称： 相对强弱指数
        简介：是通过比较一段时期内的平均收盘涨数和平均收盘跌数来分析市场买沽盘的意向和实力。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['RSI'] = talib.RSI(self.df['close'], timeperiod=timeperiod)

    def cal_stoch(self, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
        """
        计算随机指标（STOCH）。
        名称： 随机指标,俗称KD

        参数:
        fastk_period -- 快速K周期，默认为5。
        slowk_period -- 慢速K周期，默认为3。
        slowk_matype -- 慢速KMA类型，默认为0。
        slowd_period -- 慢速D周期，默认为3。
        slowd_matype -- 慢速DMA类型，默认为0。
        """
        slowk, slowd = talib.STOCH(self.df['high'], self.df['low'], self.df['close'], fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=slowk_matype, slowd_period=slowd_period, slowd_matype=slowd_matype)
        self.df['STOCH_SLOWK'] = slowk
        self.df['STOCH_SLOWD'] = slowd

    def cal_stochf(self, fastk_period=5, fastd_period=3, fastd_matype=0):
        """
        计算快速随机指标（STOCHF）。
        名称： 快速随机指标

        参数:
        fastk_period -- 快速K周期，默认为5。
        fastd_period -- 快速D周期，默认为3。
        fastd_matype -- 快速DMA类型，默认为0。
        """
        fastk, fastd = talib.STOCHF(self.df['high'], self.df['low'], self.df['close'], fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=fastd_matype)
        self.df['STOCHF_FASTK'] = fastk
        self.df['STOCHF_FASTD'] = fastd

    def cal_stochrsi(self, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0):
        """
        计算随机相对强弱指数（STOCHRSI）。
        名称： 随机相对强弱指数

        参数:
        timeperiod -- 计算周期，默认为14。
        fastk_period -- 快速K周期，默认为5。
        fastd_period -- 快速D周期，默认为3。
        fastd_matype -- 快速DMA类型，默认为0。
        """
        self.df['STOCHRSI'] = talib.STOCHRSI(self.df['close'], timeperiod=timeperiod, fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=fastd_matype)

    def cal_trix(self, timeperiod=30):
        """
        计算1日变动率（ROC）的三重平滑指数移动平均（TRIX）。
        名称： 1日变动率（ROC）的三重平滑指数移动平均

        参数:
        timeperiod -- 计算周期，默认为30。
        """
        self.df['TRIX'] = talib.TRIX(self.df['close'], timeperiod=timeperiod)

    def cal_ultosc(self, timeperiod1=7, timeperiod2=14, timeperiod3=28):
        """
        计算终极波动指标（ULTOSC）。
        名称： 终极波动指标
        简介：UOS是一种多方位功能的指标，除了趋势确认及超买超卖方面的作用之外，它的“突破”讯号不仅可以提供最适当的交易时机之外，更可以进一步加强指标的可靠度。

        参数:
        timeperiod1 -- 第一周期，默认为7。
        timeperiod2 -- 第二周期，默认为14。
        timeperiod3 -- 第三周期，默认为28。
        """
        self.df['ULTOSC'] = talib.ULTOSC(self.df['high'], self.df['low'], self.df['close'], timeperiod1=timeperiod1, timeperiod2=timeperiod2, timeperiod3=timeperiod3)

    def cal_willr(self, timeperiod=14):
        """
        计算威廉指标（WILLR）。
        名称： 威廉指标
        简介：WMS表示的是市场处于超买还是超卖状态。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['WILLR'] = talib.WILLR(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    # 成交量指标
    def cal_ad(self):
        """
        计算Chaikin A/D Line（AD）。
        名称：Chaikin A/D Line 累积/派发线（Accumulation/Distribution Line）
        简介：Marc Chaikin提出的一种平衡交易量指标，以当日的收盘价位来估算成交流量，用于估定一段时间内该证券累积的资金流量。

        参数:
        无
        """
        self.df['AD'] = talib.AD(self.df['high'], self.df['low'], self.df['close'], self.df['vol'])

    def cal_adosc(self, fastperiod=3, slowperiod=10):
        """
        计算Chaikin A/D Oscillator（ADOSC）。
        名称：Chaikin A/D Oscillator Chaikin震荡指标
        简介：将资金流动情况与价格行为相对比，检测市场中资金流入和流出的情况。

        参数:
        fastperiod -- 快速周期，默认为3。
        slowperiod -- 慢速周期，默认为10。
        """
        self.df['ADOSC'] = talib.ADOSC(self.df['high'], self.df['low'], self.df['close'], self.df['vol'], fastperiod=fastperiod, slowperiod=slowperiod)

    def cal_obv(self):
        """
        计算On Balance Volume（OBV）。
        名称：On Balance Volume 能量潮
        简介：Joe Granville提出，通过统计成交量变动的趋势推测股价趋势。

        参数:
        无
        """
        self.df['OBV'] = talib.OBV(self.df['close'], self.df['vol'])

    # 波动率指标
    def cal_atr(self, timeperiod=14):
        """
        计算真实波动幅度均值（ATR）。
        名称：真实波动幅度均值
        简介：真实波动幅度均值（ATR)是以N天的指数移动平均数平均后的交易波动幅度。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['ATR'] = talib.ATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_natr(self, timeperiod=14):
        """
        计算归一化波动幅度均值（NATR）。
        名称：归一化波动幅度均值
        简介：归一化波动幅度均值（NATR）是真实波动幅度均值（ATR）除以当前周期的收盘价的百分比表达形式。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['NATR'] = talib.NATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)

    def cal_trange(self):
        """
        计算真正的范围（TRANGE）。
        名称：真正的范围
        简介：真实的价格范围，考虑了昨天的收盘价。

        参数:
        无
        """
        self.df['TRANGE'] = talib.TRANGE(self.df['high'], self.df['low'], self.df['close'])

    # 价格指标
    def cal_avgprice(self):
        """
        计算平均价格函数（AVGPRICE）。
        名称：平均价格函数
        简介：计算给定周期内的平均价格，是开盘价、最高价、最低价和收盘价的平均值。

        参数:
        无
        """
        self.df['AVGPRICE'] = talib.AVGPRICE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_medprice(self):
        """
        计算中位数价格（MEDPRICE）。
        名称：中位数价格
        简介：计算最高价和最低价的平均值，用于衡量中间价。

        参数:
        无
        """
        self.df['MEDPRICE'] = talib.MEDPRICE(self.df['high'], self.df['low'])

    def cal_typprice(self):
        """
        计算代表性价格（TYPPRICE）。
        名称：代表性价格
        简介：计算最高价、最低价和收盘价的平均值，常用于技术分析。

        参数:
        无
        """
        self.df['TYPPRICE'] = talib.TYPPRICE(self.df['high'], self.df['low'], self.df['close'])

    def cal_wclprice(self):
        """
        计算加权收盘价（WCLPRICE）。
        名称：加权收盘价
        简介：计算最高价、最低价和收盘价的加权平均值，其中收盘价的权重为2，最高价和最低价的权重各为1。

        参数:
        无
        """
        self.df['WCLPRICE'] = talib.WCLPRICE(self.df['high'], self.df['low'], self.df['close'])
    
    # 周期指标
    def cal_ht_dcperiod(self):
        """
        计算希尔伯特变换-主导周期（HT_DCPERIOD）。
        名称：希尔伯特变换-主导周期
        简介：将价格作为信息信号，计算价格处在的周期的位置，作为择时的依据。[^1^]

        参数:
        无
        """
        self.df['HT_DCPERIOD'] = talib.HT_DCPERIOD(self.df['close'])

    def cal_ht_dcphase(self):
        """
        计算希尔伯特变换-主导循环阶段（HT_DCPHASE）。
        名称：希尔伯特变换-主导循环阶段
        简介：涉及希尔伯特变换在时间序列分析中的应用，用于识别价格趋势中的主要周期性模式。[^1^]

        参数:
        无
        """
        self.df['HT_DCPHASE'] = talib.HT_DCPHASE(self.df['close'])

    def cal_ht_phasor(self):
        """
        计算希尔伯特变换-希尔伯特变换相量分量（HT_PHASOR）。
        名称：希尔伯特变换-希尔伯特变换相量分量
        简介：返回两个值：相角（inphase）和正交幅度（quadrature）。[^1^]

        参数:
        无
        """
        inphase, quadrature = talib.HT_PHASOR(self.df['close'])
        self.df['HT_PHASOR_INPHASE'] = inphase
        self.df['HT_PHASOR_QUADRATURE'] = quadrature

    def cal_ht_sine(self):
        """
        计算希尔伯特变换-正弦波（HT_SINE）。
        名称：希尔伯特变换-正弦波
        简介：返回两个值：实部和虚部，实部可以视为时间序列的正弦部分，虚部可以视为余弦部分。[^1^]

        参数:
        无
        """
        sine, leadsine = talib.HT_SINE(self.df['close'])
        self.df['HT_SINE'] = sine
        self.df['LEADSINE'] = leadsine

    def cal_ht_trendmode(self):
        """
        计算希尔伯特变换-趋势与周期模式（HT_TRENDMODE）。
        名称：希尔伯特变换-趋势与周期模式
        简介：用于识别当前市场是处于趋势模式还是周期模式。[^1^]

        参数:
        无
        """
        self.df['HT_TRENDMODE'] = talib.HT_TRENDMODE(self.df['close'])

    # 价格形态指标
    def cal_cdl2crows(self):
        """
        计算两只乌鸦（CDL2CROWS）。
        名称：Two Crows 两只乌鸦
        简介：三日K线模式，第一天长阳，第二天高开收阴，第三天再次高开继续收阴，收盘比前一日收盘价低，预示股价下跌。

        参数:
        无
        """
        self.df['CDL2CROWS'] = talib.CDL2CROWS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdl3blackcrows(self):
        """
        计算三只乌鸦（CDL3BLACKCROWS）。
        名称：Three Black Crows 三只乌鸦
        简介：三日K线模式，连续三根阴线，每日收盘价都下跌且接近最低价，每日开盘价都在上根K线实体内，预示股价下跌。

        参数:
        无
        """
        self.df['CDL3BLACKCROWS'] = talib.CDL3BLACKCROWS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdl3inside(self):
        """
        计算三内部上涨和下跌（CDL3INSIDE）。
        名称：Three Inside Up/Down 三内部上涨和下跌
        简介：三日K线模式，母子信号+长K线，以三内部上涨为例，K线为阴阳阳，第三天收盘价高于第一天开盘价，第二天K线在第一天K线内部，预示着股价上涨。

        参数:
        无
        """
        self.df['CDL3INSIDE'] = talib.CDL3INSIDE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdl3linestrike(self):
        """
        计算三线打击（CDL3LINESTRIKE）。
        名称：Three-Line Strike 三线打击
        简介：四日K线模式，前三根阳线，每日收盘价都比前一日高，开盘价在前一日实体内，第四日市场高开，收盘价低于第一日开盘价，预示股价下跌。

        参数:
        无
        """
        self.df['CDL3LINESTRIKE'] = talib.CDL3LINESTRIKE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdl3outside(self):
        """
        计算三外部上涨和下跌（CDL3OUTSIDE）。
        名称：Three Outside Up/Down 三外部上涨和下跌
        简介：三日K线模式，与三内部上涨和下跌类似，K线为阴阳阳，但第一日与第二日的K线形态相反，以三外部上涨为例，第一日K线在第二日K线内部，预示着股价上涨。

        参数:
        无
        """
        self.df['CDL3OUTSIDE'] = talib.CDL3OUTSIDE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdl3starsinsouth(self):
        """
        计算南方三星（CDL3STARSINSOUTH）。
        名称：Three Stars In The South 南方三星
        简介：三日K线模式，与大敌当前相反，三日K线皆阴，第一日有长下影线，第二日与第一日类似，K线整体小于第一日，第三日无下影线实体信号，成交价格都在第一日振幅之内，预示下跌趋势反转，股价上升。

        参数:
        无
        """
        self.df['CDL3STARSINSOUTH'] = talib.CDL3STARSINSOUTH(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdl3whitesoldiers(self):
        """
        计算三个白兵（CDL3WHITESOLDIERS）。
        名称：Three Advancing White Soldiers 三个白兵
        简介：三日K线模式，三日K线皆阳，每日收盘价变高且接近最高价，开盘价在前一日实体上半部，预示股价上升。

        参数:
        无
        """
        self.df['CDL3WHITESOLDIERS'] = talib.CDL3WHITESOLDIERS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlabandonedbaby(self):
        """
        计算弃婴（CDLABANDONEDBABY）。
        名称：Abandoned Baby 弃婴
        简介：三日K线模式，第二日价格跳空且收十字星（开盘价与收盘价接近，最高价最低价相差不大），预示趋势反转，发生在顶部下跌，底部上涨。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLABANDONEDBABY'] = talib.CDLABANDONEDBABY(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdladvanceblock(self):
        """
        计算大敌当前（CDLADVANCEBLOCK）。
        名称：Advance Block 大敌当前
        简介：三日K线模式，三日都收阳，每日收盘价都比前一日高，开盘价都在前一日实体以内，实体变短，上影线变长。

        参数:
        无
        """
        self.df['CDLADVANCEBLOCK'] = talib.CDLADVANCEBLOCK(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlbelthold(self):
        """
        计算捉腰带线（CDLBELTHOLD）。
        名称：Belt-hold 捉腰带线
        简介：两日K线模式，下跌趋势中，第一日阴线，第二日开盘价为最低价，阳线，收盘价接近最高价，预示价格上涨。

        参数:
        无
        """
        self.df['CDLBELTHOLD'] = talib.CDLBELTHOLD(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlbreakaway(self):
        """
        计算脱离（CDLBREAKAWAY）。
        名称：Breakaway 脱离
        简介：五日K线模式，以看涨脱离为例，下跌趋势中，第一日长阴线，第二日跳空阴线，延续趋势开始震荡，第五日长阳线，收盘价在第一天收盘价与第二天开盘价之间，预示价格上涨。

        参数:
        无
        """
        self.df['CDLBREAKAWAY'] = talib.CDLBREAKAWAY(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlclosingmarubozu(self):
        """
        计算收盘缺影线（CDLCLOSINGMARUBOZU）。
        名称：Closing Marubozu 收盘缺影线
        简介：一日K线模式，以阳线为例，最低价低于开盘价，收盘价等于最高价，预示着趋势持续。

        参数:
        无
        """
        self.df['CDLCLOSINGMARUBOZU'] = talib.CDLCLOSINGMARUBOZU(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlconcealbabyswallow(self):
        """
        计算藏婴吞没（CDLCONCEALBABYSWALL）。
        名称：Concealing Baby Swallow 藏婴吞没
        简介：四日K线模式，下跌趋势中，前两日阴线无影线，第二日开盘、收盘价皆低于第二日，第三日倒锤头，第四日开盘价高于前一日最高价，收盘价低于前一日最低价，预示着底部反转。

        参数:
        无
        """
        self.df['CDLCONCEALBABYSWALL'] = talib.CDLCONCEALBABYSWALL(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlcounterattack(self):
        """
        计算反击线（CDLCOUNTERATTACK）。
        名称：Counterattack 反击线
        简介：二日K线模式，与分离线类似。

        参数:
        无
        """
        self.df['CDLCOUNTERATTACK'] = talib.CDLCOUNTERATTACK(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdldarkcloudcover(self):
        """
        计算乌云压顶（CDLDARKCLOUDCOVER）。
        名称：Dark Cloud Cover 乌云压顶
        简介：二日K线模式，第一日长阳，第二日开盘价高于前一日最高价，收盘价处于前一日实体中部以下，预示着股价下跌。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLDARKCLOUDCOVER'] = talib.CDLDARKCLOUDCOVER(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdldoji(self):
        """
        计算十字（CDLDOJI）。
        名称：Doji 十字
        简介：一日K线模式，开盘价与收盘价基本相同。

        参数:
        无
        """
        self.df['CDLDOJI'] = talib.CDLDOJI(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdldojistar(self):
        """
        计算十字星（CDLDOJISTAR）。
        名称：Doji Star 十字星
        简介：一日K线模式，开盘价与收盘价基本相同，上下影线不会很长，预示着当前趋势反转。

        参数:
        无
        """
        self.df['CDLDOJISTAR'] = talib.CDLDOJISTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdldragonflydoji(self):
        """
        计算蜻蜓十字/T形十字（CDLDRAGONFLYDOJI）。
        名称：Dragonfly Doji 蜻蜓十字/T形十字
        简介：一日K线模式，开盘后价格一路走低，之后收复，收盘价与开盘价相同，预示趋势反转。

        参数:
        无
        """
        self.df['CDLDRAGONFLYDOJI'] = talib.CDLDRAGONFLYDOJI(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlengulping(self):
        """
        计算吞噬模式（CDLENGULFING）。
        名称：Engulfing Pattern 吞噬模式
        简介：两日K线模式，分多头吞噬和空头吞噬，以多头吞噬为例，第一日为阴线，第二日阳线，第一日的开盘价和收盘价在第二日开盘价收盘价之内，但不能完全相同。

        参数:
        无
        """
        self.df['CDLENGULFING'] = talib.CDLENGULFING(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdleveningdojistar(self):
        """
        计算十字暮星（CDLEVENINGDOJISTAR）。
        名称：Evening Doji Star 十字暮星
        简介：三日K线模式，基本模式为暮星，第二日收盘价和开盘价相同，预示顶部反转。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLEVENINGDOJISTAR'] = talib.CDLEVENINGDOJISTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdleveningstar(self):
        """
        计算暮星（CDLEVENINGSTAR）。
        名称：Evening Star 暮星
        简介：三日K线模式，与晨星相反，上升趋势中, 第一日阳线，第二日价格振幅较小，第三日阴线，预示顶部反转。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLEVENINGSTAR'] = talib.CDLEVENINGSTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdlgapsidesidewhite(self):
        """
        计算向上/下跳空并列阳线（CDLGAPSIDESIDEWHITE）。
        名称：Up/Down-gap side-by-side white lines 向上/下跳空并列阳线
        简介：二日K线模式，上升趋势向上跳空，下跌趋势向下跳空，第一日与第二日有相同开盘价，实体长度差不多，则趋势持续。

        参数:
        无
        """
        self.df['CDLGAPSIDESIDEWHITE'] = talib.CDLGAPSIDESIDEWHITE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlgravestonedoji(self):
        """
        计算墓碑十字/倒T十字（CDLGRAVESTONEDOJI）。
        名称：Gravestone Doji 墓碑十字/倒T十字
        简介：一日K线模式，开盘价与收盘价相同，上影线长，无下影线，预示底部反转。

        参数:
        无
        """
        self.df['CDLGRAVESTONEDOJI'] = talib.CDLGRAVESTONEDOJI(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlhammer(self):
        """
        计算锤头（CDLHAMMER）。
        名称：Hammer 锤头
        简介：一日K线模式，实体较短，无上影线，下影线大于实体长度两倍，处于下跌趋势底部，预示反转。

        参数:
        无
        """
        self.df['CDLHAMMER'] = talib.CDLHAMMER(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlhangingman(self):
        """
        计算上吊线（CDLHANGINGMAN）。
        名称：Hanging Man 上吊线
        简介：一日K线模式，形状与锤子类似，处于上升趋势的顶部，预示着趋势反转。

        参数:
        无
        """
        self.df['CDLHANGINGMAN'] = talib.CDLHANGINGMAN(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlharami(self):
        """
        计算母子线（CDLHARAMI）。
        名称：Harami Pattern 母子线
        简介：二日K线模式，分多头母子与空头母子，两者相反，以多头母子为例，在下跌趋势中，第一日K线长阴，第二日开盘价收盘价在第一日价格振幅之内，为阳线，预示趋势反转，股价上升。

        参数:
        无
        """
        self.df['CDLHARAMI'] = talib.CDLHARAMI(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlharamicross(self):
        """
        计算十字孕线（CDLHARAMICROSS）。
        名称：Harami Cross Pattern 十字孕线
        简介：二日K线模式，与母子县类似，若第二日K线是十字线，便称为十字孕线，预示着趋势反转。

        参数:
        无
        """
        self.df['CDLHARAMICROSS'] = talib.CDLHARAMICROSS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlhighwave(self):
        """
        计算风高浪大线（CDLHIGHWAVE）。
        名称：High-Wave Candle 风高浪大线
        简介：三日K线模式，具有极长的上/下影线与短的实体，预示着趋势反转。

        参数:
        无
        """
        self.df['CDLHIGHWAVE'] = talib.CDLHIGHWAVE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlhikkake(self):
        """
        计算陷阱（CDLHIKKAKE）。
        名称：Hikkake Pattern 陷阱
        简介：三日K线模式，与母子类似，第二日价格在前一日实体范围内, 第三日收盘价高于前两日，反转失败，趋势继续。

        参数:
        无
        """
        self.df['CDLHIKKAKE'] = talib.CDLHIKKAKE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlhikkakemod(self):
        """
        计算修正陷阱（CDLHIKKAKEMOD）。
        名称：Modified Hikkake Pattern 修正陷阱
        简介：三日K线模式，与陷阱类似，上升趋势中，第三日跳空高开；下跌趋势中，第三日跳空低开，反转失败，趋势继续。

        参数:
        无
        """
        self.df['CDLHIKKAKEMOD'] = talib.CDLHIKKAKEMOD(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlhomingpigeon(self):
        """
        计算家鸽（CDLHOMINGPIGEON）。
        名称：Homing Pigeon 家鸽
        简介：二日K线模式，与母子线类似，不同的是二日K线颜色相同，第二日最高价、最低价都在第一日实体之内，预示着趋势反转。

        参数:
        无
        """
        self.df['CDLHOMINGPIGEON'] = talib.CDLHOMINGPIGEON(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlidentical3crows(self):
        """
        计算三胞胎乌鸦（CDLIDENTICAL3CROWS）。
        名称：Identical Three Crows 三胞胎乌鸦
        简介：三日K线模式，上涨趋势中，三日都为阴线，长度大致相等，每日开盘价等于前一日收盘价，收盘价接近当日最低价，预示价格下跌。

        参数:
        无
        """
        self.df['CDLIDENTICAL3CROWS'] = talib.CDLIDENTICAL3CROWS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlinneck(self):
        """
        计算颈内线（CDLINNECK）。
        名称：In-Neck Pattern 颈内线
        简介：二日K线模式，下跌趋势中，第一日长阴线，第二日开盘价较低，收盘价略高于第一日收盘价，阳线，实体较短，预示着下跌继续。

        参数:
        无
        """
        self.df['CDLINNECK'] = talib.CDLINNECK(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlinvertedhammer(self):
        """
        计算倒锤头（CDLINVERTEDHAMMER）。
        名称：Inverted Hammer 倒锤头
        简介：一日K线模式，上影线较长，长度为实体2倍以上，无下影线，在下跌趋势底部，预示着趋势反转。

        参数:
        无
        """
        self.df['CDLINVERTEDHAMMER'] = talib.CDLINVERTEDHAMMER(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlkicking(self):
        """
        计算反冲形态（CDLKICKING）。
        名称：Kicking 反冲形态
        简介：二日K线模式，与分离线类似，两日K线为秃线，颜色相反，存在跳空缺口。

        参数:
        无
        """
        self.df['CDLKICKING'] = talib.CDLKICKING(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlkickingbylength(self):
        """
        计算由较长缺影线决定的反冲形态（CDLKICKINGBYLENGTH）。
        名称：Kicking - bull/bear determined by the longer marubozu 由较长缺影线决定的反冲形态
        简介：二日K线模式，与反冲形态类似，较长缺影线决定价格的涨跌。

        参数:
        无
        """
        self.df['CDLKICKINGBYLENGTH'] = talib.CDLKICKINGBYLENGTH(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlladderbottom(self):
        """
        计算梯底（CDLLADDERBOTTOM）。
        名称：Ladder Bottom 梯底
        简介：五日K线模式，下跌趋势中，前三日阴线，开盘价与收盘价皆低于前一日开盘、收盘价，第四日倒锤头，第五日开盘价高于前一日开盘价，阳线，收盘价高于前几日价格振幅，预示着底部反转。

        参数:
        无
        """
        self.df['CDLLADDERBOTTOM'] = talib.CDLLADDERBOTTOM(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdllongleggeddoji(self):
        """
        计算长脚十字（CDLLONGLEGGEDDOJI）。
        名称：Long Legged Doji 长脚十字
        简介：一日K线模式，开盘价与收盘价相同居当日价格中部，上下影线长，表达市场不确定性。

        参数:
        无
        """
        self.df['CDLLONGLEGGEDDOJI'] = talib.CDLLONGLEGGEDDOJI(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdllongline(self):
        """
        计算长蜡烛（CDLLONGLINE）。
        名称：Long Line Candle 长蜡烛
        简介：一日K线模式，K线实体长，无上下影线。

        参数:
        无
        """
        self.df['CDLLONGLINE'] = talib.CDLLONGLINE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlmarubozu(self):
        """
        计算光头光脚/缺影线（CDLMARUBOZU）。
        名称：Marubozu 光头光脚/缺影线
        简介：一日K线模式，上下两头都没有影线的实体，阴线预示着熊市持续或者牛市反转，阳线相反。

        参数:
        无
        """
        self.df['CDLMARUBOZU'] = talib.CDLMARUBOZU(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlmatchinglow(self):
        """
        计算相同低价（CDLMATCHINGLOW）。
        名称：Matching Low 相同低价
        简介：二日K线模式，下跌趋势中，第一日长阴线，第二日阴线，收盘价与前一日相同，预示底部确认，该价格为支撑位。

        参数:
        无
        """
        self.df['CDLMATCHINGLOW'] = talib.CDLMATCHINGLOW(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlmathold(self):
        """
        计算铺垫（CDLMATHOLD）。
        名称：Mat Hold 铺垫
        简介：五日K线模式，上涨趋势中，第一日阳线，第二日跳空高开影线，第三、四日短实体影线，第五日阳线，收盘价高于前四日，预示趋势持续。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLMATHOLD'] = talib.CDLMATHOLD(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdlmorningdojistar(self):
        """
        计算十字晨星（CDLMORNINGDOJISTAR）。
        名称：Morning Doji Star 十字晨星
        简介：三日K线模式，基本模式为晨星，第二日K线为十字星，预示底部反转。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLMORNINGDOJISTAR'] = talib.CDLMORNINGDOJISTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdlmorningstar(self):
        """
        计算晨星（CDLMORNINGSTAR）。
        名称：Morning Star 晨星
        简介：三日K线模式，下跌趋势，第一日阴线，第二日价格振幅较小，第三天阳线，预示底部反转。

        参数:
        penetration -- 穿透比例，默认为0。
        """
        self.df['CDLMORNINGSTAR'] = talib.CDLMORNINGSTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'], penetration=0)

    def cal_cdlonneck(self):
        """
        计算颈上线（CDLONNECK）。
        名称：On-Neck Pattern 颈上线
        简介：二日K线模式，下跌趋势中，第一日长阴线，第二日开盘价较低，收盘价与前一日最低价相同，阳线，实体较短，预示着延续下跌趋势。

        参数:
        无
        """
        self.df['CDLONNECK'] = talib.CDLONNECK(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlpiercing(self):
        """
        计算刺透形态（CDLPIERCING）。
        名称：Piercing Pattern 刺透形态
        简介：两日K线模式，下跌趋势中，第一日阴线，第二日收盘价低于前一日最低价，收盘价处在第一日实体上部，预示着底部反转。

        参数:
        无
        """
        self.df['CDLPIERCING'] = talib.CDLPIERCING(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlrickshawman(self):
        """
        计算黄包车夫（CDLRICKSHAWMAN）。
        名称：Rickshaw Man 黄包车夫
        简介：一日K线模式，与长腿十字线类似，若实体正好处于价格振幅中点，称为黄包车夫。

        参数:
        无
        """
        self.df['CDLRICKSHAWMAN'] = talib.CDLRICKSHAWMAN(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlriselfall3methods(self):
        """
        计算上升/下降三法（CDLRISEFALL3METHODS）。
        名称：Rising/Falling Three Methods 上升/下降三法
        简介：五日K线模式，以上升三法为例，上涨趋势中，第一日长阳线，中间三日价格在第一日范围内小幅震荡，第五日长阳线，收盘价高于第一日收盘价，预示股价上升。

        参数:
        无
        """
        self.df['CDLRISEFALL3METHODS'] = talib.CDLRISEFALL3METHODS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlseparatinglines(self):
        """
        计算分离线（CDLSEPARATINGLINES）。
        名称：Separating Lines 分离线
        简介：二日K线模式，上涨趋势中，第一日阴线，第二日阳线，第二日开盘价与第一日相同且为最低价，预示着趋势继续。

        参数:
        无
        """
        self.df['CDLSEPARATINGLINES'] = talib.CDLSEPARATINGLINES(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlshootingstar(self):
        """
        计算射击之星（CDLSHOOTINGSTAR）。
        名称：Shooting Star 射击之星
        简介：一日K线模式，上影线至少为实体长度两倍，没有下影线，预示着股价下跌

        参数:
        无
        """
        self.df['CDLSHOOTINGSTAR'] = talib.CDLSHOOTINGSTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlshortline(self):
        """
        计算短蜡烛（CDLSHORTLINE）。
        名称：Short Line Candle 短蜡烛
        简介：一日K线模式，实体短，无上下影线

        参数:
        无
        """
        self.df['CDLSHORTLINE'] = talib.CDLSHORTLINE(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlspinningtop(self):
        """
        计算纺锤（CDLSPINNINGTOP）。
        名称：Spinning Top 纺锤
        简介：一日K线，实体小。

        参数:
        无
        """
        self.df['CDLSPINNINGTOP'] = talib.CDLSPINNINGTOP(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlstalledpattern(self):
        """
        计算停顿形态（CDLSTALLEDPATTERN）。
        名称：Stalled Pattern 停顿形态
        简介：三日K线模式，上涨趋势中，第二日长阳线，第三日开盘于前一日收盘价附近，短阳线，预示着上涨结束

        参数:
        无
        """
        self.df['CDLSTALLEDPATTERN'] = talib.CDLSTALLEDPATTERN(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlsticksandwich(self):
        """
        计算条形三明治（CDLSTICKSANDWICH）。
        名称：Stick Sandwich 条形三明治
        简介：三日K线模式，第一日长阴线，第二日阳线，开盘价高于前一日收盘价，第三日开盘价高于前两日最高价，收盘价于第一日收盘价相同。

        参数:
        无
        """
        self.df['CDLSTICKSANDWICH'] = talib.CDLSTICKSANDWICH(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdltaburi(self):
        """
        计算探水竿（CDLTAKURI）。
        名称：Takuri (Dragonfly Doji with very long lower shadow) 探水竿
        简介：一日K线模式，大致与蜻蜓十字相同，下影线长度长。

        参数:
        无
        """
        self.df['CDLTAKURI'] = talib.CDLTAKURI(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdltasukigap(self):
        """
        计算跳空并列阴阳线（CDLTASUKIGAP）。
        名称：Tasuki Gap 跳空并列阴阳线
        简介：三日K线模式，分上涨和下跌，以上升为例，前两日阳线，第二日跳空，第三日阴线，收盘价于缺口中，上升趋势持续。

        参数:
        无
        """
        self.df['CDLTASUKIGAP'] = talib.CDLTASUKIGAP(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlthrusting(self):
        """
        计算插入（CDLTHRUSTING）。
        名称：Thrusting Pattern 插入
        简介：二日K线模式，与颈上线类似，下跌趋势中，第一日长阴线，第二日开盘价跳空，收盘价略低于前一日实体中部，与颈上线相比实体较长，预示着趋势持续。

        参数:
        无
        """
        self.df['CDLTHRUSTING'] = talib.CDLTHRUSTING(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdltristart(self):
        """
        计算三星（CDLTRISTAR）。
        名称：Tristar Pattern 三星
        简介：三日K线模式，由三个十字组成，第二日十字必须高于或者低于第一日和第三日，预示着反转。

        参数:
        无
        """
        self.df['CDLTRISTAR'] = talib.CDLTRISTAR(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlunique3river(self):
        """
        计算奇特三河床（CDLUNIQUE3RIVER）。
        名称：Unique 3 River 奇特三河床
        简介：三日K线模式，下跌趋势中，第一日长阴线，第二日为锤头，最低价创新低，第三日开盘价低于第二日收盘价，收阳线，收盘价不高于第二日收盘价，预示着反转，第二日下影线越长可能性越大。

        参数:
        无
        """
        self.df['CDLUNIQUE3RIVER'] = talib.CDLUNIQUE3RIVER(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlupsidegap2crows(self):
        """
        计算向上跳空的两只乌鸦（CDLUPSIDEGAP2CROWS）。
        名称：Upside Gap Two Crows 向上跳空的两只乌鸦
        简介：三日K线模式，第一日阳线，第二日跳空以高于第一日最高价开盘，收阴线，第三日开盘价高于第二日，收阴线，与第一日比仍有缺口。

        参数:
        无
        """
        self.df['CDLUPSIDEGAP2CROWS'] = talib.CDLUPSIDEGAP2CROWS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    def cal_cdlxsidegap3methods(self):
        """
        计算上升/下降跳空三法（CDLXSIDEGAP3METHODS）。
        名称：Upside/Downside Gap Three Methods 上升/下降跳空三法
        简介：五日K线模式，以上升跳空三法为例，上涨趋势中，第一日长阳线，第二日短阳线，第三日跳空阳线，第四日阴线，开盘价与收盘价于前两日实体内，第五日长阳线，收盘价高于第一日收盘价，预示股价上升。

        参数:
        无
        """
        self.df['CDLXSIDEGAP3METHODS'] = talib.CDLXSIDEGAP3METHODS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])

    # 统计学指标

    def cal_beta(self, timeperiod=5):
        """
        计算β系数（BETA）。
        名称：β系数也称为贝塔系数
        简介：一种风险指数，用来衡量个别股票或股票基金相对于整个股市的价格波动情况。

        参数:
        timeperiod -- 计算周期，默认为5。
        """
        self.df['BETA'] = talib.BETA(self.df['high'], self.df['low'], timeperiod=timeperiod)

    def cal_correl(self, timeperiod=30):
        """
        计算皮尔逊相关系数（CORREL）。
        名称：皮尔逊相关系数
        简介：用于度量两个变量X和Y之间的相关（线性相关），其值介于-1与1之间。

        参数:
        timeperiod -- 计算周期，默认为30。
        """
        self.df['CORREL'] = talib.CORREL(self.df['high'], self.df['low'], timeperiod=timeperiod)

    def cal_linearreg(self, timeperiod=14):
        """
        计算线性回归（LINEARREG）。
        名称：线性回归
        简介：来确定两种或两种以上变量间相互依赖的定量关系的一种统计分析方法。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['LINEARREG'] = talib.LINEARREG(self.df['close'], timeperiod=timeperiod)

    def cal_linearreg_angle(self, timeperiod=14):
        """
        计算线性回归的角度（LINEARREG_ANGLE）。
        名称：线性回归的角度
        简介：来确定价格的角度变化。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['LINEARREG_ANGLE'] = talib.LINEARREG_ANGLE(self.df['close'], timeperiod=timeperiod)

    def cal_linearreg_intercept(self, timeperiod=14):
        """
        计算线性回归截距（LINEARREG_INTERCEPT）。
        名称：线性回归截距

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['LINEARREG_INTERCEPT'] = talib.LINEARREG_INTERCEPT(self.df['close'], timeperiod=timeperiod)

    def cal_linearreg_slope(self, timeperiod=14):
        """
        计算线性回归斜率指标（LINEARREG_SLOPE）。
        名称：线性回归斜率指标

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['LINEARREG_SLOPE'] = talib.LINEARREG_SLOPE(self.df['close'], timeperiod=timeperiod)

    def cal_stddev(self, timeperiod=5, nbdev=1):
        """
        计算标准偏差（STDDEV）。
        名称：标准偏差
        简介：种量度数据分布的分散程度之标准，用以衡量数据值偏离算术平均值的程度。

        参数:
        timeperiod -- 计算周期，默认为5。
        nbdev -- 偏差数量，默认为1。
        """
        self.df['STDDEV'] = talib.STDDEV(self.df['close'], timeperiod=timeperiod, nbdev=nbdev)

    def cal_tsf(self, timeperiod=14):
        """
        计算时间序列预测（TSF）。
        名称：时间序列预测
        简介：一种历史资料延伸预测，也称历史引伸预测法。

        参数:
        timeperiod -- 计算周期，默认为14。
        """
        self.df['TSF'] = talib.TSF(self.df['close'], timeperiod=timeperiod)

    def cal_var(self, timeperiod=5, nbdev=1):
        """
        计算方差（VAR）。
        名称：方差
        简介：方差用来计算每一个变量（观察值）与总体均数之间的差异。

        参数:
        timeperiod -- 计算周期，默认为5。
        nbdev -- 偏差数量，默认为1。
        """
        self.df['VAR'] = talib.VAR(self.df['close'], timeperiod=timeperiod, nbdev=nbdev)

class StockIndicatorsCalculator:
    def __init__(self, data):
        """
        初始化StockIndicatorsCalculator类。
        
        参数:
        data -- 包含股票数据的pandas.DataFrame对象，必须包含'Open', 'High', 'Low', 'Close', 'Volume'列。
        """
        self.data = data.copy()

    def calculate_ma(self, timeperiod=5):
        """计算移动平均线（MA）。"""
        self.data['MA{}'.format(timeperiod)] = self.data['Close'].rolling(window=timeperiod).mean()

    def calculate_ema(self, timeperiod=5):
        """计算指数移动平均线（EMA）。"""
        self.data['EMA{}'.format(timeperiod)] = self.data['Close'].ewm(span=timeperiod, adjust=False).mean()

    def calculate_rsi(self, timeperiod=14):
        """计算相对强弱指数（RSI）。"""
        delta = self.data['Close'].diff(1)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        rsi = 100 - (100 / (1 + up.rolling(window=timeperiod).mean() / down.rolling(window=timeperiod).mean()))
        self.data['RSI'] = rsi

    def calculate_bbands(self, timeperiod=5, nbdevup=2, nbdevdn=2, median_period=20):
        """计算布林带（Bollinger Bands）。"""
        self.data['MA{}'.format(median_period)] = self.data['Close'].rolling(window=median_period).mean()
        self.data['STDDEV{}'.format(timeperiod)] = self.data['Close'].rolling(window=timeperiod).std()
        self.data['UPPER_BAND'] = self.data['MA{}'.format(median_period)] + (self.data['STDDEV{}'.format(timeperiod)] * nbdevup)
        self.data['LOWER_BAND'] = self.data['MA{}'.format(median_period)] - (self.data['STDDEV{}'.format(timeperiod)] * nbdevdn)
        self.data['MIDDLE_BAND'] = self.data['MA{}'.format(median_period)]

    def calculate_macd(self, fastperiod=12, slowperiod=26, signalperiod=9):
        """计算MACD。"""
        self.data['EMA{}'.format(fastperiod)] = self.data['Close'].ewm(span=fastperiod, adjust=False).mean()
        self.data['EMA{}'.format(slowperiod)] = self.data['Close'].ewm(span=slowperiod, adjust=False).mean()
        self.data['MACD'] = self.data['EMA{}'.format(fastperiod)] - self.data['EMA{}'.format(slowperiod)]
        self.data['Signal_Line'] = self.data['MACD'].ewm(span=signalperiod, adjust=False).mean()
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['Signal_Line']

    # 指数移动均线工具
    def get_MA_EMA(self, n):
        df = self.data
        newname = "EMA" + str(n)
        df[newname] = 0  # 初始化n天指数移动均线
        for i in range(n - 1, len(df)):  # 循环第n个数据开始，为之后的每个数据计算EMA
            list_temp = []
            list_ema = []
            for d in range(n):  # 添加数据
                list_temp.append(df.loc[i - (n - d) + 1, "close"])
                list_ema.append(0)
            for d in range(n):  # 进行计算
                if d == 0:
                    list_ema[d] = list_temp[d]
                else:
                    list_ema[d] = (2 * list_temp[d] + (n - 1) * list_ema[d - 1]) / (n + 1)
            df.loc[i, newname] = list_ema[n - 1]
        # print("    --已计算指数移动均线EMA{}".format(n))
        self.data = df
 
    # 移动均线计算
    def get_MA(self, n):
        df = self.data
        newname = "MA" + str(n)
        df[newname] = None  # 初始化n天指数移动均线
        for i in range(n-1,len(df)):
            list_temp = []
            sum = 0
            avg = 0
            for d in range(n):
                sum = sum + df.loc[ i-(n-d)+1 ,"close"]
            avg = round(sum/n,2)
            df.loc[i, newname] = avg
        # print("    --已计算移动均线MA{}".format(n))
 
    # 移动均线计算
    def get_Vol_MA(self, n):
        df = self.data
        newname = "VolMA" + str(n)
        df[newname] = None  # 初始化n天指数移动均线
        for i in range(n-1,len(df)):
            list_temp = []
            sum = 0
            avg = 0
            for d in range(n):
                sum = sum + df.loc[ i-(n-d)+1 ,"vol"]
            avg = round(sum/n,2)
            df.loc[i, newname] = avg
        # print("    --已计算成交量移动均线MA{}".format(n))
 
    # Macd的快速线DIF计算
    def get_Macd_DIF(self, n1, n2):
        df = self.data
        newname = "Macd_DIF"
        df[newname] = 0  # 初始化n天指数移动均线
        for i in range(n2,len(df)):
            df.loc[i, "Macd_DIF"] = df.loc[i, "EMA" + str(n1)] - df.loc[i, "EMA" + str(n2)]
        # print("    --已计算MACD 快速线DIF")
        self.data = df
 
    # Macd的慢速线DEA计算
    def get_Macd_DEA(self, n):
        df = self.data
        newname = "Macd_DEA"
        df[newname] = 0  # 初始化n天指数移动均线
        for i in range(n - 1, len(df)):  # 循环第n个数据开始，为之后的每个数据计算EMA
            list_temp = []
            list_dif = []
            for d in range(n):  # 添加数据
                list_temp.append(df.loc[i - (n - d) + 1, "Macd_DIF"])
                list_dif.append(0)
            for d in range(n):  # 进行计算
                if d == 0:
                    list_dif[d] = list_temp[d]
                else:
                    list_dif[d] = (2 * list_temp[d] + (n - 1) * list_dif[d - 1]) / (n + 1)
            df.loc[i, newname] = list_dif[n - 1]
        # print("    --已计算MACD 慢速线DEA")
        self.data = df
 
    # 计算MACD柱状线
    def get_Macd_Bar(self,n):
        df = self.data
        for i in range(n,len(df)):
            df.loc[i,"MACD_Bar"] = 2 * ( df.loc[i, "Macd_DIF"] - df.loc[i, "Macd_DEA"])
        # print("    --已计算MACD 柱状线Bar")
        self.data = df
 
    # Macd计算
    def get_Macd(self, a=12, b=26, c=9):
 
        # print("正在计算MACD指标：")
 
        # 计算EMA12、EMA26 数据
        self.get_MA_EMA(a)
        self.get_MA_EMA(b)
 
        # 计算三条曲线
        self.get_Macd_DIF(a,b)
        self.get_Macd_DEA(c)
        self.get_Macd_Bar(b)
 
        # print("    --已完成MACD指标的计算")

