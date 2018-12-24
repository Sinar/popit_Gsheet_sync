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
    match = searchMatchCLI(searchExactURL, name, feature, featureList, exact=True)
    
    if match:
        matchID = match[0]
    else:  #Exact search failed, try flexible search
        searchURL = u'{}/en/search/{}?q={}:{}'.format(base_url, class_, feature, name)
        match = searchMatchCLI(searchURL, name, feature, featureList)

        if match:
             matchID = match[0]
             matchedVal = match[1]
             while True:
                store = input(u'Updated {0} to "{1}". Store "{2}" as an alternate {0}? (y/n): '.format(feature, name, matchedVal))
                if store.lower() == 'y':
                    storeURL = u'{}/en/{}/{}'.format(base_url, class_, matchID)                               
                    storePayload = {otherfeature: [{feature: matchedVal}]}
                    r_othernames = requests.put(storeURL, headers=headers, json=storePayload)

                    if not r_othernames.ok:
                        print("Failed to store {} as alternate name under {}".format(matchedVal, matchID))
                    break
            
                elif store.lower() == 'n':
                    break
                else:
                   print("Invalid input\nDo any of these results match? (y/n)")
        else:
            print(u"No matches found for {}. A new entry will be made for this.".format(name))
            matchID = ""
            
    return matchID


def searchMatchCLI(searchURL, name, feature, featureList, exact=False):
    r = requests.get(searchURL)
    
    if r.json()['results']:
        results = r.json()['results']
        
        if exact and len(results)==1:
            result = results[0]
            match = [result['id'], result[str(feature)]]
            print('One match found for {}: \n{} ({})'.format(name, match[1], match[0]))
        
        else:
            matches= []
            print('Matches found for {}: '.format(name))

            for j in range(min(5, len(results))):
                p= results[j]
                matches.append([p['id'], p[str(feature)]])
                
                #p[feature]
                print("\n===========")
                print(u"{}. {}".format(j, p[str(feature)]))
                print("Popit ID: {}".format(p['id']))
                for f in featureList:
                    print(u"{}: {}".format(f.upper(), p[str(f)]))
                
            while True:
                matched = input(u"Do any of these results match for {}? (y/n): ".format(name))
                if matched.lower() == 'y':
                    while True:
                        try:
                            matchIndex = int(input("Please select the matching index: "))
                            if matchIndex>=0 and matchIndex< len(matches):
                                match = matches[matchIndex]
                                break
                        except:
                            pass
                        
                    break
                elif matched.lower() == 'n':
                    match = None
                    break
                else:
                    print("Invalid input\nDo any of these results match? (y/n)")
            
    else:
        match = None
     
    
    return match
                    
            