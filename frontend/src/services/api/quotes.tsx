import instance from './apiInstance';

export const getMarketsRequest = async () => instance.get('quotes/markets/');
export const getTickersRequest = async () => instance.get('quotes/tickers/');
export const getTimeframesRequest = async () => instance.get('quotes/timeframes/');
export const getQuotesRequest = async () => instance.get('quotes/quotes/');
