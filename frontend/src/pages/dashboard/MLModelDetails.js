import { useState, useEffect } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Breadcrumbs,
  Button,
  Container,
  Divider,
  Grid,
  Link,
  Tab,
  Tabs,
  Typography
} from '@material-ui/core';
import {
  CustomerDataManagement,
} from '../../components/dashboard/customer';
import { MLModelOverviewDetails, MLModelFeaturesDetails } from '../../components/dashboard/ml-models/index';
import { useDispatch, useSelector } from '../../store/index';
import ChevronRightIcon from '../../icons/ChevronRight';
import PencilAltIcon from '../../icons/PencilAlt';
import gtm from '../../lib/gtm';
import useSettings from '../../hooks/useSettings';
import {
  getMlModelsAvailableFeaturesList,
  getMlModel,
  getMlModelsAvailableAlgorithmsList,
  saveMlModel,
  getMlModelFitResults,
  fitMlModel
} from '../../services/slices/mlModels';
import MLModelAlgorithmDetails from '../../components/dashboard/ml-models/MLModelAlgorithmDetails';
import MLModelFitList from '../../components/dashboard/ml-models/MLModelFitList';
import MLModelPredict from '../../components/dashboard/ml-models/MLModelPredict';

const tabs = [
  { label: 'Details', value: 'details' },
  { label: 'Fit', value: 'fit' },
  { label: 'Predict', value: 'predict' }
];

const MLModelDetails = () => {
  const { mlModelId } = useParams();
  const { settings } = useSettings();
  const [currentTab, setCurrentTab] = useState('details');

  const dispatch = useDispatch();
  const { availableFeaturesList, currentMlModel, availableAlgorithmsList, fit } = useSelector((store) => ({ ...store.mlModels }));

  useEffect(() => {
    gtm.push({ event: 'page_view' });
    dispatch(getMlModelsAvailableFeaturesList());
    dispatch(getMlModelsAvailableAlgorithmsList());
    dispatch(getMlModel(mlModelId));
    dispatch(getMlModelFitResults(mlModelId));
  }, []);

  const handleTabsChange = (event, value) => {
    setCurrentTab(value);
  };

  const handleSaveButton = () => {
    dispatch(saveMlModel(currentMlModel));
  };

  const handleFitButton = () => {
    dispatch(fitMlModel(currentMlModel));
    setCurrentTab('fit');
  };

  if (currentMlModel.mlModel === null) {
    return null;
  }

  return (
    <>
      <Helmet>
        <title>Dashboard: ML Model Details | Pandora</title>
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
                {currentMlModel.mlModel.fullname}
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
                  to="/dashboard/ml-models"
                  variant="subtitle2"
                >
                  ML Models
                </Link>
                <Typography
                  color="textSecondary"
                  variant="subtitle2"
                >
                  {currentMlModel.mlModel.code}
                </Typography>
              </Breadcrumbs>
            </Grid>
            <Grid item>
              <Box sx={{ m: -1 }}>
                <Button
                  color="primary"
                  startIcon={<PencilAltIcon fontSize="small" />}
                  sx={{ m: 1 }}
                  onClick={handleFitButton}
                  variant="contained"
                  disabled={fit.isFitting}
                >
                  Fit
                </Button>
                <Button
                  color="primary"
                  startIcon={<PencilAltIcon fontSize="small" />}
                  sx={{ m: 1 }}
                  onClick={handleSaveButton}
                  variant="contained"
                >
                  Save
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Box sx={{ mt: 3 }}>
            <Tabs
              indicatorColor="primary"
              onChange={handleTabsChange}
              scrollButtons="auto"
              textColor="primary"
              value={currentTab}
              variant="scrollable"
            >
              {tabs.map((tab) => (
                <Tab
                  key={tab.value}
                  label={tab.label}
                  value={tab.value}
                />
              ))}
            </Tabs>
          </Box>
          <Divider />
          <Box sx={{ mt: 3 }}>
            {currentTab === 'details' && (
              <Grid
                container
                spacing={3}
              >
                <Grid
                  item
                  lg={settings.compact ? 6 : 4}
                  md={6}
                  xl={settings.compact ? 6 : 3}
                  xs={12}
                >
                  <MLModelOverviewDetails
                    code={currentMlModel.mlModel.code}
                    fullname={currentMlModel.mlModel.fullname}
                    description={currentMlModel.mlModel.description}
                    timeframe={currentMlModel.mlModel.timeframe_code}
                    ticker={currentMlModel.mlModel.ticker_code}
                    lastFit={currentMlModel.mlModel.last_fit}
                    guid={currentMlModel.mlModel.id}
                  />
                </Grid>
                <Grid
                  item
                  lg={settings.compact ? 6 : 4}
                  md={6}
                  xl={settings.compact ? 6 : 3}
                  xs={12}
                >
                  <MLModelFeaturesDetails
                    features={currentMlModel.mlModel.parameters.features}
                    availableFeatures={availableFeaturesList.list}
                  />
                </Grid>
                <Grid
                  item
                  lg={settings.compact ? 6 : 4}
                  md={6}
                  xl={settings.compact ? 6 : 3}
                  xs={12}
                >
                  <MLModelAlgorithmDetails
                    algorithm={currentMlModel.mlModel.algorithm}
                    algorithmParameters={currentMlModel.mlModel.parameters.algorithm}
                    availableAlgorithms={availableAlgorithmsList.list}
                  />
                </Grid>
                <Grid
                  item
                  lg={settings.compact ? 6 : 4}
                  md={6}
                  xl={settings.compact ? 6 : 3}
                  xs={12}
                >
                  <CustomerDataManagement />
                </Grid>
              </Grid>
            )}
            {currentTab === 'fit' && <MLModelFitList fitResults={currentMlModel.fitResults} />}
            {currentTab === 'predict' && <MLModelPredict fitResults={currentMlModel.fitResults} />}
          </Box>
        </Container>
      </Box>
    </>
  );
};

export default MLModelDetails;
