import assert from 'node:assert/strict';
import { blindPosts, unraisedWinner } from '../web/js/preflop_blinds.js';
import { formatPreflopView } from '../web/js/preflop_actions.js';
const positions = ['BTN', 'SB', 'BB'];
assert.deepEqual(blindPosts(positions, {smallBlind:2,bigBlind:2}), [0,1,1]);
assert.deepEqual(blindPosts(positions, {smallBlind:2,bigBlind:5}), [0,.4,1]);
assert.deepEqual(blindPosts(positions, {}), [0,.5,1]);
for (const [smallBlind,bigBlind] of [[0,2],[3,2],[2,0],[NaN,2]])
  assert.throws(() => blindPosts(positions, {smallBlind,bigBlind}));
const call = to => ({kind:'call',to,label:`Limp ${to}`,freq:1});
for (const [posted, expected] of [[.5,'Complete 0.5 bb'],[.4,'Complete 0.6 bb']]) {
 const v = {positions,history:[{actor_pos:'SB',actions:[call(1)],chosen:null}]};
 assert.equal(formatPreflopView(v,{posts:[0,posted,1],ante:.1}).actions[0].label, expected);
}
const view = {positions, history:[
 {actor_pos:'BTN',actions:[call(1)],chosen:0},
 {actor_pos:'SB',actions:[{kind:'raise',to:7.5,label:'Raise 7.5',freq:1}],chosen:0},
 {actor_pos:'BTN',actions:[call(7.5),{kind:'raise',to:22.5,label:'3-bet 22.5',freq:0}],chosen:null},
]};
const original = JSON.stringify(view);
const formatted = formatPreflopView(view, {posts:[0,.5,1]});
assert.equal(formatted.actions[0].label,'Call 6.5 bb');
assert.equal(formatted.actions[1].label,'3-bet 3x');
assert.equal(formatted.actions[0].to,7.5);
assert.equal(JSON.stringify(view),original);
assert.equal(formatPreflopView({positions,history:[{actor_pos:'SB',actions:[{kind:'check',to:1,label:'Check'}]}]}, {posts:[0,1,1]}).actions[0].label,'Check');
console.log('Blind ratios, completion amounts, raise multiples, and immutable actions passed.');

const straddled = ['UTG','BTN','SB','BB'];
assert.deepEqual(blindPosts(straddled,{smallBlind:2,bigBlind:5,straddle:2}),[2,0,.4,1]);
assert.deepEqual(blindPosts(positions,{smallBlind:2,bigBlind:2,straddle:3}),[3,1,1]);
for (const straddle of [1,-1,NaN,Infinity]) assert.throws(()=>blindPosts(straddled,{straddle}));
assert.throws(()=>blindPosts(['SB','BB'],{straddle:2}));
assert.equal(unraisedWinner({utg_straddle:true},straddled),0);
assert.equal(unraisedWinner({},straddled),3);
for (const [actor,expected] of [['SB','Complete 1.5 bb'],['BB','Complete 1 bb'],['BTN','Limp 2 bb']]) {
 const v={positions:straddled,history:[{actor_pos:actor,actions:[call(2)],chosen:null}]};
 assert.equal(formatPreflopView(v,{posts:[2,0,.5,1]}).actions[0].label,expected);
}
assert.equal(formatPreflopView({positions:straddled,history:[{actor_pos:'BTN',actions:[{kind:'raise',to:5,label:'Raise 5'}]}]}, {posts:[2,0,.5,1]}).actions[0].label,'Raise 5x');
console.log('UTG straddle posts, validation, incremental calls, original-bb sizes, and unopened winner passed.');
