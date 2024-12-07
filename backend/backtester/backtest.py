class Backtester:
    def __init__(self, strategy, historical_data):
        self.strategy = strategy
        self.historical_data = historical_data

    def run(self):
        # 示例回测逻辑
        results = []
        for data in self.historical_data:
            signal = self.strategy.generate_signal(data)  # 假设策略有一个 generate_signal 方法
            results.append(signal)
        return results
