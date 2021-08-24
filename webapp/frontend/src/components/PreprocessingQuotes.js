import React from 'react';
import Paper from '@material-ui/core/Paper';
import Typography from "@material-ui/core/Typography";
import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';

export default function PreprocessingQuotes(props) {

    const [state, setState] = React.useState({
        preprocessingQuotesChecked: false,
      });

    const handleChange = (event) => {
        setState({...state, [event.target.name]: event.target.checked});
        if (event.target.checked) {
            props.addPipelineRow({
                'operOrder': 2,
                'operName': 'Предобработка данных',
                'operStatus': 'QUEUED',
                'operStart': '01.01.2021 11:12:22',
                'operEnd': '01.01.2021 11:12:22',
                'operDuration': '00:00:22',
                'addInfo': 'none',
                'taskID': ''
            });
        } else {
            props.removePipeData('Предобработка данных');
        }
    };

    return (
        <Paper>
            <FormControlLabel label="Предобработка котировок" control={
                                      <Switch
                                        checked={state.preprocessingQuotesChecked}
                                        onChange={handleChange}
                                        name="preprocessingQuotesChecked"
                                        color="primary"
                                      />}/>
            { state.preprocessingQuotesChecked && <Typography>Будет произведена предобработка данных</Typography>}

        </Paper>
    );
}