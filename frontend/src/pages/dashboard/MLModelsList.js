import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from '../../store/index';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Box, Breadcrumbs, Button, Container, Grid, Link, Typography } from '@material-ui/core';
import useSettings from '../../hooks/useSettings';
import ChevronRightIcon from '../../icons/ChevronRight';
import PlusIcon from '../../icons/Plus';
import gtm from '../../lib/gtm';
import MLModelListTable from '../../components/dashboard/ml-models/MLModelListTable';
import { getMlModels } from '../../services/slices/mlModels';
import MLModelCreateModal from '../../components/dashboard/ml-models/MLModelCreateModal';

const MLModelsList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { mlModels } = useSelector((store) => ({ ...store.mlModels }));
  const { settings } = useSettings();
  const [isOpenMLModelCreateModal, setIsOpenMLModelCreateModal] = useState(false);

  useEffect(() => {
    gtm.push({ event: 'page_view' }); // TODO what is it?
    if (!mlModels.isDeleting) {
      dispatch(getMlModels());
    }
  }, [mlModels.isDeleting]);

  const handleOpenMLModelCreateModal = () => {
    setIsOpenMLModelCreateModal(true);
  };

  const handleCloseMLModelCreateModal = (mlModelId) => {
    setIsOpenMLModelCreateModal(false);
    navigate(`/dashboard/ml-models/${mlModelId}`);
  };

  return (
    <>
      <Helmet>
        <title>Dashboard: Machine learning models | Pandora</title>
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
                Machine learning models list
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
                <Typography
                  color="textSecondary"
                  variant="subtitle2"
                >
                  ML models
                </Typography>
              </Breadcrumbs>
            </Grid>
            <Grid item>
              <Box sx={{ m: -1 }}>
                <Button
                  color="primary"
                  startIcon={<PlusIcon fontSize="small" />}
                  sx={{ m: 1 }}
                  variant="contained"
                  onClick={handleOpenMLModelCreateModal}
                >
                  New ML Model
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Box sx={{ mt: 3 }}>
            {mlModels.isLoading ? <div>Loading data...</div> : <MLModelListTable models={mlModels.list} />}
          </Box>
          <MLModelCreateModal
            open={isOpenMLModelCreateModal}
            closeHandle={handleCloseMLModelCreateModal}
          />
        </Container>
      </Box>
    </>
  );
};

export default MLModelsList;
