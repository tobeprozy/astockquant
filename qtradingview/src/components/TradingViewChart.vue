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
      createScript('/charting_library/charting_library.min.js'),
      createScript('/datafeeds/udf/dist/polyfills.js'),
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

    // 创建 TradingView 图表部件
    widget = new window.TradingView.widget({
      fullscreen: true,
      symbol: 'AAPL', // 默认股票代码
      interval: 'D', // 默认时间间隔（日线）
      container_id: 'tv_chart_container',
      
      // 数据馈送配置 - 修改为本地UDF服务器
      datafeed: new window.Datafeeds.UDFCompatibleDatafeed('http://localhost:8080'),
      library_path: '/charting_library/',
      locale: 'zh', // 使用中文界面
      
      // 功能配置
      disabled_features: ['use_localstorage_for_settings'],
      enabled_features: ['study_templates'],
      
      // 禁用图表保存功能，使用本地服务器时不需要
      charts_storage_url: '',
      client_id: '',
      user_id: ''
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