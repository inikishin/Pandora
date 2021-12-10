import { useState } from 'react';
import PropTypes from 'prop-types';
import { useFormik } from 'formik';
import { useDispatch } from '../../../store/index';
import { slice } from '../../../services/slices/mlModels';
import {
  Box,
  Button,
  Card,
  CardHeader,
  Divider, Link, List, MenuItem, ListItemText, Paper,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Typography,
  Dialog, IconButton
} from '@material-ui/core';
import PencilAltIcon from '../../../icons/PencilAlt';
import DynamicInput from '../../dynamic-forms/DynamicInput';

const MLModelAlgorithmDetails = ({ algorithm, algorithmParameters, availableAlgorithms }) => {
  console.log('Input props', algorithm, '|', algorithmParameters, '|', availableAlgorithms);
  const [isOpenAvailableAlgorithmsListModal, setIsOpenAvailableAlgorithmsListModal] = useState(false);
  const [isOpenAlgorithmSettingsModal, setIsOpenAlgorithmSettingsModal] = useState(false);
  const [currentAlgorithm, setCurrentAlgorithm] = useState({});

  const handleOpenAvailableAlgorithmListModal = () => {
    setIsOpenAvailableAlgorithmsListModal(true);
  };

  const handleCloseAvailableAlgorithmsListModal = (checkedAlgorithm) => {
    setIsOpenAvailableAlgorithmsListModal(false);
    if (checkedAlgorithm) {
      setCurrentAlgorithm(checkedAlgorithm);
      setIsOpenAlgorithmSettingsModal(true);
    }
  };

  const handleCloseAlgorithmSettingsModal = () => {
    setIsOpenAlgorithmSettingsModal(false);
  };

  return (
    <>
      <Card>
        <CardHeader title="ML Model Algorithm" />
        <Divider />
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>
                <Typography
                  color="textPrimary"
                  variant="subtitle2"
                >
                  ML model algorithm
                </Typography>
              </TableCell>
              <TableCell>
                <Typography
                  color="textSecondary"
                  variant="body2"
                >
                  {algorithm}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <IconButton>
                  <PencilAltIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
            {algorithmParameters && Object.keys(algorithmParameters).map((item) => (
              <TableRow
                key={item}
              >
                <TableCell>
                  <Typography
                    color="textPrimary"
                    variant="subtitle2"
                  >
                    {item}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography
                    color="textSecondary"
                    variant="body2"
                  >
                    {algorithmParameters[item]}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <IconButton>
                    <PencilAltIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <Box
          sx={{
            alignItems: 'flex-start',
            display: 'flex',
            flexDirection: 'column',
            p: 1
          }}
        >
          <Button
            color="inherit"
            startIcon={<PencilAltIcon fontSize="small" />}
            sx={{ mt: 1 }}
            variant="text"
            onClick={handleOpenAvailableAlgorithmListModal}
          >
            Edit
          </Button>
        </Box>
      </Card>
      <AvailableAlgorithmsListModal
        availableAlgorithmsList={availableAlgorithms}
        open={isOpenAvailableAlgorithmsListModal}
        closeHandle={handleCloseAvailableAlgorithmsListModal}
      />
      <AlgorithmSettingsModal
        algorithm={currentAlgorithm}
        open={isOpenAlgorithmSettingsModal}
        closeHandle={handleCloseAlgorithmSettingsModal}
      />
    </>
  );
};

const AvailableAlgorithmsListModal = ({ availableAlgorithmsList, open, closeHandle }) => {
  const handleClickAlgorithm = (event) => {
    event.stopPropagation();
    const clickedAlgorithm = availableAlgorithmsList.find((item) => (item.code === event.currentTarget.id));
    closeHandle(clickedAlgorithm);
  };

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
          <Box sx={{ p: 2 }}>
            <Typography
              color="textPrimary"
              variant="h6"
            >
              Available algorithms
            </Typography>
          </Box>
          <List disablePadding>
            {availableAlgorithmsList.map((algorithm) => (
              <MenuItem
                divider
                key={algorithm.name}
                onClick={handleClickAlgorithm}
                id={algorithm.code}
              >
                <ListItemText
                  primary={(
                    <Link
                      color="textPrimary"
                      sx={{ cursor: 'pointer' }}
                      underline="none"
                      variant="subtitle2"
                    >
                      {algorithm.name}
                    </Link>
                  )}
                  secondary={algorithm.description}
                />

              </MenuItem>
            ))}
          </List>
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
            >
              Select algorithm
            </Button>
          </Box>
        </Paper>
      </Box>
    </Dialog>
  );
};

const AlgorithmSettingsModal = ({ algorithm, open, closeHandle }) => {
  const dispatch = useDispatch();

  let initialValues = {
    code: ''
  };
  if (algorithm.params && Object.keys(algorithm.params)) {
    Object.keys(algorithm.params).forEach((item) => {
      initialValues = {
        [item]: algorithm.params[item].default
      };
    });
  }

  const formik = useFormik({
    initialValues,
    values: {},
    onSubmit: (values, actions) => {
      dispatch(slice.actions.ADD_ALGORITHM({ algorithm, values }));
      actions.resetForm({ values: '' });
      closeHandle();
    }
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
            maxWidth: 550,
            minWidth: 400,
            mx: 'auto'
          }}
        >
          <form onSubmit={formik.handleSubmit}>
            <Box sx={{ p: 2 }}>
              <Typography
                color="textPrimary"
                variant="h6"
              >
                {`Algorithm ${algorithm.name} settings`}
              </Typography>
            </Box>
            <Box sx={{ p: 1 }}>
              {algorithm.params && Object.keys(algorithm.params).map((item) => (
                <DynamicInput
                  key={item}
                  type={algorithm.params[item].type}
                  name={item}
                  defaultValue={algorithm.params[item].default}
                  description={algorithm.params[item].description}
                  onChange={formik.handleChange}
                  value={formik.values[item]}
                  selectList={algorithm.params[item].type === 'select' ? algorithm.params[item].select_list : []}
                />
              ))}
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
                Save algorithm
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Dialog>
  );
};

MLModelAlgorithmDetails.propTypes = {
  algorithm: PropTypes.string,
  algorithmParameters: PropTypes.array,
  availableAlgorithms: PropTypes.array,
};

AvailableAlgorithmsListModal.propTypes = {
  availableAlgorithmsList: PropTypes.array,
  open: PropTypes.bool,
  closeHandle: PropTypes.func
};

AlgorithmSettingsModal.propTypes = {
  algorithm: PropTypes.object,
  open: PropTypes.bool,
  closeHandle: PropTypes.func
};

export default MLModelAlgorithmDetails;
