NEXT_RECHECK=()=>{ if(SHOWING==="current") return loadCurrent().then(loadEditions); };
// boot: load live data first; fallback to snapshot only on error or slow network (>2.5s)
let booted=false;
const bootTimer=setTimeout(()=>{
  if(!booted){
    booted=true;
    applyEdition(SNAPSHOT,"current");
    LIVE=false;
    const st=document.getElementById("stamp"); if(st) st.textContent=`EDITION ${EDITION_DAY} · SNAPSHOT · THE DESK DID NOT ANSWER`;
    if(!route()){ let v=null, reader=null; try{ v=localStorage.getItem("ubik-view"); reader=localStorage.getItem("ubik-reader"); }catch(e){} if(v==="chat") v="agent"; if(v==="mine") v="ledger"; go(v||(reader==="human"?"edition":"agent")); if(!reader) showCover(false); }
  }
}, 2500);

loadCurrent().then(loadEditions).then(()=>{
  booted=true; clearTimeout(bootTimer);
  if(!route()){ let v=null, reader=null; try{ v=localStorage.getItem("ubik-view"); reader=localStorage.getItem("ubik-reader"); }catch(e){} if(v==="chat") v="agent"; if(v==="mine") v="ledger"; go(v||(reader==="human"?"edition":"agent")); if(!reader) showCover(false); }
}).catch(()=>{
  booted=true; clearTimeout(bootTimer);
  applyEdition(SNAPSHOT,"current");
  LIVE=false;
  const st=document.getElementById("stamp"); if(st) st.textContent=`EDITION ${EDITION_DAY} · SNAPSHOT · THE DESK DID NOT ANSWER`;
  if(!route()){ let v=null, reader=null; try{ v=localStorage.getItem("ubik-view"); reader=localStorage.getItem("ubik-reader"); }catch(e){} if(v==="chat") v="agent"; if(v==="mine") v="ledger"; go(v||(reader==="human"?"edition":"agent")); if(!reader) showCover(false); }
  loadEditions().catch(()=>{});
});
