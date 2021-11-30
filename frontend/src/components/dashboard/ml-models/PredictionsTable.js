import PropTypes from 'prop-types';
import {
  Box,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow, Typography,
} from '@material-ui/core';
import PencilAltIcon from '../../../icons/PencilAlt';
import React from 'react';
import formatDateTime from '../../../utils/formatDate';

const PredictionsTable = ({ predictionsData }) => (
  <Box sx={{ m: 2 }}>
    <Typography
      color="textPrimary"
      gutterBottom
      variant="h6"
    >
      Predictions results
    </Typography>
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>
            DateTime
          </TableCell>
          <TableCell>
            Prediction Value
          </TableCell>
          <TableCell align="right">
            Actions
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {predictionsData.map((prediction) => (
          <TableRow
            hover
            key={prediction[0]}
          >
            <TableCell>
              {formatDateTime(prediction[0])}
            </TableCell>
            <TableCell>
              {prediction[1]}
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
  </Box>
);

PredictionsTable.propTypes = {
  predictionsData: PropTypes.array,
};

export default PredictionsTable;
