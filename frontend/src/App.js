import React from 'react';
import axios from 'axios';

class App extends React.Component {
  state = {
    staticData: {},
    realTimeData: {}
  };

  componentDidMount() {
    this.fetchStaticData();
    this.fetchRealTimeData();
  }

  fetchStaticData = async () => {
    const response = await axios.get('/api/static-data');
    this.setState({ staticData: response.data });
  };

  fetchRealTimeData = async () => {
    const response = await axios.get('/api/real-time-data');
    this.setState({ realTimeData: response.data });
  };

  render() {
    return (
      <div>
        <h1>Stock Data</h1>
        <h2>Static Data</h2>
        <pre>{JSON.stringify(this.state.staticData, null, 2)}</pre>
        <h2>Real-Time Data</h2>
        <pre>{JSON.stringify(this.state.realTimeData, null, 2)}</pre>
      </div>
    );
  }
}

export default App;
