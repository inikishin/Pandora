import { createSlice } from '@reduxjs/toolkit';
import {
  getTickersRequest,
  getTimeframesRequest,
  // getQuotesRequest,
  getMarketsRequest,
} from '../api/quotes';

const initialState = {
  markets: {
    isLoading: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  tickers: {
    isLoading: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  timeframes: {
    isLoading: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  quotes: {
    isLoading: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
};

export const slice = createSlice({
  name: 'quotes',
  initialState,
  reducers: {
    GET_MARKETS_REQUEST(state) {
      state.markets.isLoading = true;
      state.markets.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_MARKETS_SUCCESS(state, action) {
      state.markets.isLoading = false;
      state.markets.list = action.payload;
    },
    GET_MARKETS_FAILED(state, action) {
      state.markets.isLoading = false;
      state.markets.list = [];
      state.markets.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_TICKERS_REQUEST(state) {
      state.tickers.isLoading = true;
      state.tickers.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_TICKERS_SUCCESS(state, action) {
      state.tickers.isLoading = false;
      state.tickers.list = action.payload;
    },
    GET_TICKERS_FAILED(state, action) {
      state.tickers.isLoading = false;
      state.tickers.list = [];
      state.tickers.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_TIMEFRAMES_REQUEST(state) {
      state.timeframes.isLoading = true;
      state.timeframes.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_TIMEFRAMES_SUCCESS(state, action) {
      state.timeframes.isLoading = false;
      state.timeframes.list = action.payload;
    },
    GET_TIMEFRAMES_FAILED(state, action) {
      state.timeframes.isLoading = false;
      state.timeframes.list = [];
      state.timeframes.errors = {
        hasError: true,
        message: action.payload
      };
    },
  }
});

export const { reducer } = slice;

export const getMarkets = () => async (dispatch) => {
  dispatch(slice.actions.GET_MARKETS_REQUEST);

  await getMarketsRequest().then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_MARKETS_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_MARKETS_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getTickers = () => async (dispatch) => {
  dispatch(slice.actions.GET_TICKERS_REQUEST);

  await getTickersRequest().then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_TICKERS_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_TICKERS_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getTimeframes = () => async (dispatch) => {
  dispatch(slice.actions.GET_TIMEFRAMES_REQUEST);

  await getTimeframesRequest().then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_TIMEFRAMES_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_TIMEFRAMES_FAILED(`API Error: ${error.message}`));
    }
  );
};
