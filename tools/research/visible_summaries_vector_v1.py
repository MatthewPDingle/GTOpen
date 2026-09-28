"""Vectorized visible-card summaries; preserve all original feature semantics."""
import numpy as np
from sampled_visible_poker_features_v1 import WIDTH

STARTS=np.asarray([v for i in range(7) for v in (19*i,19*i+14)]+[133,135,139]+[155+6*i for i in range(19)],dtype=np.int16)
WIDTHS=np.asarray([14,5]*7+[2,4,16]+[6]*19,dtype=np.int16)
PATTERNS=np.zeros((10,13),dtype=np.int16)
for i,high in enumerate(range(4,13)):PATTERNS[i,high-4:high+1]=1
PATTERNS[9,[12,0,1,2,3]]=1
HIGHS=np.asarray([*range(4,13),3])


def summaries(cards):
    """Input: [N,7], missing board cards padded with 52, two private cards first."""
    cards=np.asarray(cards)
    if cards.ndim!=2 or cards.shape[1]!=7 or cards.dtype.kind not in 'iu':raise ValueError('Seven integer card slots required')
    if np.any((cards<0)|(cards>52)) or np.any(cards[:,:2]>=52):raise ValueError('Invalid private or board card')
    live=cards<52;board_n=live[:,2:].sum(1)
    if np.any(~np.isin(board_n,[0,3,4,5])) or np.any(live[:,2:]!=(np.arange(5)[None,:]<board_n[:,None])):raise ValueError('Invalid visible board padding')
    ordered=np.sort(cards,axis=1)
    if np.any((ordered[:,1:]==ordered[:,:-1])&(ordered[:,1:]<52)):raise ValueError('Duplicate visible cards')
    n=len(cards);x=np.zeros((n,WIDTH),dtype=np.float64)
    if n==0:return x.astype(np.float32)
    rank=cards//4;suit=cards%4;ids=np.arange(n)[:,None]
    count=np.zeros((n,14),dtype=np.int16);np.add.at(count,(ids,rank),live.astype(np.int16));count=count[:,:13]
    board=np.zeros((n,14),dtype=np.int16);np.add.at(board,(ids,rank[:,2:]),live[:,2:].astype(np.int16));board=board[:,:13]
    suit_rank=np.zeros((n,4,14),dtype=np.int16)
    np.add.at(suit_rank,(ids,suit,rank),live.astype(np.int16));suit_rank=suit_rank[:,:,:13]
    br_suit=np.zeros((n,4),dtype=np.int16);np.add.at(br_suit,(ids,suit[:,2:]),live[:,2:].astype(np.int16))
    ho_suit=np.zeros((n,4),dtype=np.int16);np.add.at(ho_suit,(ids,suit[:,:2]),1)
    r=np.arange(13)[None,:];present=count>0
    def descending(mask):return np.sort(np.where(mask,r,-1),axis=1)[:,::-1]
    high=descending(present);pairs=descending(count>=2);trips=descending(count>=3);quads=descending(count==4)
    coverage=present.astype(np.int16)@PATTERNS.T;board_coverage=(board>0).astype(np.int16)@PATTERNS.T
    straight=np.where(coverage==5,HIGHS[None,:],-1).max(1)
    suit_counts=suit_rank.sum(2);flush_suit=suit_counts.argmax(1)
    flush_present=suit_rank[np.arange(n),flush_suit,:]>0
    flush_cards=descending(flush_present);is_flush=suit_counts.max(1)>=5
    sf_coverage=flush_present.astype(np.int16)@PATTERNS.T
    sf_high=np.where(sf_coverage==5,HIGHS[None,:],-1).max(1)
    category=np.zeros(n,dtype=int);tie=high[:,:5].copy()
    def assign(mask,cat,values):
        category[mask]=cat;tie[mask]=-1;tie[np.flatnonzero(mask)[:,None],np.arange(values.shape[1])[None,:]]=values[mask]
    kick=descending(present&(r!=pairs[:,0,None]));assign(pairs[:,0]>=0,1,np.column_stack((pairs[:,0],kick[:,:3])))
    kick=descending(present&(r!=pairs[:,0,None])&(r!=pairs[:,1,None]));assign(pairs[:,1]>=0,2,np.column_stack((pairs[:,:2],kick[:,0])))
    kick=descending(present&(r!=trips[:,0,None]));assign(trips[:,0]>=0,3,np.column_stack((trips[:,0],kick[:,:2])))
    assign(straight>=0,4,straight[:,None]);assign(is_flush,5,flush_cards[:,:5])
    partner=np.where(pairs[:,0]==trips[:,0],pairs[:,1],pairs[:,0]);assign((trips[:,0]>=0)&(partner>=0),6,np.column_stack((trips[:,0],partner)))
    kick=descending(present&(r!=quads[:,0,None]));assign(quads[:,0]>=0,7,np.column_stack((quads[:,0],kick[:,0])))
    assign(is_flush&(sf_high>=0),8,sf_high[:,None])
    x[np.arange(n),category]=1.;x[:,9:14]=(tie+1)/13
    x[:,14:17]=np.sort(board,axis=1)[:,-3:][:,::-1]/4
    order=np.argsort(br_suit*3+ho_suit,axis=1)[:,::-1]
    x[:,17:25:2]=np.take_along_axis(br_suit,order,axis=1)/5
    x[:,18:25:2]=np.take_along_axis(ho_suit,order,axis=1)/2
    board_high=np.where(board>0,r,-1).max(1)
    x[:,25]=coverage.max(1)/5;x[:,26]=board_coverage.max(1)/5
    x[:,27]=(rank[:,:2]>board_high[:,None]).sum(1)/2
    x[:,28]=(board[ids,rank[:,:2]]>0).sum(1)/2
    x[:,29]=rank[:,0]==rank[:,1];x[:,30]=suit[:,0]==suit[:,1]
    x[:,31]=(board>0).sum(1)/5;x[:,32]=(board_high+1)/13
    x[board_n==0]=0
    assert np.isfinite(x).all() and np.all((x>=0)&(x<=1))
    return x.astype(np.float32)


