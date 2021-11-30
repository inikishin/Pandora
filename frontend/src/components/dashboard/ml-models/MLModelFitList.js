import { Link as RouterLink } from 'react-router-dom';
import { format } from 'date-fns';
import {
  Box,
  Card,
  CardHeader,
  Divider,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow
} from '@material-ui/core';
import ArrowRightIcon from '../../../icons/ArrowRight';
import MoreMenu from '../../MoreMenu';
import Scrollbar from '../../Scrollbar';
import PropTypes from 'prop-types';

const MLModelFitList = ({ fitResults }) => {
  console.log('length', fitResults.length);
  return (
    <Card>
      <CardHeader
        action={<MoreMenu />}
        title="Ml Model Fit List"
      />
      <Divider />
      <Scrollbar>
        <Box sx={{ minWidth: 1150 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  ID
                </TableCell>
                <TableCell>
                  Algorithm
                </TableCell>
                <TableCell>
                  Score
                </TableCell>
                <TableCell>
                  Fitted at
                </TableCell>
                <TableCell align="right">
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {fitResults.map((result) => (
                <TableRow key={result.id}>
                  <TableCell>
                    #
                    {result.id}
                  </TableCell>
                  <TableCell>
                    {result.algorithm}
                  </TableCell>
                  <TableCell>
                    {result.score}
                  </TableCell>
                  <TableCell>
                    {format(new Date(result.created_at), 'dd MMM yyyy | HH:mm')}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      component={RouterLink}
                      to={`/dashboard/ml-models/${result.ml_model}/fit-results/${result.id}`}
                    >
                      <ArrowRightIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Scrollbar>
      <TablePagination
        component="div"
        count={fitResults.length}
        onPageChange={() => {
        }}
        onRowsPerPageChange={() => {
        }}
        page={0}
        rowsPerPage={5}
        rowsPerPageOptions={[5, 10, 25]}
      />
    </Card>
  );
};

MLModelFitList.propTypes = {
  fitResults: PropTypes.array,
};

export default MLModelFitList;
