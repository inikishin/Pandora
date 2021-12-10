import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: {
    id: 1,
    username: 'Ilya'
  }
};

export const slice = createSlice({
  name: 'auth',
  initialState,
  reducers: {}
});

export const { reducer } = slice;
