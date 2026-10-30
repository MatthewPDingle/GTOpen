"""Decode every layout word and compare complete original/reference images."""
import hashlib,struct,sys
from pathlib import Path

def replay(path,fixture_index,native_words):
    data=Path(path).read_bytes();offset=0;checks=0;encoded=0;images=[]
    def take(n):
        nonlocal offset
        assert n>=0 and offset+n<=len(data),(offset,n,len(data))
        v=memoryview(data)[offset:offset+n];offset+=n;return v
    def number(fmt):return struct.unpack(fmt,take(struct.calcsize(fmt)))[0]
    assert bytes(take(16))==b'D131-LAYOUT-R1\0\0'
    assert number('<I')==fixture_index and number('<I')==2
    for player in range(2):
        count=number('<Q');actual=take(count*8)
        other_count=number('<Q');expected=take(other_count*8)
        assert count==other_count and actual==expected;checks+=count;encoded+=count*2
        assert sys.byteorder=='little';words=actual.cast('Q');j=0
        def word():
            nonlocal j
            assert j<len(words);v=words[j];j+=1;return v
        compact=word();arena_len=word();assert compact in[0,1]
        sizes=[]
        for _ in range(3):
            length=word();capacity=word();assert capacity>=length;sizes.append(length)
        active,copies,inactive=sizes
        for _ in range(active):
            node,host,device,length=[word()for _ in range(4)]
            assert node<=0xffffffff and device+length<=arena_len
        for _ in range(copies):
            host,device,length=[word()for _ in range(3)]
            assert device+length<=arena_len
        for _ in range(inactive):
            node,host,length,initial0,initial1=[word()for _ in range(5)]
            assert node<=0xffffffff and initial0==initial1==0xffffffffffffffff
        for array_index in range(3):
            length=word();capacity=word();assert capacity>=length
            if array_index<2:assert length==0
            for _ in range(length):assert word()==0
        assert j==count
        images.append({'player':player,'compact':bool(compact),'arena_len':arena_len,'active_blocks':active,'copy_spans':copies,'inactive_blocks':inactive,'words_per_arm':count,'image_sha256':hashlib.sha256(actual).hexdigest()})
    assert offset==len(data) and sum(x['words_per_arm']for x in images)==native_words
    return {'status':'pass_all_layout_words_capacities_and_frames','raw_bytes':len(data),'encoded_words':encoded,'checks':checks,'images':images,'raw_sha256':hashlib.sha256(data).hexdigest()}
