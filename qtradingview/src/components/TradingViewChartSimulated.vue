<template>
  <div class="tradingview-chart-container">
    <div class="controls">
      <select v-model="selectedSymbol" @change="changeSymbol" class="symbol-selector">
        <option value="AAPL">Apple (AAPL)</option>
        <option value="MSFT">Microsoft (MSFT)</option>
        <option value="GOOG">Google (GOOG)</option>
        <option value="TSLA">Tesla (TSLA)</option>
        <option value="BABA">Alibaba (BABA)</option>
      </select>
      <select v-model="selectedInterval" @change="changeInterval" class="interval-selector">
        <option value="1D">Daily</option>
        <option value="1W">Weekly</option>
        <option value="1M">Monthly</option>
      </select>
      <button @click="refreshData" class="refresh-btn">Refresh Data</button>
    </div>
    <div id="tv_chart_container_sim" ref="chartContainer"></div>
    <div v-if="!serverConnected" class="server-warning">
      ⚠️ Python data server not connected. Please run: python tests/enhanced_udf_server.py
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

let widget = null;
const chartContainer = ref(null);
const selectedSymbol = ref('AAPL');
const selectedInterval = ref('1D');
const serverConnected = ref(false);

// 检查服务器连接状态
const checkServerConnection = async () => {
  try {
    const response = await fetch('http://localhost:8080/config');
    serverConnected.value = response.ok;
  } catch (error) {
    serverConnected.value = false;
  }
};

// 加载 TradingView 库文件
const loadTradingViewLibraries = () => {
  return new Promise((resolve, reject) => {
    // 检查是否已经加载了 TradingView 库
    if (window.TradingView && window.Datafeeds) {
      resolve();
      return;
    }

    // 创建 script 元素的函数
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

    // 依次加载所需的脚本文件
    Promise.all([
      createScript('/charting_library/charting_library.standalone.js'),
      createScript('/datafeeds/udf/dist/bundle.js')
    ])
      .then(resolve)
      .catch(reject);
  });
};

// 创建自定义数据源
const createCustomDatafeed = () => {
  return {
    onReady: (callback) => {
      console.log('[onReady]: Method called');
      setTimeout(() => callback({
        exchanges: [
          { value: 'Simulated', name: 'Simulated Exchange', desc: 'Simulated Stock Exchange' }
        ],
        symbols_types: [
          { name: 'Stock', value: 'stock' }
        ],
        supported_resolutions: ['1', '5', '15', '30', '60', 'D', 'W', 'M']
      }), 0);
    },

    searchSymbols: (userInput, exchange, symbolType, onResultReadyCallback) => {
      console.log('[searchSymbols]: Method called');
      fetch(`http://localhost:8080/search?query=${userInput}&limit=10`)
        .then(response => response.json())
        .then(data => {
          onResultReadyCallback(data);
        })
        .catch(error => {
          console.error('Search symbols error:', error);
          onResultReadyCallback([]);
        });
    },

    resolveSymbol: (symbolName, onSymbolResolvedCallback, onResolveErrorCallback) => {
      console.log('[resolveSymbol]: Method called', symbolName);
      
      fetch(`http://localhost:8080/symbols?symbol=${symbolName}`)
        .then(response => response.json())
        .then(symbolInfo => {
          if (symbolInfo.name) {
            const symbol = {
              ticker: symbolInfo.name,
              name: symbolInfo.name,
              description: symbolInfo.description,
              type: 'stock',
              session: '0930-1600',
              timezone: 'America/New_York',
              exchange: 'Simulated',
              minmov: 1,
              pricescale: 100,
              has_intraday: true,
              has_no_volume: false,
              has_weekly_and_monthly: true,
              supported_resolutions: ['1', '5', '15', '30', '60', 'D', 'W', 'M'],
              volume_precision: 0,
              data_status: 'streaming'
            };
            setTimeout(() => onSymbolResolvedCallback(symbol), 0);
          } else {
            onResolveErrorCallback('Symbol not found');
          }
        })
        .catch(error => {
          console.error('Resolve symbol error:', error);
          onResolveErrorCallback('Network error');
        });
    },

    getBars: (symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) => {
      console.log('[getBars]: Method called', symbolInfo, resolution, periodParams);
      
      const { from, to, firstDataRequest } = periodParams;
      
      fetch(`http://localhost:8080/history?symbol=${symbolInfo.ticker}&resolution=${resolution}&from=${from}&to=${to}`)
        .then(response => response.json())
        .then(data => {
          if (data.s === 'ok') {
            const bars = [];
            for (let i = 0; i < data.t.length; i++) {
              bars.push({
                time: data.t[i] * 1000, // TradingView expects milliseconds
                low: data.l[i],
                high: data.h[i],
                open: data.o[i],
                close: data.c[i],
                volume: data.v[i]
              });
            }
            onHistoryCallback(bars, { noData: false });
          } else {
            onHistoryCallback([], { noData: true });
          }
        })
        .catch(error => {
          console.error('Get bars error:', error);
          onErrorCallback('Network error');
        });
    },

    subscribeBars: (symbolInfo, resolution, onRealtimeCallback, subscriberUID, onResetCacheNeededCallback) => {
      console.log('[subscribeBars]: Method called with subscriberUID:', subscriberUID);
      // 这里可以实现实时数据订阅
    },

    unsubscribeBars: (subscriberUID) => {
      console.log('[unsubscribeBars]: Method called with subscriberUID:', subscriberUID);
      // 这里可以实现取消实时数据订阅
    }
  };
};

