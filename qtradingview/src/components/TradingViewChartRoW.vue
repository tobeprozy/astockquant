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
      createScript('/charting_library/charting_library.standalone.js'),
      createScript('/datafeeds/udf/dist/bundle.js')
    ])
      .then(resolve)
      .catch(reject);
  });
};

// 初始化 TradingView 图表
const initTradingViewChart = async () => {
  try {
    await loadTradingViewLibraries();
    
    if (!chartContainer.value) {
      console.error('Chart container not found');
      return;
    }

    // 确保容器元素存在
    if (!chartContainer.value) {
      console.error('Chart container not found');
      return;
    }

    // 创建 TradingView 图表部件
    widget = new TradingView.widget({
      fullscreen: true,
      symbol: 'AAPL', // 默认股票代码
      interval: '1D', // 默认时间间隔（日线）
      container: 'tv_chart_container',
      
      // 数据馈送配置
      datafeed: new Datafeeds.UDFCompatibleDatafeed('https://demo-feed-data.tradingview.com'),
      library_path: '/charting_library/',
      locale: 'zh', // 使用中文界面
      
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
  height: 800px;
}
</style>