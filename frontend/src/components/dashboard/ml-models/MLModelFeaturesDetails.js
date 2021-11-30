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
import TrashIcon from '../../../icons/Trash';

const MLModelFeaturesDetails = (props) => {
  const dispatch = useDispatch();
  const { features, availableFeatures, ...other } = props;
  const [isOpenAvailableFeaturesListModal, setIsOpenAvailableFeaturesListModal] = useState(false);
  const [isOpenFeatureSettingsModal, setIsOpenFeatureSettingsModal] = useState(false);
  const [currentFeature, setCurrentFeature] = useState({});

  const handleOpenAvailableFeaturesListModal = () => {
    setIsOpenAvailableFeaturesListModal(true);
  };

  const handleCloseAvailableFeaturesListModal = (feature) => {
    setIsOpenAvailableFeaturesListModal(false);
    if (feature) {
      setCurrentFeature(feature);
      setIsOpenFeatureSettingsModal(true);
    }
  };

  const handleDeleteFeature = (e) => {
    dispatch(slice.actions.DELETE_FEATURE(e.currentTarget.id));
  };

  const handleCloseFeatureSettingsModal = () => {
    setIsOpenFeatureSettingsModal(false);
  };

  return (
    <>
      <Card {...other}>
        <CardHeader title="ML Model Features" />
        <Divider />
        <Table>
          <TableBody>
            {features.map((item) => (
              <TableRow
                key={item.code}
              >
                <TableCell>
                  <Typography
                    color="textPrimary"
                    variant="subtitle2"
                  >
                    {item.code}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography
                    color="textSecondary"
                    variant="body2"
                  >
                    {item.params.period}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <IconButton>
                    <PencilAltIcon fontSize="small" />
                  </IconButton>
                  <IconButton onClick={handleDeleteFeature} id={item.code}>
                    <TrashIcon fontSize="small" />
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
            onClick={handleOpenAvailableFeaturesListModal}
          >
            Add
          </Button>
        </Box>
      </Card>
      <AvailableFeaturesListModal
        availableFeatureList={availableFeatures}
        open={isOpenAvailableFeaturesListModal}
        closeHandle={handleCloseAvailableFeaturesListModal}
      />
      <FeatureSettingsModal
        feature={currentFeature}
        open={isOpenFeatureSettingsModal}
        closeHandle={handleCloseFeatureSettingsModal}
      />
    </>
  );
};

const AvailableFeaturesListModal = ({ availableFeatureList, open, closeHandle }) => {
  const handleClickFeature = (event) => {
    event.stopPropagation();
    const clickedFeature = availableFeatureList.find((item) => (item.name === event.currentTarget.id));
    console.log(clickedFeature);
    closeHandle(clickedFeature);
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
              Available features
            </Typography>
          </Box>
          <List disablePadding>
            {availableFeatureList.map((feature) => (
              <MenuItem
                divider
                key={feature.name}
                onClick={handleClickFeature}
                id={feature.name}
              >
                <ListItemText
                  primary={(
                    <Link
                      color="textPrimary"
                      sx={{ cursor: 'pointer' }}
                      underline="none"
                      variant="subtitle2"
                    >
                      {feature.name}
                    </Link>
                  )}
                  secondary={feature.description}
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
              Add feature
            </Button>
          </Box>
        </Paper>
      </Box>
    </Dialog>
  );
};

const FeatureSettingsModal = ({ feature, open, closeHandle }) => {
  const dispatch = useDispatch();

  let initialValues = {
    code: ''
  };
  if (feature.params && Object.keys(feature.params)) {
    Object.keys(feature.params).forEach((item) => {
      initialValues = {
        [item]: feature.params[item].default
      };
    });
  }
  console.log('initialValues', initialValues);
  const formik = useFormik({
    initialValues,
    values: {},
    onSubmit: (values, actions) => {
      dispatch(slice.actions.ADD_FEATURE({ feature, values }));
      actions.resetForm({ values: '' });
      closeHandle();
    }
  });
  console.log('formik', formik);

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
          <form onSubmit={formik.handleSubmit}>
            <Box sx={{ p: 2 }}>
              <Typography
                color="textPrimary"
                variant="h6"
              >
                {`Feature ${feature.name} settings`}
              </Typography>
            </Box>
            <Box sx={{ p: 1 }}>
              <DynamicInput
                type="text"
                name="code"
                defaultValue=""
                description="unique feature code"
                onChange={formik.handleChange}
                value={formik.values.code}
              />
              {feature.params && Object.keys(feature.params).map((item) => (
                <DynamicInput
                  key={item}
                  type={feature.params[item].type}
                  name={item}
                  defaultValue={feature.params[item].default}
                  description={feature.params[item].description}
                  onChange={formik.handleChange}
                  value={formik.values[item]}
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
                Add feature
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Dialog>
  );
};

MLModelFeaturesDetails.propTypes = {
  features: PropTypes.array,
  availableFeatures: PropTypes.array,
};

AvailableFeaturesListModal.propTypes = {
  availableFeatureList: PropTypes.array,
  open: PropTypes.bool,
  closeHandle: PropTypes.func
};

FeatureSettingsModal.propTypes = {
  feature: PropTypes.object,
  open: PropTypes.bool,
  closeHandle: PropTypes.func
};

export default MLModelFeaturesDetails;
