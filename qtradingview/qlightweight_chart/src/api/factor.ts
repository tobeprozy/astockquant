// 模拟API调用，返回股票数据
export async function exec_sql(params: { sql_command: string }) {
  // 模拟异步延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 生成模拟股票数据
  const mockData = generateMockStockData()
  
  return {
    res: mockData.join('\n')
  }
}

function generateMockStockData() {
  const data = []
  const startDate = new Date('2024-01-01')
  let basePrice = 10.0
  
  for (let i = 0; i < 100; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)
    
    // 生成随机价格变动
    const volatility = 0.02
    const change = (Math.random() - 0.5) * volatility
    basePrice = Math.max(basePrice + change, 1.0)
    
    const open = basePrice + (Math.random() - 0.5) * 0.1
    const close = basePrice + (Math.random() - 0.5) * 0.1
    const high = Math.max(open, close) + Math.random() * 0.1
    const low = Math.min(open, close) - Math.random() * 0.1
    const volume = Math.floor(Math.random() * 1000000) + 100000
    
    data.push(JSON.stringify({
      date: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume: volume,
      dtprice: parseFloat(((open + high + low + close) / 4).toFixed(2))
    }))
  }
  
  return data
}