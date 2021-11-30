import { useState } from 'react';
import {
  Box,
  Card,
  CardHeader,
  Divider,
  TextField, Button, Snackbar, Alert
} from '@material-ui/core';
import MoreMenu from '../../MoreMenu';
import Scrollbar from '../../Scrollbar';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from '../../../store';
import { getMlModelPredict } from '../../../services/slices/mlModels';
import DataExampleTable from './DataExampleTable';
import CandlestickAndPredictionChart from '../../charts/CandlestickAndPredictionChart';
import PredictionsTable from './PredictionsTable';

const MLModelPredict = ({ fitResults }) => {
  const [selectedFitResult, setSelectedFitResult] = useState('');
  const [isOpenSelectAlert, setIsOpenSelectAlert] = useState(false);

  const dispatch = useDispatch();
  const { currentPredict } = useSelector((store) => ({ ...store.mlModels }));

  const handleSelect = (e) => {
    e.preventDefault();
    setSelectedFitResult(e.target.value);
  };

  const handlePredict = () => {
    if (selectedFitResult) {
      dispatch(getMlModelPredict(selectedFitResult));
    } else {
      setIsOpenSelectAlert(true);
    }
  };

  const handleCloseSelectAlert = () => {
    setIsOpenSelectAlert(false);
  };

  return (
    <Card>
      <CardHeader
        action={<MoreMenu />}
        title="Predict prices"
      />
      <Divider />
      <Scrollbar>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }} m={2}>
          <TextField
            fullWidth
            label="Model fit variant"
            name="fit_results"
            onChange={handleSelect}
            select
            SelectProps={{ native: true }}
            value={selectedFitResult}
            variant="outlined"
            sx={{ m: 2 }}
          >
            {fitResults.map((result) => (
              <option
                key={result.id}
                value={result.id}
              >
                {`'${result.algorithm}' trained at ${result.created_at} (${result.id})`}
              </option>
            ))}
          </TextField>
          <Button
            sx={{ m: 2, minWidth: 120 }}
            color="primary"
            variant="contained"
            onClick={handlePredict}
          >
            Predict
          </Button>
        </Box>
        {currentPredict.predict
          ? (
            <Box sx={{ m: 2 }}>
              <PredictionsTable predictionsData={currentPredict.predict.predictions} />
              <CandlestickAndPredictionChart
                chartData={currentPredict.predict.data_example}
                predictionsData={currentPredict.predict.predictions}
              />
              <DataExampleTable dataExample={currentPredict.predict.data_example} />
            </Box>
          )
          : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
              <Box sx={{ height: 50 }}>
                <span>No predict. Please select fit variant and press Predict button</span>
              </Box>
            </Box>
          )}
      </Scrollbar>
      <Snackbar
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        open={isOpenSelectAlert}
        onClose={handleCloseSelectAlert}
        autoHideDuration={6000}
      >
        <Alert
          onClose={handleCloseSelectAlert}
          severity="warning"
          sx={{ width: '100%' }}
        >
          Please select fit model variant
        </Alert>
      </Snackbar>
    </Card>
  );
};

MLModelPredict.propTypes = {
  fitResults: PropTypes.array,
};

export default MLModelPredict;
