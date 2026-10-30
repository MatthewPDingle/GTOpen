"""Vectorized equivalent of the frozen 33 visible-card summaries; CPU only."""
import numpy as np

WIDTH=33
RANKS=np.arange(13,dtype=np.int16)
STRAIGHTS=np.array([[r in range(hi-4,hi+1) for r in range(13)] for hi in range(4,13)]
    + [[r in (12,0,1,2,3) for r in range(13)]],dtype=np.int16)
HIGHS=np.array(list(range(4,13))+[3],dtype=np.int16)

def _top(present,k):
    return np.sort(np.where(present,RANKS,-1),axis=1)[:,::-1][:,:k]

def _straight(present):
    counts=present.astype(np.int16)@STRAIGHTS.T
    return np.max(np.where(counts==5,HIGHS,-1),axis=1),np.max(counts,axis=1)

def summaries(cards):
    """n x 7 integer cards, hole first, unseen trailing board cards encoded 52."""
    cards=np.asarray(cards)
    if cards.ndim!=2 or cards.shape[1]!=7 or cards.dtype.kind not in 'iu':
        raise ValueError('Seven integer card slots required')
    if not len(cards):return np.zeros((0,WIDTH),dtype=np.float32)
    if np.any(cards>52) or np.any(cards<0):raise ValueError('Card outside deck')
    missing=cards==52;nvisible=np.sum(~missing,axis=1)
    if np.any(~np.isin(nvisible,[2,5,6,7])) or np.any(missing!=(np.arange(7)[None,:]>=nvisible[:,None])):
        raise ValueError('Two hole cards and zero, three, four or five board cards required')
    ordered=np.sort(cards,axis=1)
    if np.any((ordered[:,1:]==ordered[:,:-1])&(ordered[:,1:]!=52)):
        raise ValueError('Duplicate visible card')
    result=np.zeros((len(cards),WIDTH),dtype=np.float32)
    live=nvisible>2
    if not np.any(live):return result
    c=cards[live].astype(np.int16,copy=False);n=len(c);rank=c//4;suit=c%4;valid=c!=52
    counts=np.sum((rank[:,:,None]==RANKS)&valid[:,:,None],axis=1)
    board_counts=np.sum((rank[:,2:,None]==RANKS)&valid[:,2:,None],axis=1)
    present=counts>0;board_present=board_counts>0
    suit_ids=np.arange(4,dtype=np.int16)
    board_suits=np.sum((suit[:,2:,None]==suit_ids)&valid[:,2:,None],axis=1)
    hole_suits=np.sum(suit[:,:2,None]==suit_ids,axis=1)
    flush_suit=np.argmax(board_suits+hole_suits,axis=1)
    flush=np.max(board_suits+hole_suits,axis=1)>=5
    flush_ranks=np.any((rank[:,:,None]==RANKS)&valid[:,:,None]&(suit==flush_suit[:,None])[:,:,None],axis=1)
    straight,coverage=_straight(present);straight_flush,_=_straight(flush_ranks)
    _,board_coverage=_straight(board_present)
    trips=_top(counts>=3,1)[:,0];quads=_top(counts==4,1)[:,0];pairs=_top(counts>=2,2)
    other_pair=_top((counts>=2)&(RANKS!=trips[:,None]),1)[:,0]
    category=np.zeros(n,dtype=np.int16);tie=_top(present,5).copy()
    pair=pairs[:,0]>=0
    category[pair]=1;tie[pair]=np.column_stack((pairs[pair,0],_top(present[pair]&(RANKS!=pairs[pair,0,None]),3),np.full(np.count_nonzero(pair),-1)))
    two_pair=pairs[:,1]>=0
    category[two_pair]=2
    kept=present[two_pair]&(RANKS!=pairs[two_pair,0,None])&(RANKS!=pairs[two_pair,1,None])
    tie[two_pair]=np.column_stack((pairs[two_pair],_top(kept,1),np.full((np.count_nonzero(two_pair),2),-1)))
    three=trips>=0;category[three]=3
    kept=present[three]&(RANKS!=trips[three,None])
    tie[three]=np.column_stack((trips[three],_top(kept,2),np.full((np.count_nonzero(three),2),-1)))
    straight_rows=straight>=0;category[straight_rows]=4
    tie[straight_rows]=np.column_stack((straight[straight_rows],np.full((np.count_nonzero(straight_rows),4),-1)))
    category[flush]=5;tie[flush]=_top(flush_ranks[flush],5)
    full=three&(other_pair>=0);category[full]=6
    tie[full]=np.column_stack((trips[full],other_pair[full],np.full((np.count_nonzero(full),3),-1)))
    four=quads>=0;category[four]=7
    kept=present[four]&(RANKS!=quads[four,None])
    tie[four]=np.column_stack((quads[four],_top(kept,1),np.full((np.count_nonzero(four),3),-1)))
    sf=flush&(straight_flush>=0);category[sf]=8
    tie[sf]=np.column_stack((straight_flush[sf],np.full((np.count_nonzero(sf),4),-1)))
    x=np.zeros((n,WIDTH),dtype=np.float32);x[np.arange(n),category]=1.
    x[:,9:14]=(tie+1)/13
    x[:,14:17]=np.sort(board_counts,axis=1)[:,::-1][:,:3]/4
    groups=np.sort(board_suits*3+hole_suits,axis=1)[:,::-1]
    x[:,17:25:2]=(groups//3)/5;x[:,18:25:2]=(groups%3)/2
    board_high=_top(board_present,1)[:,0]
    x[:,25]=coverage/5;x[:,26]=board_coverage/5
    x[:,27]=np.sum(rank[:,:2]>board_high[:,None],axis=1)/2
    x[:,28]=np.sum(np.take_along_axis(board_present,rank[:,:2],axis=1),axis=1)/2
    x[:,29]=rank[:,0]==rank[:,1];x[:,30]=suit[:,0]==suit[:,1]
    x[:,31]=np.sum(board_present,axis=1)/5;x[:,32]=(board_high+1)/13
    assert np.isfinite(x).all() and np.all((x>=0)&(x<=1))
    result[live]=x
    return result
