import re


def strip_pars(text):

    pars = re.findall(r'\((.*?)\)', text)
    notpars = re.sub(r'\([^)]*?\)', '', text)
    
    if pars:
        pars = pars[0]
    
    return notpars.strip(), pars.strip()


def simplified_ipa(ipa, pars=False):

    suprasegmentals = "( ) ˈ ː . ˌ ˑ ‿ | ‖ ↗ ↘ ˥ ˦ ˧ ˨ ˩ ꜛ".split()#|↗‖↘

    if pars:
        ipa = strip_pars(ipa)[0]
    for i in suprasegmentals:
        ipa = ipa.replace(i, '')

    return ipa



class WeightedLevenshteinDistance():

    
    def __init__(self):

        similar = """p b
                    t d
                    ʈ ɖ
                    c ɟ
                    k g
                    q ɢ
                    m ɱ
                    n ɳ
                    ɲ ŋ
                    ʙ r
                    ɾ ɽ
                    ɸ β
                    f v
                    θ ð
                    s z
                    ʃ ʒ
                    ʂ ʐ
                    ç ʝ
                    x ɣ
                    χ ʁ
                    ħ ʕ
                    h ɦ
                    ɬ ɮ
                    ɯ u""".split('\n')

        similarv = """i y
                    ɨ ʉ
                    ɪ ʏ
                    e ø
                    ɘ ɵ
                    ɤ o
                    ɛ œ
                    ɜ ɞ
                    ʌ ɔ
                    a ɶ
                    ɑ ɒ""".split('\n')

        similar = [s.strip().split() for s in similar if s.strip()]
        self.similars = {}
        for pair in similar:
            x = pair[0]
            y = pair[1]
            self.similars[x]=y
            self.similars[y]=x

        similarv = [s.strip().split() for s in similarv if s.strip()]
        self.similarsv = {}
        for pair in similarv:
            x = pair[0]
            y = pair[1]
            self.similarsv[x]=y
            self.similarsv[y]=x


    def minimum(self, a, b, c, d=1e31):
        
        if(a <= b and a <= c and a <= d):
            return a
        if(b <= a and b <= c and b <= d):
            return b
        if(c <= a and c <= b and c <= d):
            return c

        return d


    def computeLevenshteinDistance_str(self, str1, str2, add=1, delete=1, substitute=1, simplify=False):

        str1 = simplified_ipa(str1, simplify)
        str2 = simplified_ipa(str2, simplify)

        return self.computeLevenshteinDistance(list(str1), list(str2), add, delete, substitute)


    def computeLevenshteinDistance(self, str1, str2, insert=1, delete=1, substitute=1):

        if min([len(str1),len(str2)])<1:
            return False

        distance = [[0 for i in range(len(str2)+1)] for i in range(len(str1)+1)]

        for i in range(len(str1)+1):
            distance[i][0] = i * delete    # non-weighted algorithm doesn't take Delete weight into account

        for j in range(len(str2)+1):
            distance[0][j] = j * insert    # non-weighted algorithm doesn't take Insert weight into account

        for i in range(1,len(str1)+1):
            
            for j in range(1,len(str2)+1):
                
                distance[i][j]= self.minimum(distance[i-1][j] + delete,
                                             distance[i][j-1] + insert,
                                             distance[i-1][j-1] + (0 if (str1[i-1] == str2[j-1]) else 0.5 \
                                                          if (str1[i-1] in self.similars and self.similars[str1[i-1]] == str2[j-1]) else 0.5 \
                                                          if (str1[i-1] in self.similarsv and self.similarsv[str1[i-1]] == str2[j-1]) else substitute)    \
                                    )

        return (1. * distance[len(str1)][len(str2)] / min([len(str1), len(str2)]))
	

WLD = WeightedLevenshteinDistance()


def weighted_ipa_lev(str1, str2, insert=1, delete=1, substitute=1, simplify=False):

    return WLD.computeLevenshteinDistance_str(str1, str2, insert, delete, substitute, simplify)


        
