from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .forms import policy
from .lib.modelpredictors import predict_proba_all_models
from .lib.textprocessors import  text_process_policy, post_process_segments, reverse_paragraph_segmenter
import pickle
import pandas as pd

data_encryption = pickle.load(open('./models/data_encryption_NB_segment.pkl','rb'))
data_retention = pickle.load(open('models/data_retention_RF_segment.pkl','rb'))
do_not_track = pickle.load(open('models/do_not_track_NB_segment.pkl','rb'))
first_party = pickle.load(open('models/first_party_collection_NB_segment.pkl','rb'))
third_party = pickle.load(open('models/third_party_sharing_RF_segment.pkl','rb'))
user_access = pickle.load(open('models/user_access_RF_segment.pkl','rb'))
policy_change = pickle.load(open('models/policy_change_NB_segment.pkl','rb'))

models_to_evaluate = {
    'data_encryption':data_encryption,
    'data_retention': data_retention,
    'do_not_track': do_not_track,
    'first_party': first_party,
    'third_party':third_party,
    'user_access':user_access,
    'policy_change':policy_change}

model_threshold = {
    'data_encryption' : 0.05,
    'data_retention': 0.1,
    'do_not_track': 0.1,
    'first_party': 0.1,
    'third_party':0.1,
    'user_access':0.1,
    'policy_change':0.1}

policy_threshold = {
    'data_encryption' : 1,
    'data_retention': 1,
    'do_not_track': 1,
    'first_party': 4,
    'third_party':4,
    'user_access':1,
    'policy_change':1}

def index(request):

    if request.method == 'POST':

        # process form data
        form = policy(request.POST)
        if form.is_valid():
            policy_text = form.cleaned_data['policy_text']
            # print(policy_text)
            segment = reverse_paragraph_segmenter(policy_text)
            # if len(' '.join(segment)) < 500:
            #     message = "Longer texts are required."
            #     return render('output.html',{'msg':message})
            or_segments = pd.DataFrame({'segments':segment})
            segments_processed = [text_process_policy(segment) for segment in segment]
            #removing blank lines
            segments_processed = [segment for segment in segments_processed if segment.strip() != '']
            __,tag_segment = predict_proba_all_models(models_to_evaluate,segments_processed,model_threshold)
            tag_segment = pd.DataFrame(tag_segment)

            results = tag_segment.sum()

            tag_segment = pd.concat([tag_segment,or_segments],axis=1)
            categories = models_to_evaluate.keys()

            segments = {}
            bools = {}

            for c in categories:
                segments[c] = list(tag_segment[tag_segment[c]==1]['segments'])
                segments[c] = post_process_segments(segments[c])

                bools[c] = results[c] >= policy_threshold[c]

            for i in segments:
                segments[i]='\n'.join(segments[i])
            #print(bools)
            return render('res.html',{'bools':bools, 'segments':segments})
    return render(request,'index.html', {'form': policy()})