import PropTypes from 'prop-types';
import { Checkbox, FormControl, FormControlLabel, InputLabel, MenuItem, Select, TextField } from '@material-ui/core';

const DynamicInput = ({ type, name, defaultValue, description, onChange, value, selectList }) => {
  if (type === '123') {
    console.log(defaultValue);
  }

  return (
    <>
      {(type === 'text') && (
      <TextField
        sx={{ m: 1 }}
        fullWidth
        label={name}
        name={name}
        required
        helperText={description}
        variant="outlined"
        onChange={onChange}
        value={value}
      />
      )}
      {(type === 'integer') && (
      <TextField
        sx={{ m: 1 }}
        fullWidth
        label={name}
        name={name}
        required
        helperText={description}
        variant="outlined"
        onChange={onChange}
        value={value}
        type="number"
      />
      )}
      {(type === 'float') && (
      <TextField
        sx={{ m: 1 }}
        fullWidth
        label={name}
        name={name}
        required
        helperText={description}
        variant="outlined"
        onChange={onChange}
        value={value}
        type="number"
      />
      )}
      {(type === 'bool') && (
        <FormControlLabel
          sx={{ m: 1 }}
          control={(
            <Checkbox
              name={name}
              onChange={onChange}
              value={value}
            />
          )}
          label={name}
        />
      )}
      {(type === 'select') && (
        <FormControl
          fullWidth
          sx={{ m: 1 }}
        >
          <InputLabel>{name}</InputLabel>
          <Select
            value={value}
            label={name}
            onChange={onChange}
            name={name}
            required
            helperText={description}
          >
            {selectList.map((item) => (<MenuItem value={item.value}>{item.description}</MenuItem>))}
          </Select>
        </FormControl>
      )}
    </>
  );
};

DynamicInput.propTypes = {
  type: PropTypes.string,
  name: PropTypes.string,
  defaultValue: PropTypes.any,
  description: PropTypes.string,
  onChange: PropTypes.func,
  value: PropTypes.any,
  selectList: PropTypes.array,
};

export default DynamicInput;
