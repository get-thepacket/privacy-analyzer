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
    'data_retention': 0.01,
    'do_not_track': 0.01,
    'first_party': 0.3,
    'third_party':0.16,
    'user_access':0.05,
    'policy_change':0.05}

policy_threshold = {
    'data_encryption' : 1,
    'data_retention': 1,
    'do_not_track': 1,
    'first_party': 5,
    'third_party':5,
    'user_access':1,
    'policy_change':1}

to_change={
    'first_party':False,
    'data_encryption':True,
    'third_party':False,
    'data_retention':False,
    'user_access':True,
    'policy_change':True,
    'do_not_track': False
}

msg={
    'first_party':'DATA COLLECTION',
    'data_encryption':'DATA SECURITY',
    'third_party':"THIRD PARTY DATA SHARING",
    'data_retention':"DATA RETENTION",
    'user_access':'USER DATA ACCESS AND DELETION',
    'policy_change':'POLICY CHANGE',
    'do_not_track': 'TRACKERS'
}



def about(request):
    return render(request, 'about.html')
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
            for i in bools:
                if to_change[i]:
                    bools[i] = not bools[i]

            tagLine={}
            if bools['data_retention']:
                tagLine['data_retention'] = "This service keeps your data even after you discontinue using its service"
            else:
                tagLine['data_retention'] = "This service does nor keep your data after you discontinue using its service"
            if bools['data_encryption']:
                tagLine['data_encryption'] = "This service does not uses encryption to protect your data"
            else:
                tagLine['data_encryption'] = "This service  uses encryption to protect your data"
            if bools['third_party']:
                tagLine['third_party'] = "Exchanges your data with third party"
            else:
                tagLine['third_party'] = "Does not Exchanges your data with third party"
            if bools['first_party']:
                tagLine['first_party'] = "This service collects users personal information"
            else:
                tagLine['first_party'] = "This service does not collect users personal information"
            if bools['user_access']:
                tagLine['user_access'] = "This service does not allows user access to data"
            else:
                tagLine['user_access'] = "This service allows user to access and delete data"
            if bools['do_not_track']:
                tagLine['do_not_track'] = "This service uses trackers"
            else:
                tagLine['do_not_track'] = "This service does not uses trackers"
            if bools['policy_change']:
                tagLine['policy_change'] = "This service does not inform users for policy changes"
            else:
                tagLine['policy_change'] = "This Service informs users for any policy change"
            arr = []
            print(bools)
            count = 1
            for i in segments:
                arr.append((count,msg[i],bools[i],segments[i],tagLine[i]))
                count+=1

            return render(request,'res.html',{'arr':arr})
    return render(request,'index.html', {'form': policy()})