import numpy as np

# A helper function to predict probabilities from models stored in a dict
def predict_proba_all_models(model_dict, segment_list, thresholds):
    """
    This takes dict of models as input and gives a dict output with result
    keys related to model keys, evaluated on list of policy segments.
    Returns the probability and cls against thresholds.
    """
    names = model_dict.keys()
    prob = {}
    cls = {}
    for name in names:
        prob[name] = np.array(model_dict[name].predict_proba(segment_list))
        prob[name] = prob[name][:, 1]
        tmp = prob[name]
        tmp[tmp >= thresholds[name]] = 1
        tmp[tmp < thresholds[name]] = 0
        cls[name] = tmp

    return prob, cls
