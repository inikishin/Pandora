import React from 'react';
import Paper from '@material-ui/core/Paper';
import Typography from "@material-ui/core/Typography";
import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import TextField from '@material-ui/core/TextField';
import Chip from '@material-ui/core/Chip';
import Button from '@material-ui/core/Button';

export default function PostDailyAnalysis(props) {

    const [state, setState] = React.useState({
        postDailyAnalysisChecked: false,
        indexData: 0,
        dateChipData: [],
    });

    const handleChange = (event) => {
        setState({...state, [event.target.name]: event.target.checked});
        if (!event.target.checked) {
            props.removePipeData('Публикация аналитики');
        }
    };

    const handleDateChecked = (event) => {
        if (!Object.values(state.dateChipData).includes(event.target.value)) {
            let a = state.dateChipData;
            a.push({key: state.indexData, label: event.target.value});
            setState({
                ...state, indexData: state.indexData + 1,
                dateChipData: a
            });
        }
    };

    const handleAddButtonClick = (event) => {
        let s = '';
        state.dateChipData.forEach(function (i) {s += i.label + ',';})
        props.addPipelineRow({
            'operOrder': 3,
            'operName': 'Публикация аналитики',
            'operStatus': 'QUEUED',
            'operStart': '01.01.2021 11:12:22',
            'operEnd': '01.01.2021 11:12:22',
            'operDuration': '00:00:22',
            'addInfo': s,
            'taskID': ''
        });
    }

    const deleteDateChip = (chipToDelete) => {
        setState({...state, dateChipData: state.dateChipData.filter((chip) => chip.key !== chipToDelete.key)});
    }

    return (
        <Paper>
            <FormControlLabel label="Публикация аналитики" control={
                <Switch
                    checked={state.postDailyAnalysisChecked}
                    onChange={handleChange}
                    name="postDailyAnalysisChecked"
                    color="primary"
                />}/>

            {state.postDailyAnalysisChecked &&
            <React.Fragment>
                <TextField id="date" label="Дата анализа" type="date" name="lastDate" defaultValue="2021-03-01"
                           onChange={handleDateChecked} InputLabelProps={{
                    shrink: true,
                }}/>
                <DateChipsArray dateChips={state.dateChipData} deleteDateChip={deleteDateChip} />
                <Typography>Будут опубликованы данные аналитические данные</Typography>
                <Button onClick={handleAddButtonClick}>Add</Button>
            </React.Fragment>

            }

        </Paper>
    );
}

function DateChipsArray(props) {

    const handleDelete = (chipToDelete) => () => {
        props.deleteDateChip(chipToDelete);
    };

    return (

        props.dateChips.map((data) => {
            return (
                <li key={data.key}>
                    <Chip
                        label={data.label}
                        onDelete={handleDelete(data)}
                    />
                </li>
            );
        })

    );
}