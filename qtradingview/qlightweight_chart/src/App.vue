<template>
  <div id="app">
    <div class="tab-container">
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'lightweight' }"
        @click="activeTab = 'lightweight'"
      >
        Lightweight Charts
      </button>
      <button 
        class="tab-button" 
        :class="{ active: activeTab === 'klinecharts' }"
        @click="activeTab = 'klinecharts'"
      >
        KLineCharts
      </button>
    </div>
    
    <div v-if="activeTab === 'lightweight'" class="chart-container">
      <div class="chart-title">Lightweight Charts - 股票K线图</div>
      <LightweightChart />
    </div>
    
    <div v-if="activeTab === 'klinecharts'" class="chart-container">
      <div class="chart-title">KLineCharts - 专业K线图</div>
      <KLineChart />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LightweightChart from './components/LightweightChart.vue'
import KLineChart from './components/KLineChart.vue'

const activeTab = ref('lightweight')
</script>