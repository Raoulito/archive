NEXT_RECHECK=()=>{ if(SHOWING==="current") return loadCurrent().then(loadEditions); };
// boot: the inlined public snapshot first, then the desk
loadCurrent().then(loadEditions).catch(()=>{ LIVE=false; const st=document.getElementById("stamp"); if(st) st.textContent=`EDITION ${EDITION_DAY} · SNAPSHOT · THE DESK DID NOT ANSWER`; loadEditions().catch(()=>{}); });
