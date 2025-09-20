# qtradingview

基于Vue 3和TradingView图表库的股票交易视图组件。

## 技术栈
- Vue 3 (^3.5.21)
- Vite (^7.1.6)
- TradingView Charting Library

## 开发环境
- node --version v22.19.0
- npm --version 10.9.3

## 安装步骤

1. 安装依赖
```bash
npm install
```
2. 启动开发服务器
```bash
npm run dev
```
3. 构建生产版本
```bash
npm run build
```
4. 预览生产版本
```bash
npm run preview
```

## 项目结构
- `src/` - 源代码目录
  - `components/` - Vue组件
  - `main.js` - 应用入口文件
- `public/` - 静态资源和TradingView图表库

## 功能特点
- TradingView图表集成
- Vue 3组件封装
- 响应式界面

## 注意事项
- 确保TradingView图表库文件正确放置在`public/charting_library/`目录下
