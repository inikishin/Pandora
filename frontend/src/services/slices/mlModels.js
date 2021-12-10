import { createSlice } from '@reduxjs/toolkit';
import {
  getMlModelsRequest,
  getMlModelsAvailableFeaturesListRequest,
  getMlModelRequest,
  getMlModelsAvailableAlgorithmsListRequest,
  postMlModelRequest,
  deleteMlModelRequest,
  patchMlModelRequest,
  getMlModelFitResultsRequest,
  getMlModelFitResultRequest,
  getMlModelPredictRequest,
  postFitMlModelRequest
} from '../api/mlModels';

const initialState = {
  mlModels: {
    isLoading: false,
    isDeleting: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  availableFeaturesList: {
    isLoading: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  currentMlModel: {
    isLoading: false,
    mlModel: null,
    fitResults: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  availableAlgorithmsList: {
    isLoading: false,
    list: [],
    errors: {
      hasError: false,
      message: ''
    },
  },
  currentFitResult: {
    isLoading: false,
    fitResult: null,
    errors: {
      hasError: false,
      message: ''
    },
  },
  currentPredict: {
    isLoading: false,
    predict: null,
    errors: {
      hasError: false,
      message: ''
    },
  },
  fit: {
    isFitting: false,
    errors: {
      hasError: false,
      message: ''
    },
  },
};

export const slice = createSlice({
  name: 'mlModels',
  initialState,
  reducers: {
    GET_ML_MODELS_REQUEST(state) {
      state.mlModels.isLoading = true;
      state.mlModels.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_ML_MODELS_SUCCESS(state, action) {
      state.mlModels.isLoading = false;
      state.mlModels.list = action.payload;
    },
    GET_ML_MODELS_FAILED(state, action) {
      state.mlModels.isLoading = false;
      state.mlModels.list = [];
      state.mlModels.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_AVAILABLE_FEATURES_LIST_REQUEST(state) {
      state.availableFeaturesList.isLoading = true;
      state.availableFeaturesList.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_AVAILABLE_FEATURES_LIST_SUCCESS(state, action) {
      state.availableFeaturesList.isLoading = false;
      state.availableFeaturesList.list = action.payload;
    },
    GET_AVAILABLE_FEATURES_LIST_FAILED(state, action) {
      state.availableFeaturesList.isLoading = false;
      state.availableFeaturesList.list = [];
      state.availableFeaturesList.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_ML_MODEL_REQUEST(state) {
      state.currentMlModel.isLoading = true;
      state.currentMlModel.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_ML_MODEL_SUCCESS(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.mlModel = action.payload;
      state.currentMlModel.mlModel.parameters = JSON.parse(action.payload.parameters);
    },
    GET_ML_MODEL_FAILED(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.mlModel = null;
      state.currentMlModel.errors = {
        hasError: true,
        message: action.payload
      };
    },
    ADD_FEATURE(state, action) {
      const paramsArray = Object.keys(action.payload.values).filter((item) => (item !== 'code'));
      const params = {};
      paramsArray.forEach((item) => {
        params[item] = action.payload.values[item];
      });
      state.currentMlModel.mlModel.parameters.features = [
        ...state.currentMlModel.mlModel.parameters.features,
        {
          code: action.payload.values.code,
          name: action.payload.feature.name,
          params
        }
      ];
    },
    DELETE_FEATURE(state, action) {
      state.currentMlModel.mlModel.parameters.features = state.currentMlModel.mlModel.parameters.features.filter((item) => (item.code !== action.payload));
    },
    GET_AVAILABLE_ALGORITHM_LIST_REQUEST(state) {
      state.availableAlgorithmsList.isLoading = true;
      state.availableAlgorithmsList.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_AVAILABLE_ALGORITHM_LIST_SUCCESS(state, action) {
      state.availableAlgorithmsList.isLoading = false;
      state.availableAlgorithmsList.list = action.payload;
    },
    GET_AVAILABLE_ALGORITHM_LIST_FAILED(state, action) {
      state.availableAlgorithmsList.isLoading = false;
      state.availableAlgorithmsList.list = [];
      state.availableAlgorithmsList.errors = {
        hasError: true,
        message: action.payload
      };
    },
    ADD_ALGORITHM(state, action) {
      console.log('action', action);
      const paramsArray = Object.keys(action.payload.values).filter((item) => (item !== 'code'));
      const params = {};
      paramsArray.forEach((item) => {
        params[item] = action.payload.values[item];
      });
      state.currentMlModel.mlModel.algorithm = action.payload.algorithm.code;
      state.currentMlModel.mlModel.parameters.algorithm = {
        name: action.payload.algorithm.name,
        ...params
      };
    },
    SAVE_ML_MODEL_REQUEST(state) {
      state.currentMlModel.isLoading = true;
      state.currentMlModel.errors = {
        hasError: false,
        message: ''
      };
    },
    SAVE_ML_MODEL_SUCCESS(state) {
      state.currentMlModel.isLoading = false;
    },
    SAVE_ML_MODEL_FAILED(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_ML_MODEL_FIT_RESULTS_REQUEST(state) {
      state.currentMlModel.isLoading = true;
      state.currentMlModel.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_ML_MODEL_FIT_RESULTS_SUCCESS(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.fitResults = action.payload;
    },
    GET_ML_MODEL_FIT_RESULTS_FAILED(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.fitResults = [];
      state.currentMlModel.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_ML_MODEL_FIT_RESULT_REQUEST(state) {
      state.currentFitResult.isLoading = true;
      state.currentFitResult.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_ML_MODEL_FIT_RESULT_SUCCESS(state, action) {
      state.currentFitResult.isLoading = false;
      state.currentFitResult.fitResult = action.payload;
      state.currentFitResult.fitResult.parameters = JSON.parse(action.payload.parameters);
      state.currentFitResult.fitResult.fit_results = JSON.parse(action.payload.fit_results);
    },
    GET_ML_MODEL_FIT_RESULT_FAILED(state, action) {
      state.currentFitResult.isLoading = false;
      state.currentFitResult.fitResult = null;
      state.currentFitResult.errors = {
        hasError: true,
        message: action.payload
      };
    },
    GET_ML_MODEL_PREDICT_REQUEST(state) {
      state.currentPredict.isLoading = true;
      state.currentPredict.errors = {
        hasError: false,
        message: ''
      };
    },
    GET_ML_MODEL_PREDICT_SUCCESS(state, action) {
      state.currentPredict.isLoading = false;
      state.currentPredict.predict = action.payload;
    },
    GET_ML_MODEL_PREDICT_FAILED(state, action) {
      state.currentPredict.isLoading = false;
      state.currentPredict.predict = null;
      state.currentPredict.errors = {
        hasError: true,
        message: action.payload
      };
    },
    ML_MODEL_FIT_REQUEST(state) {
      console.log('ui');
      state.fit.isFitting = true;
      state.fit.errors = {
        hasError: false,
        message: ''
      };
    },
    ML_MODEL_FIT_SUCCESS(state) {
      state.fit.isFitting = false;
    },
    ML_MODEL_FIT_FAILED(state, action) {
      state.fit.isFitting = false;
      state.fit.errors = {
        hasError: true,
        message: action.payload
      };
    },
    UPDATE_ML_MODEL_DETAILS(state, action) {
      state.currentMlModel.mlModel = { ...state.currentMlModel.mlModel, ...action.payload };
    },
    CREATE_ML_MODEL_REQUEST(state) {
      state.currentMlModel.isLoading = true;
      state.currentMlModel.errors = {
        hasError: false,
        message: ''
      };
    },
    CREATE_ML_MODEL_SUCCESS(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.mlModel = action.payload;
      state.currentMlModel.mlModel.parameters = JSON.parse(action.payload.parameters);
    },
    CREATE_ML_MODEL_FAILED(state, action) {
      state.currentMlModel.isLoading = false;
      state.currentMlModel.errors = {
        hasError: true,
        message: action.payload
      };
    },
    DELETE_ML_MODEL_REQUEST(state) {
      state.mlModels.isDeleting = true;
      state.mlModels.errors = {
        hasError: false,
        message: ''
      };
    },
    DELETE_ML_MODEL_SUCCESS(state) {
      state.mlModels.isDeleting = false;
    },
    DELETE_ML_MODEL_FAILED(state, action) {
      state.mlModels.isDeleting = false;
      state.mlModels.errors = {
        hasError: true,
        message: action.payload
      };
    },
  }
});

export const { reducer } = slice;

export const getMlModels = () => async (dispatch) => {
  dispatch(slice.actions.GET_ML_MODELS_REQUEST());

  await getMlModelsRequest().then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_ML_MODELS_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_ML_MODELS_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getMlModelsAvailableFeaturesList = () => async (dispatch) => {
  dispatch(slice.actions.GET_AVAILABLE_FEATURES_LIST_REQUEST());

  await getMlModelsAvailableFeaturesListRequest().then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_AVAILABLE_FEATURES_LIST_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_AVAILABLE_FEATURES_LIST_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getMlModel = (id) => async (dispatch) => {
  dispatch(slice.actions.GET_ML_MODEL_REQUEST());

  await getMlModelRequest(id).then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_ML_MODEL_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_ML_MODEL_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getMlModelsAvailableAlgorithmsList = () => async (dispatch) => {
  dispatch(slice.actions.GET_AVAILABLE_ALGORITHM_LIST_REQUEST());

  await getMlModelsAvailableAlgorithmsListRequest().then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_AVAILABLE_ALGORITHM_LIST_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_AVAILABLE_ALGORITHM_LIST_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const saveMlModel = (mlModel) => async (dispatch) => {
  dispatch(slice.actions.SAVE_ML_MODEL_REQUEST());

  const mlModelForRequest = { ...mlModel.mlModel, parameters: JSON.stringify(mlModel.mlModel.parameters) };

  await patchMlModelRequest(mlModelForRequest).then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.SAVE_ML_MODEL_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.SAVE_ML_MODEL_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const createMlModel = (mlModel) => async (dispatch) => {
  dispatch(slice.actions.CREATE_ML_MODEL_REQUEST());

  const mlModelForRequest = { ...mlModel, parameters: JSON.stringify(mlModel.parameters) };

  await postMlModelRequest(mlModelForRequest).then((res) => {
    if (res && res.status === 201) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.CREATE_ML_MODEL_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.CREATE_ML_MODEL_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const deleteMlModel = (mlModelId) => async (dispatch) => {
  dispatch(slice.actions.DELETE_ML_MODEL_REQUEST());

  await deleteMlModelRequest(mlModelId).then((res) => {
    if (res && res.status === 204) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then(() => {
    dispatch(slice.actions.DELETE_ML_MODEL_SUCCESS());
  }).catch(
    (error) => {
      dispatch(slice.actions.DELETE_ML_MODEL_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getMlModelFitResults = (mlModelId) => async (dispatch) => {
  dispatch(slice.actions.GET_ML_MODEL_FIT_RESULTS_REQUEST());

  await getMlModelFitResultsRequest(mlModelId).then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_ML_MODEL_FIT_RESULTS_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_ML_MODEL_FIT_RESULTS_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getMlModelFitResult = (id) => async (dispatch) => {
  dispatch(slice.actions.GET_ML_MODEL_FIT_RESULT_REQUEST());

  await getMlModelFitResultRequest(id).then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_ML_MODEL_FIT_RESULT_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_ML_MODEL_FIT_RESULT_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const getMlModelPredict = (id) => async (dispatch) => {
  dispatch(slice.actions.GET_ML_MODEL_PREDICT_REQUEST());

  await getMlModelPredictRequest(id).then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.GET_ML_MODEL_PREDICT_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.GET_ML_MODEL_PREDICT_FAILED(`API Error: ${error.message}`));
    }
  );
};

export const fitMlModel = (mlModel) => async (dispatch) => {
  dispatch(slice.actions.ML_MODEL_FIT_REQUEST());

  await postFitMlModelRequest(mlModel.mlModel.id).then((res) => {
    if (res && res.status === 200) {
      return res.data;
    }
    return Promise.reject(new Error(`Request failed with status ${res.status}`));
  }).then((data) => {
    if (!data) {
      throw new Error(`No data in response: ${data}`);
    } else {
      dispatch(slice.actions.ML_MODEL_FIT_SUCCESS(data));
    }
  }).catch(
    (error) => {
      dispatch(slice.actions.ML_MODEL_FIT_FAILED(`API Error: ${error.message}`));
    }
  );
};
