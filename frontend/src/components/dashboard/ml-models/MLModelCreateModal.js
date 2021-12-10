import { useDispatch, useSelector } from '../../../store';
import { useEffect } from 'react';
import { getTickers, getTimeframes } from '../../../services/slices/quotes';
import { useFormik } from 'formik';
import { createMlModel } from '../../../services/slices/mlModels';
import {
  Box, Button,
  Dialog,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography
} from '@material-ui/core';
import PropTypes from 'prop-types';

const MLModelCreateModal = ({ open, closeHandle }) => {
  const dispatch = useDispatch();
  const { timeframes, tickers } = useSelector((state) => ({ ...state.quotes }));
  const { mlModel } = useSelector((state) => ({ ...state.mlModels.currentMlModel }));
  const { user } = useSelector((state) => ({ ...state.auth }));

  useEffect(() => {
    dispatch(getTickers());
    dispatch(getTimeframes());
  }, []);

  useEffect(() => {
    console.log(mlModel);
    if (mlModel && mlModel.id) {
      closeHandle(mlModel.id);
    }
  }, [mlModel]);

  const initialValues = {
    code: '',
    fullname: '',
    description: '',
    timeframe: '',
    ticker: ''
  };

  const formik = useFormik({
    initialValues,
    values: {},
    onSubmit: ((values) => {
      dispatch(createMlModel({
        ...values,
        timeframe_code: timeframes.list.find((item) => (item.id === values.timeframe)).code,
        ticker_code: tickers.list.find((item) => (item.id === values.ticker)).code,
        parameters: {
          features: [],
        },
        user: user.id,
      }));
    })
  });

  return (
    <Dialog
      open={open}
      onClose={closeHandle}
    >
      <Box
        sx={{
          backgroundColor: 'background.default',
          minHeight: '100%',
          p: 2
        }}
      >
        <Paper
          elevation={22}
          sx={{
            maxWidth: 320,
            minWidth: 300,
            mx: 'auto'
          }}
        >
          {(timeframes.isLoading || tickers.isLoading) ? <span>isLoading</span> : <span>not isLoading</span>}
          <form onSubmit={formik.handleSubmit}>
            <Box sx={{ p: 2 }}>
              <Typography
                color="textPrimary"
                variant="h6"
              >
                ML Model details
              </Typography>
            </Box>
            <Box sx={{ p: 2 }}>
              <TextField
                sx={{ m: 1 }}
                fullWidth
                label="code"
                name="code"
                required
                helperText="ML Model unique code"
                variant="outlined"
                onChange={formik.handleChange}
                value={formik.values.code}
              />
              <TextField
                sx={{ m: 1 }}
                fullWidth
                label="fullname"
                name="fullname"
                required
                helperText="ML Model fullname"
                variant="outlined"
                onChange={formik.handleChange}
                value={formik.values.fullname}
              />
              <TextField
                sx={{ m: 1 }}
                fullWidth
                label="description"
                name="description"
                required
                helperText="ML Model description"
                variant="outlined"
                onChange={formik.handleChange}
                value={formik.values.description}
              />
              <FormControl
                fullWidth
                sx={{ m: 1 }}
              >
                <InputLabel>Timeframe</InputLabel>
                <Select
                  value={formik.values.timeframe}
                  label="Timeframe"
                  onChange={formik.handleChange}
                  name="timeframe"
                  required
                >
                  {timeframes.list.map((item) => (<MenuItem key={item.id} value={item.id}>{item.code.toUpperCase()}</MenuItem>))}
                </Select>
              </FormControl>
              <FormControl
                fullWidth
                sx={{ m: 1 }}
              >
                <InputLabel>Ticker</InputLabel>
                <Select
                  value={formik.values.ticker}
                  label="Ticker"
                  onChange={formik.handleChange}
                  name="ticker"
                  required
                >
                  {tickers.list.slice(1, 20).map((item) => (<MenuItem key={item.id} value={item.id}>{item.code.toUpperCase()}</MenuItem>))}
                </Select>
              </FormControl>
            </Box>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                p: 1
              }}
            >
              <Button
                color="primary"
                size="small"
                variant="text"
                type="submit"
              >
                Create
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Dialog>
  );
};

MLModelCreateModal.propTypes = {
  open: PropTypes.bool,
  closeHandle: PropTypes.func,
};

export default MLModelCreateModal;
