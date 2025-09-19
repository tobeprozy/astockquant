from abc import ABC, abstractmethod
import pandas as pd


class IndicatorCalculator(ABC):
    """
    指标计算器的抽象基类
    所有指标计算适配器都需要实现这个接口
    """
    
    
    def calculate_ma(self, data: pd.DataFrame, timeperiod: int = 5) -> pd.DataFrame:
        """
        计算移动平均线（MA）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: MA的周期，默认为5
            
        Returns:
            DataFrame: 包含MA指标的DataFrame
        """
        pass
    
    
    def calculate_ema(self, data: pd.DataFrame, timeperiod: int = 5) -> pd.DataFrame:
        """
        计算指数移动平均线（EMA）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: EMA的周期，默认为5
            
        Returns:
            DataFrame: 包含EMA指标的DataFrame
        """
        pass
    
    
    def calculate_rsi(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算相对强弱指数（RSI）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: RSI的周期，默认为14
            
        Returns:
            DataFrame: 包含RSI指标的DataFrame
        """
        pass
    
    
    def calculate_bbands(self, data: pd.DataFrame, timeperiod: int = 5, nbdevup: int = 2, nbdevdn: int = 2) -> pd.DataFrame:
        """
        计算布林带（Bollinger Bands）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 布林带的周期，默认为5
            nbdevup: 上轨偏差，默认为2
            nbdevdn: 下轨偏差，默认为2
            
        Returns:
            DataFrame: 包含布林带指标的DataFrame
        """
        pass
    
    
    def calculate_macd(self, data: pd.DataFrame, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> pd.DataFrame:
        """
        计算MACD指标
        
        Args:
            data: 包含股票数据的DataFrame
            fastperiod: 快速EMA周期，默认为12
            slowperiod: 慢速EMA周期，默认为26
            signalperiod: 信号线周期，默认为9
            
        Returns:
            DataFrame: 包含MACD指标的DataFrame
        """
        pass
    
    # 波动率指标
    
    def calculate_atr(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算平均真实波动幅度（ATR）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含ATR指标的DataFrame
        """
        pass
        
    
    def calculate_natr(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算归一化波动幅度均值（NATR）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含NATR指标的DataFrame
        """
        pass
        
    
    def calculate_trange(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算真正的范围（TRANGE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含TRANGE指标的DataFrame
        """
        pass
    
    # 价格指标
    
    def calculate_avgprice(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算平均价格函数（AVGPRICE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含AVGPRICE指标的DataFrame
        """
        pass
        
    
    def calculate_medprice(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算中位数价格（MEDPRICE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含MEDPRICE指标的DataFrame
        """
        pass
        
    
    def calculate_typprice(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算代表性价格（TYPPRICE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含TYPPRICE指标的DataFrame
        """
        pass
        
    
    def calculate_wclprice(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算加权收盘价（WCLPRICE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含WCLPRICE指标的DataFrame
        """
        pass
    
    # 周期指标
    
    def calculate_ht_dcperiod(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-主导周期（HT_DCPERIOD）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_DCPERIOD指标的DataFrame
        """
        pass
        
    
    def calculate_ht_dcphase(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-主导相位（HT_DCPHASE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_DCPHASE指标的DataFrame
        """
        pass
        
    
    def calculate_ht_phasor(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-相量分量（HT_PHASOR）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_PHASOR指标的DataFrame
        """
        pass
        
    
    def calculate_ht_sine(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-正弦波（HT_SINE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_SINE指标的DataFrame
        """
        pass
        
    
    def calculate_ht_trendline(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-趋势线（HT_TRENDLINE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_TRENDLINE指标的DataFrame
        """
        pass
        
    
    def calculate_ht_trendmode(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算希尔伯特变换-趋势模式（HT_TRENDMODE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含HT_TRENDMODE指标的DataFrame
        """
        pass
    
    # K线形态指标
    
    def calculate_cdl2crows(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算两只乌鸦（CDL2CROWS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL2CROWS指标的DataFrame
        """
        pass
        
    
    def calculate_cdl3blackcrows(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三只乌鸦（CDL3BLACKCROWS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3BLACKCROWS指标的DataFrame
        """
        pass
        
    
    def calculate_cdl3inside(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三内部上涨和下跌（CDL3INSIDE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3INSIDE指标的DataFrame
        """
        pass
        
    
    def calculate_cdl3linestrike(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三线打击（CDL3LINESTRIKE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3LINESTRIKE指标的DataFrame
        """
        pass
        
    
    def calculate_cdl3outside(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三外部上涨和下跌（CDL3OUTSIDE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3OUTSIDE指标的DataFrame
        """
        pass
        
    
    def calculate_cdl3starsinsouth(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算南方三星（CDL3STARSINSOUTH）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3STARSINSOUTH指标的DataFrame
        """
        pass
        
    
    def calculate_cdl3whitesoldiers(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算白色三兵（CDL3WHITESOLDIERS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDL3WHITESOLDIERS指标的DataFrame
        """
        pass
        
    
    def calculate_cdlabandonedbaby(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算弃婴形态（CDLABANDONEDBABY）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLABANDONEDBABY指标的DataFrame
        """
        pass
        
    
    def calculate_cdlbelthold(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算捉腰带线（CDLBELTHOLD）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLBELTHOLD指标的DataFrame
        """
        pass
        
    
    def calculate_cdlbreakaway(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算脱离（CDLBREAKAWAY）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLBREAKAWAY指标的DataFrame
        """
        pass
        
    
    def calculate_cdlclosingmarubozu(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算收盘缺影线（CDLCLOSINGMARUBOZU）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLCLOSINGMARUBOZU指标的DataFrame
        """
        pass
        
    
    def calculate_cdlconcealbabyswallow(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算藏婴吞没（CDLCONCEALBABYSWALL）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLCONCEALBABYSWALL指标的DataFrame
        """
        pass
        
    
    def calculate_cdlcounterattack(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算反击线（CDLCOUNTERATTACK）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLCOUNTERATTACK指标的DataFrame
        """
        pass
        
    
    def calculate_cdldarkcloudcover(self, data: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算乌云压顶（CDLDARKCLOUDCOVER）
        
        Args:
            data: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLDARKCLOUDCOVER指标的DataFrame
        """
        pass
        
    
    def calculate_cdldoji(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算十字（CDLDOJI）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLDOJI指标的DataFrame
        """
        pass
        
    
    def calculate_cdldojistar(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算十字星（CDLDOJISTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLDOJISTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdlengulping(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算吞噬模式（CDLENGULFING）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLENGULFING指标的DataFrame
        """
        pass
        
    
    def calculate_cdleveningdojistar(self, data: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算十字暮星（CDLEVENINGDOJISTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLEVENINGDOJISTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdleveningstar(self, data: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算暮星（CDLEVENINGSTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLEVENINGSTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdlgapsidesidewhite(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算向上/下跳空并列阳线（CDLGAPSIDESIDEWHITE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLGAPSIDESIDEWHITE指标的DataFrame
        """
        pass
        
    
    def calculate_cdlhammer(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算锤头（CDLHAMMER）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHAMMER指标的DataFrame
        """
        pass
        
    
    def calculate_cdlhangingman(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算上吊线（CDLHANGINGMAN）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHANGINGMAN指标的DataFrame
        """
        pass
        
    
    def calculate_cdlharami(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算母子线（CDLHARAMI）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHARAMI指标的DataFrame
        """
        pass
        
    
    def calculate_cdlharamicross(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算十字孕线（CDLHARAMICROSS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHARAMICROSS指标的DataFrame
        """
        pass
        
    
    def calculate_cdlhighwave(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算风高浪大线（CDLHIGHWAVE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHIGHWAVE指标的DataFrame
        """
        pass
        
    
    def calculate_cdlhikkake(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算陷阱（CDLHIKKAKE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHIKKAKE指标的DataFrame
        """
        pass
        
    
    def calculate_cdlhikkakemod(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算修正陷阱（CDLHIKKAKEMOD）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHIKKAKEMOD指标的DataFrame
        """
        pass
        
    
    def calculate_cdlhomingpigeon(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算家鸽（CDLHOMINGPIGEON）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLHOMINGPIGEON指标的DataFrame
        """
        pass
        
    
    def calculate_cdlidentical3crows(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三胞胎乌鸦（CDLIDENTICAL3CROWS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLIDENTICAL3CROWS指标的DataFrame
        """
        pass
        
    
    def calculate_cdlinneck(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算颈内线（CDLINNECK）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLINNECK指标的DataFrame
        """
        pass
        
    
    def calculate_cdlinvertedhammer(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算倒锤头（CDLINVERTEDHAMMER）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLINVERTEDHAMMER指标的DataFrame
        """
        pass
        
    
    def calculate_cdlkicking(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算反冲形态（CDLKICKING）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLKICKING指标的DataFrame
        """
        pass
        
    
    def calculate_cdlkickingbylength(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算由较长缺影线决定的反冲形态（CDLKICKINGBYLENGTH）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLKICKINGBYLENGTH指标的DataFrame
        """
        pass
        
    
    def calculate_cdlladderbottom(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算梯底（CDLLADDERBOTTOM）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLLADDERBOTTOM指标的DataFrame
        """
        pass
        
    
    def calculate_cdllongleggeddoji(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算长脚十字（CDLLONGLEGGEDDOJI）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLLONGLEGGEDDOJI指标的DataFrame
        """
        pass
        
    
    def calculate_cdllongline(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算长蜡烛（CDLLONGLINE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLLONGLINE指标的DataFrame
        """
        pass
        
    
    def calculate_cdlmarubozu(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算光头光脚/缺影线（CDLMARUBOZU）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLMARUBOZU指标的DataFrame
        """
        pass
        
    
    def calculate_cdlmatchinglow(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算相同低价（CDLMATCHINGLOW）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLMATCHINGLOW指标的DataFrame
        """
        pass
        
    
    def calculate_cdlmathold(self, data: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算铺垫（CDLMATHOLD）
        
        Args:
            data: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLMATHOLD指标的DataFrame
        """
        pass
        
    
    def calculate_cdlmorningdojistar(self, data: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算十字晨星（CDLMORNINGDOJISTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLMORNINGDOJISTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdlmorningstar(self, data: pd.DataFrame, penetration: int = 0) -> pd.DataFrame:
        """
        计算晨星（CDLMORNINGSTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            penetration: 穿透比例，默认为0
            
        Returns:
            DataFrame: 包含CDLMORNINGSTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdlonneck(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算颈上线（CDLONNECK）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLONNECK指标的DataFrame
        """
        pass
        
    
    def calculate_cdlpiercing(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算刺透形态（CDLPIERCING）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLPIERCING指标的DataFrame
        """
        pass
        
    
    def calculate_cdlrickshawman(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算黄包车夫（CDLRICKSHAWMAN）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLRICKSHAWMAN指标的DataFrame
        """
        pass
        
    
    def calculate_cdlriselfall3methods(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算上升/下降三法（CDLRISEFALL3METHODS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLRISEFALL3METHODS指标的DataFrame
        """
        pass
        
    
    def calculate_cdlseparatinglines(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算分离线（CDLSEPARATINGLINES）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSEPARATINGLINES指标的DataFrame
        """
        pass
        
    
    def calculate_cdlshootingstar(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算射击之星（CDLSHOOTINGSTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSHOOTINGSTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdlshortline(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算短蜡烛（CDLSHORTLINE）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSHORTLINE指标的DataFrame
        """
        pass
        
    
    def calculate_cdlspinningtop(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算纺锤（CDLSPINNINGTOP）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSPINNINGTOP指标的DataFrame
        """
        pass
        
    
    def calculate_cdlstalledpattern(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算停顿形态（CDLSTALLEDPATTERN）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSTALLEDPATTERN指标的DataFrame
        """
        pass
        
    
    def calculate_cdlsticksandwich(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算条形三明治（CDLSTICKSANDWICH）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLSTICKSANDWICH指标的DataFrame
        """
        pass
        
    
    def calculate_cdltaburi(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算探水竿（CDLTAKURI）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTAKURI指标的DataFrame
        """
        pass
        
    
    def calculate_cdltasukigap(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算跳空并列阴阳线（CDLTASUKIGAP）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTASUKIGAP指标的DataFrame
        """
        pass
        
    
    def calculate_cdlthrusting(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算插入（CDLTHRUSTING）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTHRUSTING指标的DataFrame
        """
        pass
        
    
    def calculate_cdltristart(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算三星（CDLTRISTAR）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLTRISTAR指标的DataFrame
        """
        pass
        
    
    def calculate_cdlunique3river(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算奇特三河床（CDLUNIQUE3RIVER）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLUNIQUE3RIVER指标的DataFrame
        """
        pass
        
    
    def calculate_cdlupsidegap2crows(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算向上跳空的两只乌鸦（CDLUPSIDEGAP2CROWS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLUPSIDEGAP2CROWS指标的DataFrame
        """
        pass
        
    
    def calculate_cdlxsidegap3methods(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算上升/下降跳空三法（CDLXSIDEGAP3METHODS）
        
        Args:
            data: 包含股票数据的DataFrame
            
        Returns:
            DataFrame: 包含CDLXSIDEGAP3METHODS指标的DataFrame
        """
        pass
    
    # 统计学指标
    
    def calculate_beta(self, data: pd.DataFrame, timeperiod: int = 5) -> pd.DataFrame:
        """
        计算β系数（BETA）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为5
            
        Returns:
            DataFrame: 包含BETA指标的DataFrame
        """
        pass
        
    
    def calculate_correl(self, data: pd.DataFrame, timeperiod: int = 30) -> pd.DataFrame:
        """
        计算皮尔逊相关系数（CORREL）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为30
            
        Returns:
            DataFrame: 包含CORREL指标的DataFrame
        """
        pass
        
    
    def calculate_linearreg(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归（LINEARREG）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG指标的DataFrame
        """
        pass
        
    
    def calculate_linearreg_angle(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归的角度（LINEARREG_ANGLE）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG_ANGLE指标的DataFrame
        """
        pass
        
    
    def calculate_linearreg_intercept(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归截距（LINEARREG_INTERCEPT）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG_INTERCEPT指标的DataFrame
        """
        pass
        
    
    def calculate_linearreg_slope(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算线性回归斜率指标（LINEARREG_SLOPE）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含LINEARREG_SLOPE指标的DataFrame
        """
        pass
        
    
    def calculate_stddev(self, data: pd.DataFrame, timeperiod: int = 5, nbdev: int = 1) -> pd.DataFrame:
        """
        计算标准偏差（STDDEV）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为5
            nbdev: 偏差数量，默认为1
            
        Returns:
            DataFrame: 包含STDDEV指标的DataFrame
        """
        pass
        
    
    def calculate_tsf(self, data: pd.DataFrame, timeperiod: int = 14) -> pd.DataFrame:
        """
        计算时间序列预测（TSF）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为14
            
        Returns:
            DataFrame: 包含TSF指标的DataFrame
        """
        pass
        
    
    def calculate_var(self, data: pd.DataFrame, timeperiod: int = 5, nbdev: int = 1) -> pd.DataFrame:
        """
        计算方差（VAR）
        
        Args:
            data: 包含股票数据的DataFrame
            timeperiod: 计算周期，默认为5
            nbdev: 偏差数量，默认为1
            
        Returns:
            DataFrame: 包含VAR指标的DataFrame
        """
        pass
    
    def prepare_df(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        准备数据，确保数据格式正确
        
        Args:
            data: 原始数据DataFrame
            
        Returns:
            DataFrame: 格式化后的DataFrame
        """
        # 确保必要的列存在
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        if not required_columns.issubset(data.columns):
            # 尝试进行列名映射
            column_mapping = {
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            }
            data = data.rename(columns=column_mapping)
        
        return data