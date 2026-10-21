// ---- who this is for: 18 and over, outside the United States; confirmed once per browser ----
(function attest(){
  let ok=false; try{ ok=localStorage.getItem("ubik-attest")==="1"; }catch(e){}
  const d=document.getElementById("attest"); if(!d||ok) return;
  d.showModal();
  d.querySelector(".yes").addEventListener("click",()=>{ try{ localStorage.setItem("ubik-attest","1"); }catch(e){} d.close(); });
  d.querySelector(".no").addEventListener("click",()=>{ location.href="https://ubikistan.github.io/archive/"; });
})();
function notAvailable(){ const el=document.getElementById("stamp"); if(el) el.textContent="NOT AVAILABLE IN THE UNITED STATES"; const g=document.getElementById("gate"); if(g) g.innerHTML='<span class="gstate locked">NOT AVAILABLE IN THE UNITED STATES</span>'; }
