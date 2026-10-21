// ---- market prices, read through the desk from Polymarket's public data; never linked ----
// The mapping from a UBIK question to a contract is hand-made. `adj` marks a contract on a neighbouring
// question, not the same one; `invert` reads the contract's NO side (1 − YES price) as the question's YES.
const MKT_MAP={
 "q_20261020_02":{venue:"Polymarket", pm:"2364962", c:"Trump and Putin meet next in China, by 31 Dec", adj:true},
 "q_20261020_03":{venue:"Polymarket", pm:"5686978", c:"US × Iran ceasefire continues through 22 Nov, read as 1 − price", adj:true, invert:true},
 "q_20261019_04":{venue:"Polymarket", pm:"5458389", c:"Moody's or S&P downgrades France by 31 Oct, read as 1 − price", adj:true, invert:true},
 "q_20261018_03":{venue:"Polymarket", pm:"3940930", c:"Bank of Korea holds at the November meeting"},
};
let MKT={};
async function loadMarkets(){
  const ids=[...new Set(Object.values(MKT_MAP).map(m=>m.pm))]; if(!ids.length) return;
  const {body}=await deskGet("/markets?pm="+ids.join(","),false); const got={};
  for(const [q,m] of Object.entries(MKT_MAP)){ const r=(body.markets||{})[m.pm]; if(r&&r.yes!=null&&!r.closed){ got[q]={venue:m.venue, p:m.invert?+(1-r.yes).toFixed(3):r.yes, c:m.c, adj:!!m.adj, t:r.read.slice(0,10), read:r.read.slice(0,10), vol:"", url:r.slug?"https://polymarket.com/market/"+r.slug:null}; } }
  MKT=got;
}
