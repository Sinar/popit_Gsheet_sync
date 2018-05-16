#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def searchCLI_naive(base_url, searchTerm, class_, featureName):    
    foundID = ""

    searchURL = u'{}/en/search/{}/?q={}:{}'.format(base_url, class_, featureName, searchTerm )
    r = requests.get(searchURL)
    if r.ok:
        if r.json()['results']:
            foundID= r.json()['results'][0]['id']
    
    if foundID:
        return foundID
    else:
        return ""
        
def searchCLI(base_url, name, class_, feature, otherfeature, headers, featureList):
    '''
    class: org, person, post
    feature: name, label
    featureList: list of additional features to display in search results
    '''
      
    searchExactURL = u'{}/en/search/{}?q={}:"{}"'.format(base_url, class_, feature, name)
    matchID = searchMatchCLI(searchExactURL, name, feature, featureList)
    
    if not matchID:
        searchURL = u'{}/en/search/{}?q={}:{}'.format(base_url, class_, feature, name)
        matchID = searchMatchCLI(searchURL, name, feature, featureList)

        if matchID:
             while True:
                store = input(u'Store "{0}" as an alternate {1} under the matched {1}? (y/n): '.format(name, feature))
                if store.lower() == 'y':
                    storeURL = u'{}/en/{}/{}'.format(base_url, class_, matchID)                               
                    storePayload = {otherfeature: [{feature: name}]}
                    r_othernames = requests.put(storeURL, headers=headers, json=storePayload)

                    if not r_othernames.ok:
                        print("Failed to store {} as alternate name under {}".format(name, matchID))
                    break
            
                elif store.lower() == 'n':
                    break
                else:
                   print("Invalid input\nDo any of these results match? (y/n)")
        else:
            print(u"No matches found for {}. A new entry will be made for this.".format(name))
            
    return matchID


def searchMatchCLI(searchURL, name, feature, featureList):
    r = requests.get(searchURL)
    
    if r.json()['results']:
        results = r.json()['results']
        
        if len(results)==1:
            matchID = results[0]['id']
            print('One match found for {}: \n{}'.format(name, matchID))
        
        else:
            ids= []
            print('Matches found for {}: '.format(name))

            #for j in range(len(results)):
            for j in range(min(5, len(results))):
                p= results[j]
                ids.append(p['id'])

                print("\n===========")
                print(u"{}. {}".format(j, p[str(feature)]))
                print("Popit ID: {}".format(p['id']))
                for f in featureList:
                    print(u"{}: {}".format(f.upper(), p[str(f)]))
                
            while True:
                match = input(u"Do any of these results match for {}? (y/n): ".format(name))
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
                    
            