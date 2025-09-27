<template>
  <div class="tradingview-chart-container">
    <div class="header">
      <h2 class="title">📊 Real Stock Data Chart</h2>
      <div class="server-status" :class="serverStatus.class">
        {{ serverStatus.text }}
      </div>
    </div>
    
    <div class="controls">
      <div class="control-group">
        <label>股票代码:</label>
        <select v-model="selectedSymbol" @change="changeSymbol" class="symbol-selector" :disabled="loadingStocks">
          <template v-if="loadingStocks">
            <option value="">加载中...</option>
          </template>
          <template v-else-if="stocksList.length > 0">
            <optgroup label="A股股票">
              <option v-for="stock in stocksList" :key="stock.symbol" :value="stock.symbol">
                {{ stock.description }} ({{ stock.real_symbol }})
              </option>
            </optgroup>
          </template>
          <template v-else>
            <option value="">暂无数据</option>
          </template>
        </select>
      </div>
      
      <div class="control-group">
        <label>时间周期:</label>
        <select v-model="selectedInterval" @change="changeInterval" class="interval-selector">
          <option value="1D">日线</option>
          <option value="1W">周线</option>
          <option value="1M">月线</option>
        </select>
      </div>
      
      <div class="control-group">
        <button @click="refreshData" class="refresh-btn" :disabled="!serverConnected">
          🔄 刷新数据
        </button>
        <button @click="checkServerStatus" class="status-btn">
          📡 检查状态
        </button>
      </div>
    </div>

    <div class="data-info" v-if="dataInfo.visible">
      <div class="info-item">
        <span class="label">数据源:</span>
        <span class="value">QData (AkShare)</span>
      </div>
      <div class="info-item">
        <span class="label">最后更新:</span>
        <span class="value">{{ dataInfo.lastUpdate }}</span>
      </div>
      <div class="info-item">
        <span class="label">数据点数:</span>
        <span class="value">{{ dataInfo.dataPoints }}</span>
      </div>
    </div>
    
    <div id="tv_chart_container_qdata" ref="chartContainer"></div>
    
    <div v-if="!serverConnected" class="server-warning">
      <div class="warning-content">
        <h3>⚠️ 服务器未连接</h3>
        <p>请启动数据服务器:</p>
        <div class="command-box">
          <code>python data_server/qdata_udf_server.py</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';

let widget = null;
const chartContainer = ref(null);
const selectedSymbol = ref('');
const selectedInterval = ref('1D');
const serverConnected = ref(false);
const serverInfo = ref({});
const error = ref('');
const dataInfo = ref({
  visible: false,
  lastUpdate: '',
  dataPoints: 0
});
const stocksList = ref([]);
const loadingStocks = ref(false);

// 服务器状态计算属性
const serverStatus = computed(() => {
  if (serverConnected.value) {
    return {
      text: `✅ 服务器在线 (${serverInfo.value.available_stocks || 0} 只股票)`,
      class: 'online'
    };
  } else {
    return {
      text: '❌ 服务器离线',
      class: 'offline'
    };
  }
});

// 检查服务器连接状态
const checkServerConnection = async () => {
  try {
    const response = await fetch('http://localhost:8080/status');
    if (response.ok) {
      const status = await response.json();
      serverConnected.value = true;
      serverInfo.value = status;
      error.value = '';
      // 如果已连接且股票列表为空，则获取股票列表
      if (stocksList.value.length === 0) {
        await fetchStocksList();
      }
    } else {
      serverConnected.value = false;
    }
  } catch (e) {
    serverConnected.value = false;
  }
};

// 获取股票列表
const fetchStocksList = async () => {
  loadingStocks.value = true;
  try {
    const response = await fetch('http://localhost:8080/stocks');
    if (response.ok) {
      const data = await response.json();
      if (data.s === 'ok' && data.data && data.data.length > 0) {
        stocksList.value = data.data;
        // 设置默认选中第一个股票
        if (!selectedSymbol.value && stocksList.value.length > 0) {
          selectedSymbol.value = stocksList.value[0].symbol;
        }
      }
    }
  } catch (e) {
    console.error('获取股票列表失败:', e);
  } finally {
    loadingStocks.value = false;
  }
};

// 检查服务器状态
const checkServerStatus = async () => {
  await checkServerConnection();
  if (serverConnected.value) {
    alert(`服务器状态：
✅ QData 已初始化: ${serverInfo.value.qdata_initialized ? '是' : '否'}
📊 可用股票数量: ${serverInfo.value.available_stocks}
💾 缓存数据数量: ${serverInfo.value.cache_size}`);
  }
};

// 加载 TradingView 库文件
const loadTradingViewLibraries = () => {
  return new Promise((resolve, reject) => {
    if (window.TradingView && window.Datafeeds) {
      resolve();
      return;
    }

    const createScript = (src) => {
      return new Promise((scriptResolve, scriptReject) => {
        const script = document.createElement('script');
        script.src = src;
        script.type = 'text/javascript';
        script.onload = scriptResolve;
        script.onerror = scriptReject;
        document.head.appendChild(script);
      });
    };

    Promise.all([
      createScript('/charting_library/charting_library.standalone.js'),
      createScript('/datafeeds/udf/dist/bundle.js')
    ])
      .then(resolve)
      .catch(reject);
  });
};

