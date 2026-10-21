// ---- the next edition: ubik.gold publishes once a day at about the same hour, so the estimate is this edition's hour, a day on ----
let FIRST_AT="", NEXT_RECHECK=null, nextTimer=null, lastRecheck=0;
function nextEditionAt(){ if(!FIRST_AT) return null; const t=new Date(FIRST_AT).getTime(); if(isNaN(t)) return null; const now=Date.now(); let next=t+86400000; const overdue=next<=now; while(next+86400000<=now) next+=86400000; return {at:new Date(next), overdue}; }
function renderNextClock(){
  const el=document.getElementById("nextclock"); if(!el) return; const n=nextEditionAt(); if(!n){ el.textContent=""; el.title=""; return; }
  const hm=n.at.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",hour12:false}); const ms=n.at.getTime()-Date.now();
  if(n.overdue){ el.innerHTML=el.dataset.short!=null?`<i class="due"></i>NEXT DUE · ~${hm}`:`<i class="due"></i>NEXT EDITION DUE · USUALLY ~${hm}`; el.classList.add("overdue"); }
  else { const m=Math.max(1,Math.round(ms/60000)), h=Math.floor(m/60), mm=m%60; el.innerHTML=el.dataset.short!=null?`NEXT ~${hm} · ${h?h+"H ":""}${mm}M`:`NEXT EDITION ~${hm} · IN ${h?h+"H ":""}${mm}M`; el.classList.remove("overdue"); }
  el.title=`Estimated from this edition's publication time (${new Date(FIRST_AT).toLocaleString()}), a day on. ubik.gold sets the real hour.`;
  if(n.overdue&&NEXT_RECHECK&&Date.now()-lastRecheck>10*60000){ lastRecheck=Date.now(); Promise.resolve().then(NEXT_RECHECK).catch(()=>{}); }
}
function startNextClock(){ renderNextClock(); if(nextTimer) clearInterval(nextTimer); nextTimer=setInterval(renderNextClock,30000); }
