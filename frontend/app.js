const API = "http://127.0.0.1:8000";
const $ = id => document.getElementById(id);
const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
$("today").textContent = new Date().toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric",year:"numeric"});
$("date").value = new Date(Date.now()+86400000).toISOString().slice(0,10);

async function api(path, options={}) {
  const response = await fetch(API + path, options);
  const body = await response.json().catch(()=>({detail:"The API returned an invalid response."}));
  if(!response.ok) throw new Error(body.detail || "API request failed.");
  return body;
}
function showError(message){ $("form-error").textContent = message; }
async function loadDashboard(){
  try{
    const [health,stats,locations,recent] = await Promise.all([
      api("/api/health"),api("/api/stats"),api("/api/locations"),api("/api/recent?limit=10")
    ]);
    $("api-status").textContent = "Connected · " + health.dataset_rows.toLocaleString() + " rows";
    $("records").textContent = stats.rows.toLocaleString();
    $("locations").textContent = stats.locations_count;
    $("rain-rate").textContent = stats.rain_rate + "%";
    $("dry-rate").textContent = stats.dry_rate + "%";
    $("location").innerHTML = locations.locations.map(x=>`<option>${escapeHtml(x)}</option>`).join("");
    renderBars(stats.by_location);
    renderRecent(recent.records);
  }catch(e){
    $("api-status").textContent = "Offline — start backend";
    $("location-chart").innerHTML = `<div class="loading">Could not load data. Start the API at <b>127.0.0.1:8000</b>.</div>`;
    showError("Backend connection failed. Follow the README startup steps, then refresh this page.");
  }
}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function renderBars(items){
  $("location-chart").innerHTML = items.map(x=>`
    <div class="bar-item"><span>${escapeHtml(x.location)}</span>
    <div class="bar-track"><div class="bar-fill" style="width:${Math.min(100,x.rain_rate)}%"></div></div>
    <span class="bar-value">${x.rain_rate}%</span></div>`).join("");
}
function renderRecent(rows){
  $("recent-rows").innerHTML = rows.map(r=>`<tr>
    <td>${r.date}</td><td>${escapeHtml(r.location)}</td><td>${r.temperature}</td>
    <td>${r.humidity}%</td><td>${r.precipitation} mm</td>
    <td><span class="pill ${r.rain_tomorrow?"rain":"dry"}">${r.rain_tomorrow?"Rain":"No rain"}</span></td>
  </tr>`).join("");
}
$("prediction-form").addEventListener("submit",async e=>{
  e.preventDefault(); showError("");
  const btn=$("predict-btn"); btn.disabled=true; btn.innerHTML="Calculating…";
  const payload={
    location:$("location").value,date:$("date").value,
    temperature:Number($("temperature").value),humidity:Number($("humidity").value),
    wind_speed:Number($("wind").value),precipitation:Number($("precipitation").value),
    cloud_cover:Number($("cloud").value),pressure:Number($("pressure").value)
  };
  try{
    const result=await api("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    $("empty-result").hidden=true; $("result-content").hidden=false;
    $("result-outcome").textContent=result.label;
    $("result-outcome").style.color=result.prediction?"#4268e8":"#269c7c";
    $("probability").textContent=result.rain_probability+"%";
    $("meter-fill").style.width=result.rain_probability+"%";
    $("confidence").textContent=result.confidence+"%";
    $("result-note").textContent=result.model_note+" Forecast date: "+result.date+".";
  }catch(err){showError(err.message);}
  finally{btn.disabled=false;btn.innerHTML='Generate prediction <span>→</span>';}
});
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
loadDashboard();
