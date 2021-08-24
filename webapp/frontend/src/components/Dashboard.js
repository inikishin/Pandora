import React from 'react';
import { useEffect, useRef } from 'react';
import clsx from 'clsx';
import { makeStyles, useTheme } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import MailIcon from '@material-ui/icons/Mail';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import Button from "@material-ui/core/Button";

import LoadQuotes from "./LoadQuotes";
import PreprocessingQuotes from "./PreprocessingQuotes";
import PostDailyAnalysis from "./PostDailyAnalysis";
import WorkflowTable from "./WorkflowTable";

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  appBar: {
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: drawerWidth,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  hide: {
    display: 'none',
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: 'flex-end',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: -drawerWidth,
  },
  contentShift: {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  },
}));

export default function Dashboard() {
    const classes = useStyles();
    const theme = useTheme();
    const [state, setState] = React.useState({'open': false,
                                                        'pipelineRows': [],
                                                        'isPending': false,
                                                        'currentOperation': null,
                                                        'currentOperationStart': 1,
                                                        'currentOperationDuration': null});

    useEffect(() => {
        let id;
        if (state.isPending) {
            id = setInterval(() => {
                //setState({...state, currentOperationDuration: state.currentOperationDuration + 1});
                updatePipelineRow('Загрузка данных', state.currentOperationStart+1)
                console.log('interval', state.pipelineRows);
            }, 3000);
        } else {
            return () => clearInterval(id);
        }
    });

    // хендлеры для обработки паплайна
    function pipelineCompare(a, b) {
        if (a.operOrder < b.operOrder) {
            return -1;
        }
        if (a.operOrder > b.operOrder) {
            return 1;
        }
        // a должно быть равным b
        return 0;
    }

    function addPipelineRow(rowData) {
        let r = state.pipelineRows;
        r.push(rowData);
        setState({...state, pipelineRows: r.sort(pipelineCompare)});
    }

    function updatePipelineRow(operName, duration) {
        let tmp_arr = state.pipelineRows;
        tmp_arr.forEach(function (item, index, array) {
            if (item.operName == operName) {
                item.duration = duration;
            }
        });
        console.log(tmp_arr);
        setState({...state, pipelineRows: tmp_arr});
    }

    function removePipeData(operName) {
        return setState({...state, pipelineRows: state.pipelineRows.filter((oper) => oper.operName !== operName)});
    }

    // хендлеры для менюшки
    const handleDrawerOpen = () => {
        setState( {...state, open: true});
    };

    const handleDrawerClose = () => {
        setState({...state, open: false});
    };

    const handleExecute = () => {
        setState({...state, isPending: true});
        let id = loadquotes();
    };

    // api
    const url = 'http://127.0.0.1:9999';

    function checkTaskStatus(id) {
        fetch(url + '/api/getaskstatus/' + id)
            .then(
                function (response) {
                    if (response.status !== 200) {
                        console.log('Looks like there was a problem. Status Code: ' +
                            response.status);
                        return;
                    }

                    // Examine the text in the response
                    response.json().then(function (data) {
                        console.log(data);
                    });
                }
            )
            .catch(function (err) {
                console.log('Fetch Error :-S', err);
            });
    }

    function loadquotes() {
        fetch(url + '/api/loadquotes')
            .then(
                function (response) {
                    if (response.status !== 200) {
                        console.log('Looks like there was a problem. Status Code: ' +
                            response.status);
                        return;
                    }

                    // Examine the text in the response
                    response.json().then(function (data) {
                        console.log(data);
                        return data.id;
                    });
                }
            )
            .catch(function (err) {
                console.log('Fetch Error :-S', err);
            });
    }
    return (
        <div className={classes.root}>
            <CssBaseline />
            <AppBar position="fixed" className={clsx(classes.appBar, {
                  [classes.appBarShift]: state.open,
                })}>
                <Toolbar>
                    <IconButton color="inherit" aria-label="open drawer" onClick={handleDrawerOpen} edge="start"
                        className={clsx(classes.menuButton, state.open && classes.hide)}>
                        <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" noWrap>
                        Pandora Dashboard
                    </Typography>
                </Toolbar>
            </AppBar>
            <Drawer className={classes.drawer} variant="persistent" anchor="left" open={state.open}
                classes={{
              paper: classes.drawerPaper,
            }}>
                <div className={classes.drawerHeader}>
                    <IconButton onClick={handleDrawerClose}>
                        {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
                    </IconButton>
                </div>
                <Divider />
                <List>
                    {['Daily analysis', 'Predictions'].map((text, index) => (
                        <ListItem button key={text}>
                          <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                          <ListItemText primary={text} />
                        </ListItem>
                        ))}
                </List>
                <Divider />
                <List>
                    {['Logging', 'Storage'].map((text, index) => (
                        <ListItem button key={text}>
                          <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                          <ListItemText primary={text} />
                        </ListItem>
                      ))}
                </List>
            </Drawer>
            <main className={clsx(classes.content, {
              [classes.contentShift]: state.open,
            })}>
                <div className={classes.drawerHeader} />
                <Container maxWidth="lg">
                    <Grid container spacing={3}>
                        <Grid item lg={4}><LoadQuotes addPipelineRow={addPipelineRow} removePipeData={removePipeData} /></Grid>
                        <Grid item lg={4}><PreprocessingQuotes addPipelineRow={addPipelineRow} removePipeData={removePipeData} /></Grid>
                        <Grid item lg={4}><PostDailyAnalysis addPipelineRow={addPipelineRow} removePipeData={removePipeData} /></Grid>
                    </Grid>
                    <Grid container spacing={3}>
                        <Grid item lg={12}><WorkflowTable pipelineRows={state.pipelineRows} /></Grid>
                    </Grid>
                    <Grid container spacing={3}>
                        <Grid item lg={4}><Button onClick={handleExecute}>Execute</Button></Grid>
                    </Grid>
                    <Grid container spacing={3}>
                        <Grid item lg={4}>Logging</Grid>
                    </Grid>
                </Container>
            </main>
        </div>
    );
}