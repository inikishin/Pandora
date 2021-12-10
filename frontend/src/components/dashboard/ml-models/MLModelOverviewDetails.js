import PropTypes from 'prop-types';
import {
  Box,
  Button,
  Card,
  CardHeader,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Typography,
} from '@material-ui/core';
import MLModelOverviewDetailsEditModal from './MLModelOverviewDetailsEditModal';
import PencilAltIcon from '../../../icons/PencilAlt';
import { format } from 'date-fns';
import { useState } from 'react';

const MLModelOverviewDetails = (props) => {
  const { code, fullname, description, timeframe, ticker, lastFit, guid, ...other } = props;

  const [isOpenOverviewDetailsEditModal, setIsOpenOverviewDetailsEditModal] = useState(false);

  const handleOpenAvailableFeaturesListModal = () => {
    setIsOpenOverviewDetailsEditModal(true);
  };

  const handleCloseOverviewDetailsEditModal = () => {
    setIsOpenOverviewDetailsEditModal(false);
  };

  return (
    <Card {...other}>
      <CardHeader title="ML Model Details" />
      <Divider />
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                Code
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {code}
              </Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                Fullname
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {fullname}
              </Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                Description
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {description}
              </Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                Ticker
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {ticker.toUpperCase()}
              </Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                Timeframe
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {timeframe.toUpperCase()}
              </Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                Last fit
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {lastFit && format(new Date(lastFit), 'dd MMM yyyy | HH:mm')}
              </Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>
              <Typography
                color="textPrimary"
                variant="subtitle2"
              >
                GUID
              </Typography>
            </TableCell>
            <TableCell>
              <Typography
                color="textSecondary"
                variant="body2"
              >
                {guid}
              </Typography>
            </TableCell>
          </TableRow>
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
          Edit
        </Button>
      </Box>
      <MLModelOverviewDetailsEditModal
        open={isOpenOverviewDetailsEditModal}
        closeHandle={handleCloseOverviewDetailsEditModal}
      />
    </Card>
  );
};

MLModelOverviewDetails.propTypes = {
  code: PropTypes.string,
  fullname: PropTypes.string,
  description: PropTypes.string,
  timeframe: PropTypes.string,
  ticker: PropTypes.string,
  lastFit: PropTypes.string,
  guid: PropTypes.string
};

export default MLModelOverviewDetails;
