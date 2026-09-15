// A separate what-if study. Never writes its policy into the main game.
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function request(endpoint, body) {
  const r = await fetch(`/api/preflop/focus/${endpoint}`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
export function branchWarning(view) {
  if (!view?.low_reach) return '';
  const p = view.branch_probability;
  const frequency = p > 0 ? `${(p * 100).toPrecision(3)}%` : '0%';
  return `Rare branch · ${frequency} modeled reach. The whole-game accuracy target does not establish accuracy here. Treat these responses as unverified.`;
}

export async function openFocusedStudy(path, toast) {
  const dialog = document.createElement('dialog');
  dialog.className = 'pfl-focus-dialog';
  dialog.innerHTML = `<header><h2>Focused preflop study</h2><button type="button" class="btn sm" data-close>Close</button></header><p class="dim">Preparing this branch…</p><div data-body></div>`;
  document.body.append(dialog);dialog.showModal();
  let id = null, running = false, closed = false, timer = null, localPath = [];
  const tip = document.createElement('div');tip.className='pfl-focus-tip hidden';dialog.append(tip);
  function close() {
    if (closed) return;
    closed=true;clearTimeout(timer);
    if (running && id) request('stop',{id}).catch(()=>{});
    dialog.close();dialog.remove();
  }
  dialog.querySelector('[data-close]').onclick=close;
  dialog.addEventListener('cancel',e=>{e.preventDefault();close();});
  const body = dialog.querySelector('[data-body]');
  const subtitle=dialog.querySelector('p');
  try {
    const prepared=await request('plan',{path});
    if (closed) return;
    id=prepared.id;const plan=prepared.plan;
    subtitle.textContent=`Separate what-if study · source iteration ${plan.source_iteration} · ${plan.nodes.toLocaleString()} nodes`;
    body.innerHTML=`<p><strong>${esc(plan.line.join(' → '))}</strong></p><details open data-assumptions><summary>Incoming ranges and assumptions</summary><p>The incoming ranges below are assumptions for this study. Review the jammer’s range especially: an almost-unused jam can leave an unreliable range. Changing a range here does not change your game.</p>
      <div class="pfl-focus-ranges">${plan.positions.map((p,i)=>plan.live[i]?`<details><summary>${esc(p)} · incoming range</summary><textarea aria-label="${esc(p)} incoming range" data-seat="${i}" rows="3" spellcheck="false">${esc(plan.ranges[i])}</textarea></details>`:'').join('')}</div>
      <p class="dim">Range syntax: QQ+, AKs, AKo:0.5. Weights describe relative hand frequencies; the study normalizes each range. Suit-specific entries are pooled into hand classes.</p>
      <p class="dim">Existing models and locks stay fixed (${plan.fixed_decisions} decisions). Heads-up equity and the game’s multiway approximation are retained. This is a conditional model result, not a new full-game equilibrium.</p></details>
      <div class="pfl-focus-controls"><button class="btn sm primary" data-start>Run focused study</button><button data-cancel class="btn sm hidden">Cancel</button><span role="status" data-status></span></div>
      <progress class="hidden" max="2000" value="0" aria-label="Focused solve iteration budget"></progress><div data-result></div>`;
    const start=body.querySelector('[data-start]'),cancel=body.querySelector('[data-cancel]'),status=body.querySelector('[data-status]'),progress=body.querySelector('progress');
    cancel.onclick=async()=>{cancel.disabled=true;status.textContent='Cancelling…';try{await request('stop',{id});}catch(e){status.textContent=e.message;}};
    start.onclick=async()=>{
      start.disabled=true;
      const ranges=[...plan.ranges];body.querySelectorAll('textarea').forEach(t=>{ranges[Number(t.dataset.seat)]=t.value;});
      try {
        await request('start',{id,ranges});
        if(closed){request('stop',{id}).catch(()=>{});return;}
        running=true;body.querySelector('[data-assumptions]').open=false;cancel.classList.remove('hidden');progress.classList.remove('hidden');
        body.querySelectorAll('textarea').forEach(t=>t.disabled=true);
        await poll();
      } catch(e) {status.textContent=e.message;start.disabled=false;}
    };
    async function poll() {
      if(closed)return;
      try {
        const s=await request('status',{id});if(closed)return;
        progress.value=s.iteration;
        const gap=s.gap==null?'measuring local accuracy…':`local gap ${s.gap.toFixed(4)} bb`;
        status.textContent=`${s.iteration} / ${s.max_iterations} iterations · ${s.seconds.toFixed(1)}s · ${gap}`;
        if(s.state==='running'){timer=setTimeout(poll,600);return;}
        running=false;cancel.classList.add('hidden');progress.classList.add('hidden');
        if(s.state==='done'||s.state==='limit_reached'){
          status.textContent=`${s.state==='done'?'Local target reached':'Iteration limit reached — approximate result'} · ${s.iteration} iterations · ${s.seconds.toFixed(1)}s · ${gap}`;
          start.textContent='Study complete';await showNode();
        }else{status.textContent=s.state==='cancelled'?'Cancelled. Your main game is unchanged.':s.error;start.textContent='Close and open a new study to retry';}
      } catch(e){status.textContent=e.message;timer=setTimeout(poll,1500);}
    }
    async function showNode() {
      tip.classList.add('hidden');
      const v=await request('node',{id,path:localPath});if(closed)return;
      const out=body.querySelector('[data-result]');
      v.actions=v.actions.map(a=>({...a,label:a.kind==='call'?`Call ${(a.to-v.invested[v.actor]+(plan.ante||0)).toFixed(1)} bb`:(a.kind==='jam'||a.kind==='raise')?`${a.kind==='jam'?'All-in':'Raise to'} ${a.to} bb`:a.label}));
      const colors=v.actions.map(a=>a.kind==='fold'?'#4a78c8':a.kind==='call'||a.kind==='check'?'#5ca75f':a.kind==='jam'?'#7c3134':'#e8484c');
      out.innerHTML=`<div class="pfl-focus-controls"><button class="btn sm" data-back ${localPath.length?'':'disabled'}>← Back</button><strong>${esc(v.actor_pos||'End of preflop line')} · ${v.pot.toFixed(1)} bb pot</strong></div>
        ${v.low_reach?`<p class="pfl-focus-warning">${esc(branchWarning(v))}</p>`:''}
        <div class="pfl-focus-controls">${v.actions.map((a,i)=>`<button class="btn sm" data-action="${i}"><i style="background:${colors[i]}"></i>${esc(a.label)} · ${(a.freq*100).toFixed(1)}%</button>`).join('')}</div><div class="pfl-focus-grid"></div>`;
      out.querySelector('[data-back]').onclick=()=>{localPath.pop();showNode().catch(e=>toast(e.message,true));};
      out.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{localPath.push(Number(b.dataset.action));showNode().catch(e=>toast(e.message,true));});
      if(!v.strategy){out.querySelector('.pfl-focus-grid').textContent=v.strategy_note||'No further preflop decisions.';return;}
      const grid=out.querySelector('.pfl-focus-grid'),ranks='23456789TJQKA';
      for(let row=12;row>=0;row--)for(let col=12;col>=0;col--){
        const h=row*13+col,name=ranks[Math.max(row,col)]+ranks[Math.min(row,col)]+(row===col?'':row>col?'s':'o');
        const f=v.actions.map((_,a)=>v.strategy[a*169+h]*100);let at=0;
        const stops=f.map((x,a)=>{const old=at;at+=x;return `${colors[a]} ${old}% ${at}%`;});
        const cell=document.createElement('div');cell.className='pfl-focus-cell';cell.tabIndex=0;cell.textContent=name;
        cell.style.background=`linear-gradient(to right,${stops.join(',')})`;
        if(v.reach?.[h]===0)cell.style.opacity='0.25';
        cell.setAttribute('aria-label',`${name}: ${v.actions.map((a,i)=>`${a.label} ${f[i].toFixed(1)}%`).join(', ')}`);
        function show(){tip.innerHTML=`<strong>${name}</strong>${v.actions.map((a,i)=>`<div><span><i style="background:${colors[i]}"></i>${esc(a.label)}</span><b>${f[i].toFixed(1)}%</b></div>`).join('')}`;tip.classList.remove('hidden');const r=cell.getBoundingClientRect();tip.style.left=`${Math.max(8,Math.min(r.right+8,innerWidth-tip.offsetWidth-12))}px`;tip.style.top=`${Math.max(8,Math.min(r.top,innerHeight-tip.offsetHeight-12))}px`;}
        cell.onmouseenter=show;cell.onfocus=show;cell.onmouseleave=()=>tip.classList.add('hidden');cell.onblur=cell.onmouseleave;grid.append(cell);
      }
    }
  }catch(e){if(!closed){subtitle.textContent=e.message;toast(e.message,true);}}
}
