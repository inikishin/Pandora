import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Typography from "@material-ui/core/Typography";

export default function WorkflowTable(props) {

    return (

        <TableContainer component={Paper}>
            <Typography variant="h4">Пайплайн</Typography>
            <Table aria-label="simple table">
                <TableHead>
                    <TableRow>
                        <TableCell>Процесс</TableCell>
                        <TableCell align="right">Статус</TableCell>
                        <TableCell align="right">Время начала</TableCell>
                        <TableCell align="right">Время завершения</TableCell>
                        <TableCell align="right">Длительность</TableCell>
                        <TableCell align="left">Дополнительная информация</TableCell>
                        <TableCell>Task ID</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {props.pipelineRows.map((row) => (
                        <TableRow key={row.operName}>
                            <TableCell component="th" scope="row">
                                {row.operName}
                            </TableCell>
                            <TableCell align="right">{row.operStatus}</TableCell>
                            <TableCell align="right">{row.operStart}</TableCell>
                            <TableCell align="right">{row.operEnd}</TableCell>
                            <TableCell align="right">{row.operDuration}</TableCell>
                            <TableCell>{row.addInfo}</TableCell>
                            <TableCell>{row.taskID}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>

    );
}