import React from 'react';
import { Box, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@material-ui/core';
import PropTypes from 'prop-types';
import formatDateTime from '../../../utils/formatDate';

const DataExampleTable = ({ dataExample }) => (
  <Box sx={{ m: 2 }}>
    <Typography
      color="textPrimary"
      gutterBottom
      variant="h6"
    >
      Data example
    </Typography>
    <Table>
      <TableHead>
        <TableRow>
          {dataExample.columns.map((item) => (
            <TableCell>
              {item}
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {dataExample.values.slice(-10, dataExample.values.length).map((item) => (
          <TableRow>
            {Object.keys(item).map((value) => (
              <TableCell key={value}>
                <Typography
                  color="textPrimary"
                  gutterBottom
                  variant="subtitle2"
                >
                  {dataExample.columns[value] === 'datetime' ? formatDateTime(item[value]) : item[value]}
                </Typography>
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </Box>
);

DataExampleTable.propTypes = {
  dataExample: PropTypes.object,
};

export default DataExampleTable;
