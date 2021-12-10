import instance from './apiInstance';

export const getMlModelsRequest = async () => instance.get('predictions/ml-models/');
export const getMlModelsAvailableFeaturesListRequest = async () => instance.get('predictions/ml-models/available_features_list/');
export const getMlModelRequest = async (id) => instance.get(`predictions/ml-models/${id}/`);
export const getMlModelsAvailableAlgorithmsListRequest = async () => instance.get('predictions/ml-models/available_algorithms_list/');
export const patchMlModelRequest = async (mlModel) => instance.patch(`predictions/ml-models/${mlModel.id}/`, mlModel);
export const deleteMlModelRequest = async (mlModelId) => instance.delete(`predictions/ml-models/${mlModelId}/`);
export const postMlModelRequest = async (mlModel) => instance.post('predictions/ml-models/', mlModel);
export const postFitMlModelRequest = async (mlModelId) => instance.post(`predictions/ml-models/${mlModelId}/fit/`);
export const getMlModelFitResultsRequest = async (mlModelId) => instance.get('predictions/ml-models-fit-results/', { params: { ml_model: mlModelId } });
export const getMlModelFitResultRequest = async (mlModelFitResultId) => instance.get(`predictions/ml-models-fit-results/${mlModelFitResultId}/`);
export const getMlModelPredictRequest = async (mlModelFitResultId) => instance.get(`predictions/ml-models-fit-results/${mlModelFitResultId}/predict/`);