// 创建自定义数据源
const createQDataDatafeed = () => {
  return {
    onReady: (callback) => {
      setTimeout(() => callback({
        exchanges: [
          { value: 'SSE', name: 'Shanghai Stock Exchange', desc: '上海证券交易所' }
        ],
        symbols_types: [
          { name: 'Stock', value: 'stock' },
          { name: 'ETF', value: 'etf' }
        ],
        supported_resolutions: ['1', '5', '15', '30', '60', 'D', 'W', 'M']
      }), 0);
    },

    searchSymbols: (userInput, exchange, symbolType, onResultReadyCallback) => {
      fetch(`http://localhost:8080/search?query=${encodeURIComponent(userInput)}&limit=10`)
        .then(response => response.json())
        .then(data => onResultReadyCallback(data))
        .catch(error => onResultReadyCallback([]));
    },

    resolveSymbol: (symbolName, onSymbolResolvedCallback, onResolveErrorCallback) => {
      fetch(`http://localhost:8080/symbols?symbol=${encodeURIComponent(symbolName)}`)
        .then(response => response.json())
        .then(symbolInfo => {
          if (symbolInfo.name) {
            const symbol = {
              ticker: symbolInfo.name,
              name: symbolInfo.name,
              description: symbolInfo.description || symbolInfo.name,
              type: 'stock',
              session: '0930-1500',
              timezone: 'Asia/Shanghai',
              exchange: symbolInfo['exchange-traded'] || 'SSE',
              minmov: 1,
              pricescale: 100,
              has_intraday: false,
              has_no_volume: false,
              has_weekly_and_monthly: true,
              supported_resolutions: ['D'],
              volume_precision: 0,
              data_status: 'streaming'
            };
            setTimeout(() => onSymbolResolvedCallback(symbol), 0);
          } else {
            onResolveErrorCallback('Symbol not found');
          }
        })
        .catch(error => onResolveErrorCallback('Network error'));
    },

    getBars: (symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) => {
      const { from, to, firstDataRequest } = periodParams;
      const url = `http://localhost:8080/history?symbol=${encodeURIComponent(symbolInfo.ticker)}&resolution=${resolution}&from=${from}&to=${to}`;
      
      fetch(url)
        .then(response => response.json())
        .then(data => {
          if (data.s === 'ok' && data.t && data.t.length > 0) {
            const bars = [];
            for (let i = 0; i < data.t.length; i++) {
              bars.push({
                time: data.t[i] * 1000,
                low: data.l[i],
                high: data.h[i],
                open: data.o[i],
                close: data.c[i],
                volume: data.v[i]
              });
            }
            
            dataInfo.value = {
              visible: true,
              lastUpdate: new Date().toLocaleString(),
              dataPoints: bars.length
            };
            
            onHistoryCallback(bars, { noData: false });
          } else {
            dataInfo.value.visible = false;
            onHistoryCallback([], { noData: true });
          }
        })
        .catch(error => {
          dataInfo.value.visible = false;
          onErrorCallback('Network error');
        });
    },

    subscribeBars: (symbolInfo, resolution, onRealtimeCallback, subscriberUID) => {
      // 实时数据订阅
    },

    unsubscribeBars: (subscriberUID) => {
      // 取消实时数据订阅
    }
  };
};

// 初始化 TradingView 图表
const initTradingViewChart = async () => {
  try {
    await loadTradingViewLibraries();
    await checkServerConnection();
    
    if (!chartContainer.value) {
      return;
    }

    if (widget) {
      widget.remove();
      widget = null;
    }

    widget = new TradingView.widget({
      fullscreen: false,
      width: '100%',
      height: 600,
      symbol: selectedSymbol.value,
      interval: selectedInterval.value,
      container: 'tv_chart_container_qdata',
      datafeed: createQDataDatafeed(),
      library_path: '/charting_library/',
      locale: 'zh',
      disabled_features: [
        'use_localstorage_for_settings',
        'volume_force_overlay'
      ],
      enabled_features: [
        'study_templates'
      ],
      theme: 'light',
      debug: false
    });

    widget.onChartReady(() => {
      console.log('QData图表初始化完成');
    });

  } catch (error) {
    console.error('初始化图表失败:', error);
  }
};

// 切换股票代码
const changeSymbol = () => {
  if (widget && serverConnected.value) {
    widget.setSymbol(selectedSymbol.value, selectedInterval.value);
  }
};

// 切换时间间隔
const changeInterval = () => {
  if (widget && serverConnected.value) {
    widget.setSymbol(selectedSymbol.value, selectedInterval.value);
  }
};

// 刷新数据
const refreshData = () => {
  if (widget && serverConnected.value) {
    initTradingViewChart();
  }
};

// 组件挂载
onMounted(() => {
  checkServerConnection();
  initTradingViewChart();
  const checkInterval = setInterval(checkServerConnection, 10000);
  onUnmounted(() => {
    clearInterval(checkInterval);
  });
});

// 组件卸载
onUnmounted(() => {
  if (widget) {
    widget.remove();
    widget = null;
  }
});
</script>

<style scoped>
.tradingview-chart-container {
  width: 100%;
  height: 100%;
  background: #f8f9fb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.server-status {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 14px;
}

.server-status.online {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.server-status.offline {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

.controls {
  display: flex;
  gap: 20px;
  padding: 20px 25px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
  align-items: center;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
}

.control-group label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.symbol-selector,
.interval-selector {
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.symbol-selector:hover,
.interval-selector:hover {
  border-color: #667eea;
}

.refresh-btn,
.status-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 22px;
}

.refresh-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.status-btn {
  background: #f5f5f5;
  color: #333;
  border: 2px solid #e0e0e0;
}

.data-info {
  display: flex;
  gap: 30px;
  padding: 15px 25px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.info-item .label {
  font-weight: 600;
  color: #666;
}

.info-item .value {
  color: #333;
  font-weight: 500;
}

#tv_chart_container_qdata {
  width: 100%;
  height: 600px;
  background: white;
}

.server-warning {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 1000;
  max-width: 500px;
  text-align: center;
}

.warning-content h3 {
  color: #f57c00;
  margin-bottom: 15px;
}

.command-box {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 15px;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  margin: 15px 0;
}
</style>