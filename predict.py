
 #-*-coding:utf-8 -*-
import sys
import wordninja
import enchant
import re
import json
import random
from sklearn.cluster import KMeans
import numpy as np
import dns.resolver




def detect_word_not_in_dictionary(domain): # domain = "ctbcholding.com"
    domain = domain.split(".")[0]      # domain = "ctbcholding"
    
    to_words = wordninja.split(domain) # to_words = ['ct', 'bc', 'holding']
    
    new_concern = []
    concern = to_words               # 'bc' 也許跟 'ct' 組成一個單字，也許跟 'holding' 組成一個單字
                                     # 或者是 'ct', 'bc', 'holding' 三個在一起形成一個單字
    for ind,i in enumerate(concern): # 從 to_words 中找出所有有可能的單字組合，並存入 unique
        if len(i) <= 2 and ind > 0:
            new_concern1 = concern[ind-1] + concern[ind]
            new_concern.append(new_concern1)

            if ind < len(concern)-1:
                new_concern2 = concern[ind] + concern[ind+1]
                new_concern3 = concern[ind-1] + concern[ind] + concern[ind+1]
                new_concern.append(new_concern2)
                new_concern.append(new_concern3)
        elif len(i) <= 2 and ind == 0 and len(concern) != 1:
            new_concern4 = concern[ind] + concern[ind+1]
            new_concern.append(new_concern4)
        elif len(i) <= 2 and ind == 0:
            new_concern.append(i)
        else:
            new_concern.append(i)
    unique = set(new_concern)
    unique = list(unique)      # unique = ['ctbc', 'ctbcholding', 'holding', 'bcholding']
    
    to_words = unique
    for i in range(len(to_words)): # 第一個字母大寫
        to_words[i] = re.sub('([a-zA-Z])', lambda x: x.groups()[0].upper(), to_words[i], 1)
        # to_words = ['Ctbc', 'Ctbcholding', 'Holding', 'Bcholding']

    d = enchant.Dict("en_US") # 開啟字典
    count = 0
    score = 0
    for word in to_words:
        if d.check(word) == False:  # 查看是否在字典內
            count += 1
            suggest_list = d.suggest(word) # 不在字典內的話，查詢是否有 suggest words
            if len(suggest_list) != 0:  # 如果有 suggest words， 代表偽裝現有英文單字組合
                score += 5              # 加 5 分
    if count != 0:
        word_not_in_dictionary_score = score / count  # 避免長的網域可疑的英文單字組合越多分數越高，平均起來
    else:
        word_not_in_dictionary_score = 0
    
    return int(word_not_in_dictionary_score) # 這個 score 結果只有兩種，得 0 分，要不然就是得 5 分
                                        # domain 只要有一個可疑的單字， 就會得 5 分



def mx_score(domain):
    mail_domain = domain

    try:
        records  = dns.resolver.query(mail_domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
        exist_mx = True
    except Exception as e:
        exist_mx = False
    
    score = 0
    if exist_mx == False:
        score = 10
        
    return int(score)
    
def train_and_predict(domain, score0, score1, score2, score3): 
    
    # 把所有可能的 score 的組合當作 training data
    scores_for_fit = [[0,0,0,0],[0,0,0,10],[0,0,10,0],[0,0,10,10],
                      [5,0,0,0],[5,0,0,10],[5,0,10,0],[5,0,10,10],
                      [0,10,0,0],[0,10,0,10],[0,10,10,10],[0,10,10,0],
                      [5,10,0,0],[5,10,0,10],[5,10,10,10],[5,10,10,0]]

    X = np.array(scores_for_fit)
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X) # train
    
    prediction = kmeans.predict([[int(score0), int(score1), int(score2), int(score3)]]) # predict
    
    flag = "unsuspicious"
    
    if prediction[0] == 1:
        flag = "suspicious"
    elif prediction[0] == 2:
        flag = "very suspicious"
    
    json_data = {"domain": domain, "prediction": flag}
    
    return json.dumps(json_data, ensure_ascii=False) # 以 json 格式回傳預測


if __name__ == '__main__':
#--test--
    # json_data_from_java = json.loads('{"domain":"apple.com", "score2": 10, "score3": 10}')  # 接收 json 並轉成字典
    
    # word_not_in_dictionary_score = detect_word_not_in_dictionary(json_data_from_java["domain"])
    # mx = mx_score(json_data_from_java["domain"])
    # print(train_and_predict(json_data_from_java["domain"], 
    #                   word_not_in_dictionary_score, 
    #                   mx))

    #                   json_data_from_java["score2"],
    #                   json_data_from_java["score3"]))
#--test--

    data_from_java = []
    for i in range(1, len(sys.argv)):

        data_from_java.append((sys.argv[i]))

    word_not_in_dictionary_score = detect_word_not_in_dictionary(data_from_java[0])
    print(train_and_predict(data_from_java[0], 
                      word_not_in_dictionary_score, 
                      data_from_java[1],
                      data_from_java[2],
                      data_from_java[3]))