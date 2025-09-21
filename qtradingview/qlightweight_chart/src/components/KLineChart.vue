<template>
  <div class="p-4">
    <div id="kline-chart" class="chart-container"></div>
    <div v-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script lang="ts" setup>
import { onUnmounted, ref, onMounted } from 'vue'
import { init, dispose } from 'klinecharts'
import { exec_sql } from '@/api/factor'

const data_list = ref<any>([])
const loading = ref(true)

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
        timestamp: new Date(list.date).getTime(),
        open: list.open,
        high: list.high,
        low: list.low,
        close: list.close,
        volume: Number(list.volume),
        turnover: ((list.open + list.high + list.low + list.close) / 4) * list.volume,
      }
      data_list.value.push(obj)
    })

    if (data_list.value.length > 0) {
      chart = init('kline-chart', {
        styles: {
          grid: {
            show: true,
            horizontal: {
              show: true,
              color: '#e0e0e0',
              size: 1,
              style: 'dashed'
            },
            vertical: {
              show: true,
              color: '#e0e0e0',
              size: 1,
              style: 'dashed'
            }
          },
          candle: {
            margin: {
              top: 0.2,
              bottom: 0.1
            },
            type: 'candle_solid',
            bar: {
              upColor: '#26a69a',
              downColor: '#ef5350',
              noChangeColor: '#888888'
            },
            tooltip: {
              showRule: 'always',
              showType: 'standard'
            }
          }
        }
      })
      
      chart.applyNewData(data_list.value)
      
      // 创建技术指标
      chart.createIndicator('VOL', false, { id: 'candle_pane' })
      chart.createIndicator('MACD', false, { height: 100 })
      
      // 设置图表样式
      chart.setPriceVolumePrecision(2, 0)
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
  dispose('kline-chart')
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