def features(observations):
    """Original one-hot validation, with batched rather than scalar summaries."""
    n=len(observations)
    if n==0:return np.zeros((0,269+WIDTH),dtype=np.float32)
    rows=[o['active_features'] for o in observations]
    if any(len(row)!=36 or any(type(a) is not int or not 0<=a<269 for a in row) for row in rows):raise ValueError('Invalid original feature row')
    active=np.sort(np.asarray(rows,dtype=np.int16),axis=1);selected=active-STARTS
    if np.any(selected<0) or np.any(selected>=WIDTHS):raise ValueError('Invalid one-hot group')
    ranks=selected[:,:14:2];suits=selected[:,1:14:2];missing=ranks==13
    if np.any(missing!=(suits==4)):raise ValueError('Mismatched missing card')
    counts=np.asarray([0,3,4,5],dtype=np.int16)[selected[:,15]]+2
    if np.any(missing!=(np.arange(7)[None,:]>=counts[:,None])):raise ValueError('Future-card leakage or incomplete visible board')
    history=selected[:,17:];after_end=np.maximum.accumulate(history==0,axis=1)
    if np.any(after_end&(history!=0)):raise ValueError('Noncontiguous public history')
    cards=ranks*4+suits;cards[missing]=52;ordered=np.sort(cards,axis=1)
    if np.any((ordered[:,1:]==ordered[:,:-1])&(ordered[:,1:]!=52)):raise ValueError('Distinct visible cards required')
    cards[:,:2]=np.sort(cards[:,:2],axis=1);cards[:,2:]=np.sort(cards[:,2:],axis=1)
    unique,inverse=np.unique(cards,axis=0,return_inverse=True);extra=summaries(unique)
    x=np.zeros((n,269+WIDTH),dtype=np.float32);x[np.arange(n)[:,None],active]=1.;x[:,269:]=extra[inverse]
    return x
