import { combineReducers } from '@reduxjs/toolkit';
import { reducer as calendarReducer } from '../slices/calendar';
import { reducer as chatReducer } from '../slices/chat';
import { reducer as kanbanReducer } from '../slices/kanban';
import { reducer as mailReducer } from '../slices/mail';
import { reducer as mlModelsReducer } from '../services/slices/mlModels';
import { reducer as quotesReducer } from '../services/slices/quotes';
import { reducer as authReducer } from '../services/slices/auth';

const rootReducer = combineReducers({
  calendar: calendarReducer,
  chat: chatReducer,
  kanban: kanbanReducer,
  mail: mailReducer,
  mlModels: mlModelsReducer,
  quotes: quotesReducer,
  auth: authReducer,
});

export default rootReducer;
