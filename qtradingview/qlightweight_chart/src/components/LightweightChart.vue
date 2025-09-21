<template>
  <div class="p-4">
    <div ref="chartContainer" class="chart-container"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { createChart } from 'lightweight-charts'
import { exec_sql } from '@/api/factor'

const chartContainer = ref<HTMLElement>()
const data_list = ref<any>([])
const line_list = ref<any>([])
const loading = ref(true)

const option = ref({
  localization: {
    dateFormat: 'yyyy-MM-dd',
  },
  layout: {
    background: { type: 'solid', color: '#ffffff' },
    textColor: '#333',
  },
  grid: {
    vertLines: { color: '#e0e0e0' },
    horzLines: { color: '#e0e0e0' },
  },
})

let chart: any = null

async function handle_sql() {
  try {
    loading.value = true
    const res = await exec_sql({
      sql_command: `SELECT * FROM stock_base.tu_daily WHERE code='000001' order by date format JSONEachRow`,
    })
    
    const dataList = !res.res ? [] : res.res.split('\n')
    dataList.forEach((item: string) => {
      if (!item.trim()) return
      
      const list = JSON.parse(item)
      const obj = {
        time: list.date,
        open: list.open,
        high: list.high,
        low: list.low,
        close: list.close,
        volume: Number(list.volume),
        turnover: ((list.open + list.high + list.low + list.close) / 4) * list.volume,
      }
      data_list.value.push(obj)
      line_list.value.push({
        time: list.date,
        value: Number(list.dtprice),
      })
    })

    if (chartContainer.value) {
      chart = createChart(chartContainer.value, option.value)
      
      // 蜡烛图
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      })
      candlestickSeries.setData(data_list.value)


      chart.timeScale().fitContent()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  handle_sql()
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: calc(100vh - 200px);
  min-height: 400px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  font-size: 16px;
  color: #666;
}
</style>