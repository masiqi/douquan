import re
from os.path import dirname

def fix_url(tag, root):
    path = root[:]
    if tag == "":
        return tag
    urls = re.findall(r'''(.*)(src|href|action)=(.+?)( |\/>|>).*|(.*)url\(([^\)]+)\)''', tag, re.I)
    if urls == None :
        return tag
    else :
        if urls[0][5] == '' :
            urlQuote = urls[0][2]
        else:
            urlQuote = urls[0][5]
        
    if len(urlQuote) > 0 :
        cUrl = re.sub('''['"]''','',urlQuote)
    else :
        return tag
    
    if re.search(r'''^(http|https|ftp):(\/\/|\\\\)(([\w\/\\\+\-~`@:%])+\.)+([\w\/\\\.\=\?\+\-~`@':!%#]|(&amp;)|&)+''',cUrl,re.I) != None :
        return tag
    elif cUrl[:1] == '/' :
        cUrl = path + cUrl
    elif cUrl[:3]=='../' :
        while cUrl[:3]=='../' :
            cUrl = cUrl[3:]
            if len(path) > 0 :
                path = dirname(path)
    elif cUrl[:2]=='./' :
        cUrl = path + cUrl[1:]
    elif cUrl.lower()[:7]=='mailto:' or cUrl.lower()[:11]=='javascript:' :
        return tag
    else :
        cUrl = path + '/' + cUrl
    r = tag.replace(urlQuote,'"' + cUrl + '"')
    return r
