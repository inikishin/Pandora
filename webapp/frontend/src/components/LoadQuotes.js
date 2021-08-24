import React from 'react';
import Paper from '@material-ui/core/Paper';
import Typography from "@material-ui/core/Typography";
import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';

export default function LoadQuotes(props) {

    const [state, setState] = React.useState({
        loadQuotesChecked: false,
      });

    const handleChange = (event) => {
        setState({...state, [event.target.name]: event.target.checked});
        if (event.target.checked) {
            props.addPipelineRow({
                'operOrder': 1,
                'operName': 'Загрузка данных',
                'operStatus': 'QUEUED',
                'operStart': '01.01.2021 11:12:22',
                'operEnd': '01.01.2021 11:12:22',
                'operDuration': '00:00:22',
                'addInfo': 'none',
                'taskID': ''
            });
        }
        else
        {
            props.removePipeData('Загрузка данных');
        }
    };

    return (
        <Paper>
            <FormControlLabel label="Загрузка котировок" control={
                                      <Switch
                                        checked={state.loadQuotesChecked}
                                        onChange={handleChange}
                                        name="loadQuotesChecked"
                                        color="primary"
                                      />}/>
            { state.loadQuotesChecked && <Typography>История котировок будет загружена</Typography>}

        </Paper>
    );
}