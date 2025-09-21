"""
基于TA-Lib库的指标计算实现
"""

import talib
import pandas as pd
from qindicator.core.indicator import Indicator, DataManager

class TalibIndicator(Indicator):
    """
    基于TA-Lib库的指标计算实现
    """
    
    def __init__(self):
        """
        初始化TA-Lib指标计算器
        """
        self.data_manager = DataManager()
    
    def calculate(self, data: pd.DataFrame, indicator_type: str = 'ma', **kwargs) -> pd.DataFrame:
        """
        统一的指标计算接口
        
        Args:
            data: 包含股票数据的DataFrame
            indicator_type: 指标类型，如'ma', 'ema', 'rsi'等
            **kwargs: 传递给具体指标计算方法的参数
        
        Returns:
            pd.DataFrame: 包含计算结果的DataFrame
        """
        # 验证数据
        if not self._validate_data(data):
            raise ValueError("输入数据无效，至少需要包含'close'列")
        
        # 准备数据
        df = self.data_manager.prepare_data(data)
        
        # 根据指标类型调用对应的计算方法
        indicator_method = getattr(self, f'calculate_{indicator_type}', None)
        if indicator_method is None:
            raise ValueError(f"不支持的指标类型: {indicator_type}")
        
        return indicator_method(df, **kwargs)
    
    def calculate_ma(self, df: pd.DataFrame, timeperiod: int = 5) -> pd.DataFrame:
        """
        计算移动平均线（MA）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: MA的周期，默认为5
        
        Returns:
            DataFrame: 包含MA指标的DataFrame
        """
        df = df.copy()
        df[f'MA{timeperiod}'] = talib.MA(df['close'], timeperiod=timeperiod)
        return df
    
    def calculate_ema(self, df: pd.DataFrame, timeperiod: int = 5) -> pd.DataFrame:
        """
        计算指数移动平均线（EMA）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: EMA的周期，默认为5
        
        Returns:
            DataFrame: 包含EMA指标的DataFrame
        """
        df = df.copy()
        df[f'EMA{timeperiod}'] = talib.EMA(df['close'], timeperiod=timeperiod)
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算相对强弱指数（RSI）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: RSI的周期，默认为14
        
        Returns:
            DataFrame: 包含RSI指标的DataFrame
        """
        df = df.copy()
        df['RSI'] = talib.RSI(df['close'], timeperiod=timeperiod)
        return df
    
    def calculate_bbands(self, df: pd.DataFrame, timeperiod: int = 5, nbdevup: int = 2, nbdevdn: int = 2) -> pd.DataFrame:
        """
        计算布林带（Bollinger Bands）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 布林带的周期，默认为5
            nbdevup: 上轨偏差，默认为2
            nbdevdn: 下轨偏差，默认为2
        
        Returns:
            DataFrame: 包含布林带指标的DataFrame
        """
        df = df.copy()
        df['BB_UPPER'], df['BB_MIDDLE'], df['BB_LOWER'] = \
            talib.BBANDS(df['close'], timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=0)
        return df
    
    def calculate_macd(self, df: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> pd.DataFrame:
        """
        计算MACD指标
        
        Args:
            df: 包含股票数据的DataFrame
            fastperiod: 快速EMA周期，默认为12
            slowperiod: 慢速EMA周期，默认为26
            signalperiod: 信号线周期，默认为9
        
        Returns:
            DataFrame: 包含MACD指标的DataFrame
        """
        df = df.copy()
        macd, macd_signal, macd_hist = \
            talib.MACD(df['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        df['MACD'] = macd
        df['MACD_SIGNAL'] = macd_signal
        df['MACD_HIST'] = macd_hist
        return df

    def calculate_atr(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算平均真实波动幅度（ATR）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
        
        Returns:
            DataFrame: 包含ATR指标的DataFrame
        """
        df = df.copy()
        df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=timeperiod)
        return df

    # 波动率指标
    def calculate_natr(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算归一化波动幅度均值（NATR）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
        
        Returns:
            DataFrame: 包含NATR指标的DataFrame
        """
        df = df.copy()
        df['NATR'] = talib.NATR(df['high'], df['low'], df['close'], timeperiod=timeperiod)
        return df

    def calculate_trange(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算真正的范围（TRANGE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含TRANGE指标的DataFrame
        """
        df = df.copy()
        df['TRANGE'] = talib.TRANGE(df['high'], df['low'], df['close'])
        return df

    # 价格指标
    def calculate_avgprice(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算平均价格函数（AVGPRICE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含AVGPRICE指标的DataFrame
        """
        df = df.copy()
        df['AVGPRICE'] = talib.AVGPRICE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_medprice(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算中位数价格（MEDPRICE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含MEDPRICE指标的DataFrame
        """
        df = df.copy()
        df['MEDPRICE'] = talib.MEDPRICE(df['high'], df['low'])
        return df

    def calculate_typprice(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算代表性价格（TYPPRICE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含TYPPRICE指标的DataFrame
        """
        df = df.copy()
        df['TYPPRICE'] = talib.TYPPRICE(df['high'], df['low'], df['close'])
        return df

    def calculate_wclprice(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算加权收盘价（WCLPRICE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含WCLPRICE指标的DataFrame
        """
        df = df.copy()
        df['WCLPRICE'] = talib.WCLPRICE(df['high'], df['low'], df['close'])
        return df

    # 周期指标
    def calculate_ht_dcperiod(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-主导周期（HT_DCPERIOD）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_DCPERIOD指标的DataFrame
        """
        df = df.copy()
        df['HT_DCPERIOD'] = talib.HT_DCPERIOD(df['close'])
        return df

    def calculate_ht_dcphase(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-主导循环阶段（HT_DCPHASE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_DCPHASE指标的DataFrame
        """
        df = df.copy()
        df['HT_DCPHASE'] = talib.HT_DCPHASE(df['close'])
        return df

    def calculate_ht_phasor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-希尔伯特变换相量分量（HT_PHASOR）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_PHASOR指标的DataFrame
        """
        df = df.copy()
        inphase, quadrature = talib.HT_PHASOR(df['close'])
        df['HT_PHASOR_INPHASE'] = inphase
        df['HT_PHASOR_QUADRATURE'] = quadrature
        return df

    def calculate_ht_sine(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-正弦波（HT_SINE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_SINE指标的DataFrame
        """
        df = df.copy()
        sine, leadsine = talib.HT_SINE(df['close'])
        df['HT_SINE'] = sine
        df['LEADSINE'] = leadsine
        return df

    def calculate_ht_trendmode(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-趋势与周期模式（HT_TRENDMODE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_TRENDMODE指标的DataFrame
        """
        df = df.copy()
        df['HT_TRENDMODE'] = talib.HT_TRENDMODE(df['close'])
        return df

    # 价格形态指标
    def calculate_cdl2crows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算两只乌鸦（CDL2CROWS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL2CROWS指标的DataFrame
        """
        df = df.copy()
        df['CDL2CROWS'] = talib.CDL2CROWS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdl3blackcrows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三只乌鸦（CDL3BLACKCROWS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3BLACKCROWS指标的DataFrame
        """
        df = df.copy()
        df['CDL3BLACKCROWS'] = talib.CDL3BLACKCROWS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdl3inside(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三内部上涨和下跌（CDL3INSIDE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3INSIDE指标的DataFrame
        """
        df = df.copy()
        df['CDL3INSIDE'] = talib.CDL3INSIDE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdl3linestrike(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三线打击（CDL3LINESTRIKE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3LINESTRIKE指标的DataFrame
        """
        df = df.copy()
        df['CDL3LINESTRIKE'] = talib.CDL3LINESTRIKE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdl3outside(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三外部上涨和下跌（CDL3OUTSIDE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3OUTSIDE指标的DataFrame
        """
        df = df.copy()
        df['CDL3OUTSIDE'] = talib.CDL3OUTSIDE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdl3starsinsouth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算南方三星（CDL3STARSINSOUTH）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3STARSINSOUTH指标的DataFrame
        """
        df = df.copy()
        df['CDL3STARSINSOUTH'] = talib.CDL3STARSINSOUTH(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdl3whitesoldiers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三个白兵（CDL3WHITESOLDIERS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3WHITESOLDIERS指标的DataFrame
        """
        df = df.copy()
        df['CDL3WHITESOLDIERS'] = talib.CDL3WHITESOLDIERS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlabandonedbaby(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算弃婴（CDLABANDONEDBABY）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLABANDONEDBABY指标的DataFrame
        """
        df = df.copy()
        df['CDLABANDONEDBABY'] = talib.CDLABANDONEDBABY(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdladvanceblock(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算大敌当前（CDLADVANCEBLOCK）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLADVANCEBLOCK指标的DataFrame
        """
        df = df.copy()
        df['CDLADVANCEBLOCK'] = talib.CDLADVANCEBLOCK(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlbelthold(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算捉腰带线（CDLBELTHOLD）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLBELTHOLD指标的DataFrame
        """
        df = df.copy()
        df['CDLBELTHOLD'] = talib.CDLBELTHOLD(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlbreakaway(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算脱离（CDLBREAKAWAY）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLBREAKAWAY指标的DataFrame
        """
        df = df.copy()
        df['CDLBREAKAWAY'] = talib.CDLBREAKAWAY(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlclosingmarubozu(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算收盘缺影线（CDLCLOSINGMARUBOZU）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLCLOSINGMARUBOZU指标的DataFrame
        """
        df = df.copy()
        df['CDLCLOSINGMARUBOZU'] = talib.CDLCLOSINGMARUBOZU(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlconcealbabyswallow(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算藏婴吞没（CDLCONCEALBABYSWALL）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLCONCEALBABYSWALL指标的DataFrame
        """
        df = df.copy()
        df['CDLCONCEALBABYSWALL'] = talib.CDLCONCEALBABYSWALL(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlcounterattack(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算反击线（CDLCOUNTERATTACK）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLCOUNTERATTACK指标的DataFrame
        """
        df = df.copy()
        df['CDLCOUNTERATTACK'] = talib.CDLCOUNTERATTACK(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdldarkcloudcover(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算乌云压顶（CDLDARKCLOUDCOVER）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLDARKCLOUDCOVER指标的DataFrame
        """
        df = df.copy()
        df['CDLDARKCLOUDCOVER'] = talib.CDLDARKCLOUDCOVER(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdldoji(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算十字（CDLDOJI）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLDOJI指标的DataFrame
        """
        df = df.copy()
        df['CDLDOJI'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdldojistar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算十字星（CDLDOJISTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLDOJISTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLDOJISTAR'] = talib.CDLDOJISTAR(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlengulping(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算吞噬模式（CDLENGULFING）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLENGULFING指标的DataFrame
        """
        df = df.copy()
        df['CDLENGULFING'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdleveningdojistar(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算十字暮星（CDLEVENINGDOJISTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLEVENINGDOJISTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLEVENINGDOJISTAR'] = talib.CDLEVENINGDOJISTAR(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdleveningstar(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算暮星（CDLEVENINGSTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLEVENINGSTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLEVENINGSTAR'] = talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdlgapsidesidewhite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算向上/下跳空并列阳线（CDLGAPSIDESIDEWHITE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLGAPSIDESIDEWHITE指标的DataFrame
        """
        df = df.copy()
        df['CDLGAPSIDESIDEWHITE'] = talib.CDLGAPSIDESIDEWHITE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlhammer(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算锤头（CDLHAMMER）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHAMMER指标的DataFrame
        """
        df = df.copy()
        df['CDLHAMMER'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlhangingman(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算上吊线（CDLHANGINGMAN）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHANGINGMAN指标的DataFrame
        """
        df = df.copy()
        df['CDLHANGINGMAN'] = talib.CDLHANGINGMAN(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlharami(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算母子线（CDLHARAMI）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHARAMI指标的DataFrame
        """
        df = df.copy()
        df['CDLHARAMI'] = talib.CDLHARAMI(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlharamicross(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算十字孕线（CDLHARAMICROSS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHARAMICROSS指标的DataFrame
        """
        df = df.copy()
        df['CDLHARAMICROSS'] = talib.CDLHARAMICROSS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlhighwave(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算风高浪大线（CDLHIGHWAVE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHIGHWAVE指标的DataFrame
        """
        df = df.copy()
        df['CDLHIGHWAVE'] = talib.CDLHIGHWAVE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlhikkake(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算陷阱（CDLHIKKAKE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHIKKAKE指标的DataFrame
        """
        df = df.copy()
        df['CDLHIKKAKE'] = talib.CDLHIKKAKE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlhikkakemod(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算修正陷阱（CDLHIKKAKEMOD）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHIKKAKEMOD指标的DataFrame
        """
        df = df.copy()
        df['CDLHIKKAKEMOD'] = talib.CDLHIKKAKEMOD(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlhomingpigeon(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算家鸽（CDLHOMINGPIGEON）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHOMINGPIGEON指标的DataFrame
        """
        df = df.copy()
        df['CDLHOMINGPIGEON'] = talib.CDLHOMINGPIGEON(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlidentical3crows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三胞胎乌鸦（CDLIDENTICAL3CROWS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLIDENTICAL3CROWS指标的DataFrame
        """
        df = df.copy()
        df['CDLIDENTICAL3CROWS'] = talib.CDLIDENTICAL3CROWS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlinneck(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算颈内线（CDLINNECK）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLINNECK指标的DataFrame
        """
        df = df.copy()
        df['CDLINNECK'] = talib.CDLINNECK(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlinvertedhammer(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算倒锤头（CDLINVERTEDHAMMER）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLINVERTEDHAMMER指标的DataFrame
        """
        df = df.copy()
        df['CDLINVERTEDHAMMER'] = talib.CDLINVERTEDHAMMER(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlkicking(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算反冲形态（CDLKICKING）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLKICKING指标的DataFrame
        """
        df = df.copy()
        df['CDLKICKING'] = talib.CDLKICKING(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlkickingbylength(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算由较长缺影线决定的反冲形态（CDLKICKINGBYLENGTH）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLKICKINGBYLENGTH指标的DataFrame
        """
        df = df.copy()
        df['CDLKICKINGBYLENGTH'] = talib.CDLKICKINGBYLENGTH(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlladderbottom(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算梯底（CDLLADDERBOTTOM）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLLADDERBOTTOM指标的DataFrame
        """
        df = df.copy()
        df['CDLLADDERBOTTOM'] = talib.CDLLADDERBOTTOM(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdllongleggeddoji(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算长脚十字（CDLLONGLEGGEDDOJI）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLLONGLEGGEDDOJI指标的DataFrame
        """
        df = df.copy()
        df['CDLLONGLEGGEDDOJI'] = talib.CDLLONGLEGGEDDOJI(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdllongline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算长蜡烛（CDLLONGLINE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLLONGLINE指标的DataFrame
        """
        df = df.copy()
        df['CDLLONGLINE'] = talib.CDLLONGLINE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlmarubozu(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算光头光脚/缺影线（CDLMARUBOZU）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLMARUBOZU指标的DataFrame
        """
        df = df.copy()
        df['CDLMARUBOZU'] = talib.CDLMARUBOZU(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlmatchinglow(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算相同低价（CDLMATCHINGLOW）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLMATCHINGLOW指标的DataFrame
        """
        df = df.copy()
        df['CDLMATCHINGLOW'] = talib.CDLMATCHINGLOW(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlmathold(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算铺垫（CDLMATHOLD）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLMATHOLD指标的DataFrame
        """
        df = df.copy()
        df['CDLMATHOLD'] = talib.CDLMATHOLD(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdlmorningdojistar(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算十字晨星（CDLMORNINGDOJISTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLMORNINGDOJISTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLMORNINGDOJISTAR'] = talib.CDLMORNINGDOJISTAR(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdlmorningstar(self, df: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算晨星（CDLMORNINGSTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLMORNINGSTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLMORNINGSTAR'] = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'], penetration=penetration)
        return df

    def calculate_cdlonneck(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算颈上线（CDLONNECK）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLONNECK指标的DataFrame
        """
        df = df.copy()
        df['CDLONNECK'] = talib.CDLONNECK(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlpiercing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算刺透形态（CDLPIERCING）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLPIERCING指标的DataFrame
        """
        df = df.copy()
        df['CDLPIERCING'] = talib.CDLPIERCING(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlrickshawman(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算黄包车夫（CDLRICKSHAWMAN）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLRICKSHAWMAN指标的DataFrame
        """
        df = df.copy()
        df['CDLRICKSHAWMAN'] = talib.CDLRICKSHAWMAN(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlriselfall3methods(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算上升/下降三法（CDLRISEFALL3METHODS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLRISEFALL3METHODS指标的DataFrame
        """
        df = df.copy()
        df['CDLRISEFALL3METHODS'] = talib.CDLRISEFALL3METHODS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlseparatinglines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算分离线（CDLSEPARATINGLINES）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSEPARATINGLINES指标的DataFrame
        """
        df = df.copy()
        df['CDLSEPARATINGLINES'] = talib.CDLSEPARATINGLINES(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlshootingstar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算射击之星（CDLSHOOTINGSTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSHOOTINGSTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLSHOOTINGSTAR'] = talib.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlshortline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算短蜡烛（CDLSHORTLINE）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSHORTLINE指标的DataFrame
        """
        df = df.copy()
        df['CDLSHORTLINE'] = talib.CDLSHORTLINE(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlspinningtop(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算纺锤（CDLSPINNINGTOP）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSPINNINGTOP指标的DataFrame
        """
        df = df.copy()
        df['CDLSPINNINGTOP'] = talib.CDLSPINNINGTOP(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlstalledpattern(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算停顿形态（CDLSTALLEDPATTERN）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSTALLEDPATTERN指标的DataFrame
        """
        df = df.copy()
        df['CDLSTALLEDPATTERN'] = talib.CDLSTALLEDPATTERN(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlsticksandwich(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算条形三明治（CDLSTICKSANDWICH）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSTICKSANDWICH指标的DataFrame
        """
        df = df.copy()
        df['CDLSTICKSANDWICH'] = talib.CDLSTICKSANDWICH(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdltaburi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算探水竿（CDLTAKURI）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTAKURI指标的DataFrame
        """
        df = df.copy()
        df['CDLTAKURI'] = talib.CDLTAKURI(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdltasukigap(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算跳空并列阴阳线（CDLTASUKIGAP）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTASUKIGAP指标的DataFrame
        """
        df = df.copy()
        df['CDLTASUKIGAP'] = talib.CDLTASUKIGAP(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlthrusting(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算插入（CDLTHRUSTING）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTHRUSTING指标的DataFrame
        """
        df = df.copy()
        df['CDLTHRUSTING'] = talib.CDLTHRUSTING(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdltristart(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算三星（CDLTRISTAR）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTRISTAR指标的DataFrame
        """
        df = df.copy()
        df['CDLTRISTAR'] = talib.CDLTRISTAR(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlunique3river(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算奇特三河床（CDLUNIQUE3RIVER）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLUNIQUE3RIVER指标的DataFrame
        """
        df = df.copy()
        df['CDLUNIQUE3RIVER'] = talib.CDLUNIQUE3RIVER(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlupsidegap2crows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算向上跳空的两只乌鸦（CDLUPSIDEGAP2CROWS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLUPSIDEGAP2CROWS指标的DataFrame
        """
        df = df.copy()
        df['CDLUPSIDEGAP2CROWS'] = talib.CDLUPSIDEGAP2CROWS(df['open'], df['high'], df['low'], df['close'])
        return df

    def calculate_cdlxsidegap3methods(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算上升/下降跳空三法（CDLXSIDEGAP3METHODS）
        
        Args:
            df: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLXSIDEGAP3METHODS指标的DataFrame
        """
        df = df.copy()
        df['CDLXSIDEGAP3METHODS'] = talib.CDLXSIDEGAP3METHODS(df['open'], df['high'], df['low'], df['close'])
        return df

    # 统计学指标
    def calculate_beta(self, df: pd.DataFrame, timeperiod: int = 5) -> pd.DataFrame:
        """
        计算β系数（BETA）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为5
            
        Returns:
            DataFrame: 包含BETA指标的DataFrame
        """
        df = df.copy()
        df['BETA'] = talib.BETA(df['high'], df['low'], timeperiod=timeperiod)
        return df

    def calculate_correl(self, df: pd.DataFrame, timeperiod: int = 30) -> pd.DataFrame:
        """
        计算皮尔逊相关系数（CORREL）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为30
            
        Returns:
            DataFrame: 包含CORREL指标的DataFrame
        """
        df = df.copy()
        df['CORREL'] = talib.CORREL(df['high'], df['low'], timeperiod=timeperiod)
        return df

    def calculate_linearreg(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归（LINEARREG）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG指标的DataFrame
        """
        df = df.copy()
        df['LINEARREG'] = talib.LINEARREG(df['close'], timeperiod=timeperiod)
        return df

    def calculate_linearreg_angle(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归的角度（LINEARREG_ANGLE）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG_ANGLE指标的DataFrame
        """
        df = df.copy()
        df['LINEARREG_ANGLE'] = talib.LINEARREG_ANGLE(df['close'], timeperiod=timeperiod)
        return df

    def calculate_linearreg_intercept(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归截距（LINEARREG_INTERCEPT）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG_INTERCEPT指标的DataFrame
        """
        df = df.copy()
        df['LINEARREG_INTERCEPT'] = talib.LINEARREG_INTERCEPT(df['close'], timeperiod=timeperiod)
        return df

    def calculate_linearreg_slope(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归斜率指标（LINEARREG_SLOPE）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG_SLOPE指标的DataFrame
        """
        df = df.copy()
        df['LINEARREG_SLOPE'] = talib.LINEARREG_SLOPE(df['close'], timeperiod=timeperiod)
        return df

    def calculate_stddev(self, df: pd.DataFrame, timeperiod: int = 5, nbdev: int = 1) -> pd.DataFrame:
        """
        计算标准偏差（STDDEV）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为5
            nbdev: 偏差数量，默认为1
            
        Returns:
            DataFrame: 包含STDDEV指标的DataFrame
        """
        df = df.copy()
        df['STDDEV'] = talib.STDDEV(df['close'], timeperiod=timeperiod, nbdev=nbdev)
        return df

    def calculate_tsf(self, df: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算时间序列预测（TSF）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含TSF指标的DataFrame
        """
        df = df.copy()
        df['TSF'] = talib.TSF(df['close'], timeperiod=timeperiod)
        return df

    def calculate_var(self, df: pd.DataFrame, timeperiod: int = 5, nbdev: int = 1) -> pd.DataFrame:
        """
        计算方差（VAR）
        
        Args:
            df: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为5
            nbdev: 偏差数量，默认为1
            
        Returns:
            DataFrame: 包含VAR指标的DataFrame
        """
        df = df.copy()
        df['VAR'] = talib.VAR(df['close'], timeperiod=timeperiod, nbdev=nbdev)
        return df