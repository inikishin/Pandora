import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import Chart from 'react-apexcharts';
import {
  Box,
  Breadcrumbs,
  Button,
  Container,
  Divider,
  Grid,
  Link, Paper,
  Typography
} from '@material-ui/core';
import useSettings from '../../hooks/useSettings';
import ChevronRightIcon from '../../icons/ChevronRight';
import gtm from '../../lib/gtm';
import { getMlModel, getMlModelFitResult } from '../../services/slices/mlModels';
import Scrollbar from '../../components/Scrollbar';
import { format } from 'date-fns';
import DataExampleTable from '../../components/dashboard/ml-models/DataExampleTable';

const MLModelFitResultsDetails = () => {
  const dispatch = useDispatch();
  const { mlModelId, fitResultsId } = useParams();
  const { currentFitResult, currentMlModel } = useSelector((store) => ({ ...store.mlModels }));

  const { settings } = useSettings();

  useEffect(() => {
    dispatch(getMlModel(mlModelId));
    dispatch(getMlModelFitResult(fitResultsId));
    gtm.push({ event: 'page_view' });
  }, []);

  if (!currentFitResult.fitResult || !currentMlModel.mlModel) {
    return null;
  }

  return (
    <>
      <Helmet>
        <title>Dashboard: ML Model Fit Results Details | Pandora</title>
      </Helmet>
      <Box
        sx={{
          backgroundColor: 'background.default',
          minHeight: '100%',
          py: 8
        }}
      >
        <Container maxWidth={settings.compact ? 'xl' : false}>
          <Grid
            container
            justifyContent="space-between"
            spacing={3}
          >
            <Grid item>
              <Typography
                color="textPrimary"
                variant="h5"
              >
                ML Model Fit Results Details
              </Typography>
              <Breadcrumbs
                aria-label="breadcrumb"
                separator={<ChevronRightIcon fontSize="small" />}
                sx={{ mt: 1 }}
              >
                <Link
                  color="textPrimary"
                  component={RouterLink}
                  to="/dashboard"
                  variant="subtitle2"
                >
                  Dashboard
                </Link>
                <Link
                  color="textPrimary"
                  component={RouterLink}
                  to="/dashboard"
                  variant="subtitle2"
                >
                  ML Models
                </Link>
                <Link
                  color="textPrimary"
                  component={RouterLink}
                  to={`/dashboard/ml-models/${currentMlModel.mlModel.id}`}
                  variant="subtitle2"
                >
                  {currentMlModel.mlModel.fullname}
                </Link>
                <Typography
                  color="textSecondary"
                  variant="subtitle2"
                >
                  {currentFitResult.fitResult.algorithm}
                </Typography>
              </Breadcrumbs>
            </Grid>
            <Grid item>
              <Box sx={{ m: -1 }}>
                <Button
                  color="primary"
                  sx={{ m: 1 }}
                  variant="outlined"
                >
                  Preview PDF
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Divider sx={{ my: 3 }} />
          <Paper>
            <Scrollbar>
              <Box
                sx={{
                  minWidth: 800,
                  p: 6
                }}
              >
                <Grid
                  container
                  justifyContent="space-between"
                >
                  <Grid item>
                    <Typography
                      color="textPrimary"
                      variant="h6"
                    >
                      {`Trained at ${format(new Date(currentFitResult.fitResult.created_at), 'dd MMM yyyy HH:mm')}`}
                    </Typography>
                  </Grid>
                  <Grid item>
                    <Typography
                      align="right"
                      color="textPrimary"
                      variant="h4"
                    >
                      {`Algorithm: ${currentFitResult.fitResult.algorithm}`}
                      <br />
                      {`Score: ${currentFitResult.fitResult.score}`}
                    </Typography>
                    <Typography
                      align="right"
                      color="textPrimary"
                      variant="subtitle2"
                    >
                      {`Model filename: ${currentFitResult.fitResult.filename}`}
                    </Typography>
                  </Grid>
                </Grid>
                <Box sx={{ my: 4 }}>
                  <Grid
                    container
                    justifyContent="space-between"
                  >
                    <Grid item>
                      <Typography
                        color="textPrimary"
                        variant="body2"
                      >
                        Параметры тренировки:
                        <br />
                        {`Целевая колонка: ${currentFitResult.fitResult.parameters.predict.target}`}
                        <br />
                        {`Смещение: ${currentFitResult.fitResult.parameters.predict.shift}`}
                        <br />
                        {`Процент тренировочных данных: ${currentFitResult.fitResult.parameters.fit.split_train_percentage * 100}%`}
                        <br />
                      </Typography>
                    </Grid>
                    <Grid item>
                      <Typography
                        align="right"
                        color="textPrimary"
                        variant="body2"
                      >
                        Параметры алгоритма:
                        <br />
                        {
                          Object.keys(currentFitResult.fitResult.parameters.algorithm).map((key) => (
                            <>
                              { `${key}: ${currentFitResult.fitResult.parameters.algorithm[key]}` }
                              <br />
                            </>
                          ))
                        }
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
                <DataExampleTable dataExample={currentFitResult.fitResult.fit_results.data_example} />
                <Box sx={{ mt: 2 }}>
                  <Typography
                    color="textPrimary"
                    gutterBottom
                    variant="h6"
                  >
                    {currentFitResult.fitResult.fit_results.target_predict_chart.title}
                  </Typography>
                  <Typography
                    color="textSecondary"
                    variant="body2"
                  >
                    {currentFitResult.fitResult.fit_results.target_predict_chart.description}
                  </Typography>
                  <Chart
                    type="line"
                    options={{
                      chart: {
                        id: 'basic',
                      },
                      xaxis: {
                        categories: currentFitResult.fitResult.fit_results.target_predict_chart.x_data,
                        title: {
                          text: currentFitResult.fitResult.fit_results.target_predict_chart.x_title
                        },
                      },
                      yaxis: {
                        title: {
                          text: currentFitResult.fitResult.fit_results.target_predict_chart.y_title
                        },
                      },
                      legend: {
                        position: 'top'
                      }
                    }}
                    series={
                        [
                          {
                            name: currentFitResult.fitResult.fit_results.target_predict_chart.y_label_1,
                            data: currentFitResult.fitResult.fit_results.target_predict_chart.y_data_1
                          },
                          {
                            name: currentFitResult.fitResult.fit_results.target_predict_chart.y_label_2,
                            data: currentFitResult.fitResult.fit_results.target_predict_chart.y_data_2,
                          }
                        ]
                    }
                  />
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography
                    color="textPrimary"
                    gutterBottom
                    variant="h6"
                  >
                    Last bars
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
                      }
                    }}
                    series={[
                      {
                        type: 'line',
                        name: 'MA13',
                        data: currentFitResult.fitResult.fit_results.data_example.values.map((item) => (
                          { x: new Date(item[0]).toLocaleDateString(), y: item[7] }
                        ))
                      },
                      {
                        type: 'candlestick',
                        name: 'chart',
                        data: currentFitResult.fitResult.fit_results.data_example.values.map((item) => (
                          { x: new Date(item[0]).toLocaleDateString(), y: item.slice(1, 5) }
                        ))
                      }]}
                    type="candlestick"
                  />
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography
                    color="textPrimary"
                    gutterBottom
                    variant="h6"
                  >
                    {currentFitResult.fitResult.fit_results.feature_importances.title}
                  </Typography>
                  <Chart
                    type="radar"
                    options={
                      {
                        dataLabels: {
                          enabled: true,
                          background: {
                            enabled: true,
                            borderRadius: 2,
                          }
                        },
                        labels: currentFitResult.fitResult.fit_results.feature_importances.x_data
                      }
                    }
                    series={[
                      {
                        name: 'Radar Series 1',
                        data: currentFitResult.fitResult.fit_results.feature_importances.y_data_1.map((item) => (item.toFixed(6)))
                      }
                    ]}
                  />
                </Box>
              </Box>
            </Scrollbar>
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default MLModelFitResultsDetails;