if __name__=="__main__":

    test = """
acts	facts	ækts	fækts
back	backs	bæk	bæks
damn	damned	dæm	dæmd
peace	paz	pis	pas
than	that	ðæn	ðæt
along	long	əˈlɒŋ	lɒŋ
babe	baby	beɪb	ˈbeɪbi
baby	babe	ˈbeɪbi	beɪb
bang	gang	beɪŋ	ɡeɪŋ
bed	beg	bɛd	bɛɡ
blue	blu	bluː	blu
burned	burnt	ˈbɜː(r)nd	ˈbɜrnt
burnt	burned	ˈbɜrnt	ˈbɜː(r)nd
bye	hi	baɪ	haɪ
care	cared	kɛəɹ	kɛəd
clothing	clothes	ˈkləʊðɪŋ	kləʊðz
color	colour	ˈkʌl.ɚ	ˈkʌl.ə(ɹ)
colour	color	ˈkʌl.ɚ	ˈkʌl.ə(ɹ)
dad	daddy	dæd	ˈdædi
day	days	deɪ	ˈdeɪz
defence	defense	ˈdifɛns	diˈfɛns
defence	defense	ˈdifɛns	dɪˈfɛns
electrical	electric	ɪˈlɛktɹɪkəl	ɪˈlɛktɹɪk
ever	never	ˈɛvə	ˈnɛv.ə(ɹ)
fancy	fantasy	ˈfæn.tsi	ˈfæn(t)əsi
fancy	fantasy	ˈfæn.tsi	ˈfæntəsi
fantasy	fancy	ˈfæntəsi	ˈfæn.tsi
favor	favour	ˈfeɪvɚ	ˈfeɪvə(ɹ)
favour	favor	ˈfeɪvɚ	ˈfeɪvə(ɹ)
fill	film	fɪl	fɪlm
filmings	film	ˈfɪlmɪŋz	fɪlm
find	fine	faɪnd	faɪn
hell	heck	hɛl	hɛk
hi	bye	haɪ	baɪ
historic	historical	hɪˈstɒɹɪk	hɪˈstɒɹɪkəl
historical	historic	hɪˈstɔːɹɪkəl	hɪˈstɔːɹɪk
hold	hole	həʊld	həʊl
labor	labour	ˈleɪ.bɚ	ˈleɪ.bə
labour	labor	ˈleɪ.bə	ˈleɪ.bɚ
league	liga	liːɡ	ˈliɡa
long	along	lɒŋ	əˈlɒŋ
mama	mom	ˈmɑmə	mɑm
mom	mama	mɑm	ˈmɑmə
mom	mum	mɑm	mʌm
mum	mom	mʌm	mɑm
never	ever	ˈnɛvɚ	ˈɛvɚ
passed	past	pɑːst	pæst
past	passed	pɑːst	pæst
personal	personnel	ˈpɜː.sən.əl	pɝ.səˈnɛl
personnel	personal	pɝ.səˈnɛl	ˈpɜː.sən.əl
polis	politicians	ˈpɒ.lɪs	ˌpɒlɪˈtɪʃənz
present	presente	prəˈzɛnt	preˈzɛnte
rear	river	ɹɪə	ˈɹɪvə
seem	seen	siːm	siːn
service	serving	ˈsɜːvɪs	ˈsɜːvɪŋ
technique	tecnica	tɛkˈniːk	ˈtɛknika
thanks	thank	θæŋks	θæŋk
that	than	ðət	ðən
theater	theatre	ˈθiː(ə)təɹ	ˈθi(ə)təɹ
theater	theatre	ˈθiː(ə)təɹ	ˈθi.eɪ.təɹ
theater	theatre	ˈθiː(ə)təɹ	ˈθɪ.ə.tə(ɹ)
theatre	theater	ˈθɪ.ə.tə(ɹ)	ˈθiː(ə)təɹ
wine	wind	waɪn	waɪnd
worse	worst	wɝs	wɝst
worst	worse	wɝst	wɝs
yours	your	jɔːɹz	jɔː(ɹ)
"""
    
    lines = test.strip().split('\n')

    for line in lines:
    
        word1, word2, str1, str2 = line.split('\t')
        print (word1, word2, str1, str2, weighted_ipa_lev(str1, str2))

