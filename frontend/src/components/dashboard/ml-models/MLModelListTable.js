import { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { format } from 'date-fns';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardHeader,
  Checkbox,
  Divider,
  IconButton,
  Link,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  Typography
} from '@material-ui/core';
import { useDispatch } from '../../../store/index';
import { deleteMlModel } from '../../../services/slices/mlModels';
import ArrowRightIcon from '../../../icons/ArrowRight';
import Label from '../../Label';
import MoreMenu from '../../MoreMenu';
import Scrollbar from '../../Scrollbar';
import MLModelListBulkActions from './MLModelListBulkActions';
import TrashIcon from '../../../icons/Trash';

const getStatusLabel = (paymentStatus) => {
  const map = {
    canceled: {
      color: 'error',
      text: 'Canceled'
    },
    completed: {
      color: 'success',
      text: 'Completed'
    },
    pending: {
      color: 'warning',
      text: 'Pending'
    },
    rejected: {
      color: 'error',
      text: 'Rejected'
    }
  };

  const { text, color } = map[paymentStatus];

  return (
    <Label color={color}>
      {text}
    </Label>
  );
};

const applyPagination = (orders, page, limit) => orders
  .slice(page * limit, page * limit + limit);

const MLModelListTable = (props) => {
  const dispatch = useDispatch();
  const { models, ...other } = props;
  const [selectedModels, setSelectedModels] = useState([]);
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(5);

  const handleSelectAllOrders = (event) => {
    setSelectedModels(event.target.checked
      ? models.map((model) => model.id)
      : []);
  };

  const handleSelectOneModel = (event, modelId) => {
    if (!selectedModels.includes(modelId)) {
      setSelectedModels((prevSelected) => [...prevSelected, modelId]);
    } else {
      setSelectedModels((prevSelected) => prevSelected.filter((id) => id !== modelId));
    }
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleLimitChange = (event) => {
    setLimit(parseInt(event.target.value, 10));
  };

  const handleDeleteMLModel = (event) => {
    dispatch(deleteMlModel(event.currentTarget.id));
  };

  const paginatedModels = applyPagination(models, page, limit);
  const enableBulkActions = selectedModels.length > 0;
  const selectedSomeOrders = selectedModels.length > 0 && selectedModels.length < models.length;
  const selectedAllOrders = selectedModels.length === models.length;

  return (
    <>
      <Card {...other}>
        <CardHeader
          action={<MoreMenu />}
          title="Machine learning models"
        />
        <Divider />
        <Scrollbar>
          <Box sx={{ minWidth: 1150 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedAllOrders}
                      color="primary"
                      indeterminate={selectedSomeOrders}
                      onChange={handleSelectAllOrders}
                    />
                  </TableCell>
                  <TableCell>
                    Code
                  </TableCell>
                  <TableCell>
                    Name
                  </TableCell>
                  <TableCell>
                    Ticker
                  </TableCell>
                  <TableCell>
                    Timeframe
                  </TableCell>
                  <TableCell>
                    Algorithm
                  </TableCell>
                  <TableCell>
                    Last fit
                  </TableCell>
                  <TableCell>
                    Status
                  </TableCell>
                  <TableCell align="right">
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedModels.map((model) => {
                  const isModelSelected = selectedModels.includes(model.guid);

                  return (
                    <TableRow
                      hover
                      key={model.guid}
                      selected={selectedModels.indexOf(model.id) !== -1}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={isModelSelected}
                          color="primary"
                          onChange={(event) => handleSelectOneModel(event, model.id)}
                          value={isModelSelected}
                        />
                      </TableCell>
                      <TableCell>
                        <Link
                          color="textPrimary"
                          component={RouterLink}
                          to={`/dashboard/ml-models/${model.id}`}
                          underline="none"
                          variant="subtitle2"
                        >
                          {model.code}
                        </Link>
                        <Typography
                          color="textSecondary"
                          variant="body2"
                        >
                          {model.guid}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          color="textPrimary"
                          variant="subtitle2"
                        >
                          {model.fullname}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {model.ticker_code.toUpperCase()}
                      </TableCell>
                      <TableCell>
                        {model.timeframe_code.toUpperCase()}
                      </TableCell>
                      <TableCell>
                        {model.algorithm}
                      </TableCell>
                      <TableCell>
                        {format(new Date(model.last_fit), 'dd MMM yyyy | HH:mm')}
                      </TableCell>
                      <TableCell>
                        {getStatusLabel('completed')}
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          component={RouterLink}
                          to={`/dashboard/ml-models/${model.id}`}
                        >
                          <ArrowRightIcon fontSize="small" />
                        </IconButton>
                        <IconButton onClick={handleDeleteMLModel} id={model.id}>
                          <TrashIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Box>
        </Scrollbar>
        <TablePagination
          component="div"
          count={models.length}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleLimitChange}
          page={page}
          rowsPerPage={limit}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </Card>
      <MLModelListBulkActions
        open={enableBulkActions}
        selected={selectedModels}
      />
    </>
  );
};

MLModelListTable.propTypes = {
  models: PropTypes.array.isRequired
};

export default MLModelListTable;
