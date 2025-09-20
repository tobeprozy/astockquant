<template>
  <div class="tradingview-chart-container">
    <div id="tv_chart_container" ref="chartContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

let widget = null;
const chartContainer = ref(null);

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
      createScript('/charting_library.min.js'),
      createScript('/udf/dist/polyfills.js'),
      createScript('/udf/dist/bundle.js')
    ])
      .then(resolve)
      .catch(reject);
  });
};

// 从URL获取参数的函数
const getParameterByName = (name) => {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
  var results = regex.exec(location.search);
  return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
};

// 初始化 TradingView 图表
const initTradingViewChart = async () => {
  try {
    await loadTradingViewLibraries();
    
    if (!chartContainer.value) {
      console.error('Chart container not found');
      return;
    }

    // 获取URL参数
    const symbol = getParameterByName('symbol') || 'AAPL';
    const interval = getParameterByName('interval') || 'D';
    const lang = getParameterByName('lang') || 'zh';
    const theme = getParameterByName('theme') || 'light';

    // 创建 TradingView 图表部件
    widget = new window.TradingView.widget({
      // debug: true, // 取消注释以在控制台中查看库错误和警告
      fullscreen: true,
      symbol: symbol,
      interval: interval,
      container_id: 'tv_chart_container',
      
      // 数据馈送配置
      datafeed: new window.Datafeeds.UDFCompatibleDatafeed('https://demo_feed.tradingview.com'),
      library_path: '/',
      locale: lang,
      theme: theme,
      
      // 功能配置
      disabled_features: ['use_localstorage_for_settings'],
      enabled_features: ['study_templates'],
      
      // 保存/加载图表配置
      charts_storage_url: 'http://saveload.tradingview.com',
      charts_storage_api_version: '1.1',
      client_id: 'tradingview.com',
      user_id: 'public_user_id'
    });

  } catch (error) {
    console.error('Failed to initialize TradingView chart:', error);
  }
};

// 组件挂载时初始化图表
onMounted(() => {
  initTradingViewChart();
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
}

#tv_chart_container {
  width: 100%;
  height: 100vh;
  margin: 0;
}

/* 适配移动设备 */
@media (max-width: 768px) {
  #tv_chart_container {
    height: calc(100vh - 40px);
  }
}
</style>