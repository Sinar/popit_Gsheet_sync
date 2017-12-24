#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def searchCLI_naive(base_url, searchTerm, class_, featureName):    
    foundID = ""

    searchURL = '{}/en/search/{}/?q={}:{}'.format(base_url, class_, featureName, searchTerm )
    r = requests.get(searchURL)
    if r.ok:
        if r.json()['results']:
            foundID= r.json()['results'][0]['id']
    
    if foundID:
        return foundID
    else:
        return ""
        
def searchCLI(base_url, name, class_, feature, otherfeature, featureList):
    '''
    class: org, person, post
    feature: name, label
    featureList: list of additional features to display in search results
    '''
    
    searchURL = '{}/en/search/{}?q={}:"{}"'.format(base_url, class_, feature, name)
    matchID = searchMatchCLI(searchURL, name, feature, featureList)
    if not matchID:
        searchOtherURL = '{}/en/search/{}?q=other_{}s.{}:"{}"'.format(base_url, class_, feature, feature, name)
        
        matchID = searchMatchCLI(searchOtherURL, name, feature, featureList)
        if matchID:
             while True:
                store = input('Store "{0}" as an alternate {1} under the matched {1}? (y/n): '.format(name, feature))
                if store.lower() == 'y':
                    storeURL = '{}/en/{}/{}/{}'.format(base_url, class_, matchID, otherfeature)                               
                    storePayload = {feature: name}
                    
                    print(storeURL)
                    print(storePayload)
                    break
            
                elif store.lower() == 'n':
                    break
                else:
                   print("Invalid input\nDo any of these results match? (y/n)")
        else:
            print("No matches found. A new entry will be made for this..")
            
    return matchID


def searchMatchCLI(searchURL, name, feature, featureList):
    r = requests.get(searchURL)
    
    if r.json()['results']:
        results = r.json()['results']
        
        if len(results)==1:
            matchID = results[0]['id']
            print('One match found {}'.format(matchID))
        
        else:
            ids= []
            for j in range(len(results)):
                p= results[j]
                ids.append(p['id'])
                print("\n===========")
                print("{}. {}".format(j, p[str(feature)]))
                for f in featureList:
                    print("{}: {}".format(f.upper(), p[str(f)]))
                
            while True:
                match = input("Do any of these results match? (y/n): ")
                if match.lower() == 'y':
                    while True:
                        try:
                            matchIndex = int(input("Please select the matching index: "))
                            if matchIndex>=0 and matchIndex< len(ids):
                                matchID = ids[matchIndex]
                                break
                        except:
                            pass
                        
                    break
                elif match.lower() == 'n':
                    matchID = "" 
                    break
                else:
                    print("Invalid input\nDo any of these results match? (y/n)")
            
    else:
        matchID = ""
     
    
    return matchID
                    
            

'''
resultsDic = {}
for j in range(len(results)):
    p = results[j]
    resultsDic[p['id']] = p[str(feature)]
print("\n===========")s
print("%d closest matches found for %s: " %(len(resultsDic), name))
ids = list(resultsDic.keys())

if len(ids)==1:
    matchID = ids[0]
    print('One match found {}'.format(matchID))
    
else:
    for j in range(len(ids)):
        print("%d.\n  %s: %s \n  ID: %s"%(j, feature.upper(), resultsDic[ids[j]], ids[j]))

'''
           