// 初始化 TradingView 图表
const initTradingViewChart = async () => {
  try {
    await loadTradingViewLibraries();
    await checkServerConnection();
    
    if (!chartContainer.value) {
      console.error('Chart container not found');
      return;
    }

    // 销毁现有的图表
    if (widget) {
      widget.remove();
      widget = null;
    }

    // 创建 TradingView 图表部件
    widget = new TradingView.widget({
      fullscreen: false,
      width: '100%',
      height: 600,
      symbol: selectedSymbol.value,
      interval: selectedInterval.value,
      container: 'tv_chart_container_sim',
      
      // 使用自定义数据馈送
      datafeed: createCustomDatafeed(),
      library_path: '/charting_library/',
      locale: 'zh', // 使用中文界面
      
      // 功能配置
      disabled_features: [
        'use_localstorage_for_settings',
        'volume_force_overlay',
        'create_volume_indicator_by_default'
      ],
      enabled_features: [
        'study_templates',
        'side_toolbar_in_fullscreen_mode'
      ],
      
      // 图表配置
      charts_storage_url: 'http://saveload.tradingview.com',
      charts_storage_api_version: '1.1',
      client_id: 'tradingview.com',
      user_id: 'public_user_id',
      
      // 自定义样式
      custom_css_url: '/tradingview-chart.css',
      
      // 主题
      theme: 'light',
      
      // 工具栏
      toolbar_bg: '#f1f3f6',
      
      // 调试模式
      debug: false
    });

    // 图表准备就绪后的回调
    widget.onChartReady(() => {
      console.log('Chart is ready');
      // 可以在这里添加自定义指标或进行其他配置
    });

  } catch (error) {
    console.error('Failed to initialize TradingView chart:', error);
  }
};

// 切换股票代码
const changeSymbol = () => {
  if (widget) {
    widget.setSymbol(selectedSymbol.value, selectedInterval.value);
  }
};

// 切换时间间隔
const changeInterval = () => {
  if (widget) {
    widget.setSymbol(selectedSymbol.value, selectedInterval.value);
  }
};

// 刷新数据
const refreshData = () => {
  if (widget) {
    // 重新初始化图表以刷新数据
    initTradingViewChart();
  }
};

// 组件挂载时初始化图表
onMounted(() => {
  initTradingViewChart();
  
  // 定期检查服务器连接状态
  const checkInterval = setInterval(checkServerConnection, 5000);
  
  onUnmounted(() => {
    clearInterval(checkInterval);
  });
});

// 组件卸载时清理图表
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
  position: relative;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.controls {
  display: flex;
  gap: 10px;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  align-items: center;
  flex-wrap: wrap;
}

.symbol-selector,
.interval-selector {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.symbol-selector:hover,
.interval-selector:hover {
  background: white;
  transform: translateY(-1px);
}

.refresh-btn {
  padding: 8px 16px;
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  background: transparent;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
  transform: translateY(-1px);
}

#tv_chart_container_sim {
  width: 100%;
  height: 600px;
  background: white;
}

.server-warning {
  position: absolute;
  top: 70px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff3cd;
  color: #856404;
  padding: 10px 20px;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    gap: 8px;
  }
  
  .symbol-selector,
  .interval-selector,
  .refresh-btn {
    width: 100%;
  }
  
  #tv_chart_container_sim {
    height: 400px;
  }
}
</style>