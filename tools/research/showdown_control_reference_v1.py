"""Independent best-of-21 five-card showdown reference for research readbacks."""
import itertools
from collections import Counter


def five(cards):
    ranks=[c//4 for c in cards];counts=Counter(ranks)
    groups=sorted(((n,r) for r,n in counts.items()),reverse=True)
    unique=sorted(counts)
    straight=None
    if len(unique)==5:
        if unique[-1]-unique[0]==4:straight=unique[-1]
        elif unique==[0,1,2,3,12]:straight=3
    flush=len({c%4 for c in cards})==1
    if flush and straight is not None:return (8,straight)
    if groups[0][0]==4:return (7,groups[0][1],groups[1][1])
    if [x[0] for x in groups]==[3,2]:return (6,groups[0][1],groups[1][1])
    if flush:return (5,*sorted(ranks,reverse=True))
    if straight is not None:return (4,straight)
    if groups[0][0]==3:return (3,groups[0][1],*sorted((r for r in ranks if r!=groups[0][1]),reverse=True))
    pairs=sorted((r for r,n in counts.items() if n==2),reverse=True)
    if len(pairs)==2:return (2,*pairs,next(r for r,n in counts.items() if n==1))
    if pairs:return (1,pairs[0],*sorted((r for r,n in counts.items() if n==1),reverse=True))
    return (0,*sorted(ranks,reverse=True))


def score(deal):
    if len(deal)!=9 or len(set(deal))!=9 or any(type(x)!=int or not 0<=x<52 for x in deal):
        raise ValueError('Nine distinct physical cards required')
    a=max(five(c) for c in itertools.combinations(deal[:2]+deal[4:],5))
    b=max(five(c) for c in itertools.combinations(deal[2:4]+deal[4:],5))
    return 2 if a>b else 1 if a==b else 0


def self_test():
    fixtures=[([48,49,44,45,0,5,22,31,40],2),([44,45,48,49,0,5,22,31,40],0),
              ([0,5,10,15,32,36,40,44,48],1),([48,1,44,45,6,11,12,29,38],2)]
    for cards,expected in fixtures:assert score(cards)==expected
    # Explicitly cover all nine five-card category branches, including kickers.
    hands=[([0,5,14,23,32],0),([48,49,4,10,19],1),([48,49,44,45,0],2),
           ([48,49,50,44,0],3),([0,5,10,15,16],4),([0,8,20,28,40],5),
           ([48,49,50,44,45],6),([48,49,50,51,0],7),([32,36,40,44,48],8)]
    for cards,category in hands:assert five(cards)[0]==category
    assert five([48,49,44,40,36])>five([48,49,44,40,32])
    return {'passed':True,'known_showdowns':len(fixtures),'five_card_categories':9,'kicker_order':True}
