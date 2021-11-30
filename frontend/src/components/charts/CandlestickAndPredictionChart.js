import PropTypes from 'prop-types';
import Chart from 'react-apexcharts';
import { Typography, Box } from '@material-ui/core';
import React from 'react';

const CandlestickAndPredictionChart = ({ chartData, predictionsData }) => {
  const resultArray = [];

  chartData.values.forEach((item) => {
    resultArray.push([...item.slice(0, 5), NaN]);
  });

  predictionsData.forEach((item) => {
    const i = resultArray.findIndex((chartDataItem) => (chartDataItem[0] === item[0]));
    if (i === -1) {
      resultArray.push([item[0], NaN, NaN, NaN, NaN, item[1]]);
    } else {
      resultArray[i] = [...resultArray[i].slice(0, 5), item[1]];
    }
  });

  return (
    <Box sx={{ m: 2 }}>
      <Typography
        color="textPrimary"
        gutterBottom
        variant="h6"
      >
        Predictions on chart
      </Typography>
      <Chart
        options={{
          chart: {
            id: 'basic-candlestick',
          },
          xaxis: {
            title: {
              text: 'date'
            },
          },
          yaxis: {
            title: {
              text: 'price'
            },
          },
          legend: {
            position: 'top'
          },
        }}
        series={[
          {
            type: 'candlestick',
            name: 'chart',
            data: resultArray.map((item) => (
              { x: new Date(item[0]).toLocaleDateString(), y: item.slice(1, 5) }
            ))
          },
          {
            type: 'line',
            name: 'prediction',
            data: resultArray.map((item) => (
              { x: new Date(item[0]).toLocaleDateString(), y: item[5] }
            )),
          }
        ]}
        type="candlestick"
      />
    </Box>
  );
};

CandlestickAndPredictionChart.propTypes = {
  chartData: PropTypes.object,
  predictionsData: PropTypes.array,
};

export default CandlestickAndPredictionChart;
