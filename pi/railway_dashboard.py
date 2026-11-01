#!/usr/bin/env python3
"""Local web dashboard for live railway-track defect detection on Raspberry Pi."""
from __future__ import annotations

import argparse
import csv
import threading
import time
from datetime import datetime
from pathlib import Path

import cv2
from flask import Flask, Response, jsonify, render_template_string, request, send_from_directory
from picamera2 import Picamera2
from ultralytics import YOLO


HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Railway Track Inspector</title>
<style>
:root{color-scheme:dark;--bg:#080d16;--panel:#101925;--line:#263749;--muted:#8ca0b5;--text:#edf5fa;--mint:#55e0ad;--red:#ff687b;--amber:#f6c76b}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 50% -30%,#1b3940 0%,transparent 48%),var(--bg);color:var(--text);font:14px Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;overflow:hidden}
header{height:68px;padding:0 22px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #253543;background:rgba(8,14,23,.9);box-shadow:0 8px 30px #0003}
.brand{display:flex;align-items:center;gap:12px}.mark{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(145deg,#1b554a,#173441);border:1px solid #397a68;color:var(--mint);font-size:20px}.title{font-size:17px;font-weight:750;letter-spacing:.015em}.subtitle{font-size:10px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase;margin-top:3px}.headright{display:flex;align-items:center;gap:10px}.tag{padding:7px 10px;border-radius:8px;border:1px solid var(--line);background:#111c28;color:#b7c7d5;font-size:11px;letter-spacing:.06em}.navlink{text-decoration:none}.navlink:hover{color:var(--mint);border-color:#397a68}.badge{display:flex;align-items:center;gap:7px;padding:8px 12px;border-radius:99px;border:1px solid #425162;color:#a9bac8;font-weight:700;font-size:11px;letter-spacing:.09em}.dot{width:7px;height:7px;background:#8191a1;border-radius:50%}.badge.live{color:var(--mint);border-color:#27705a;background:#10251f}.badge.live .dot{background:var(--mint);box-shadow:0 0 11px var(--mint)}
main{height:calc(100vh - 68px);max-width:1600px;margin:auto;padding:14px;display:grid;grid-template-columns:218px minmax(300px,1fr) 232px;gap:13px}.side{min-height:0;display:flex;flex-direction:column;gap:11px}.card,.camera-panel{background:linear-gradient(145deg,rgba(20,32,46,.98),rgba(12,21,32,.98));border:1px solid var(--line);border-radius:14px;box-shadow:0 12px 32px #0002}.card{padding:14px}.eyebrow{font-size:10px;color:#8fa6b8;letter-spacing:.15em;text-transform:uppercase;font-weight:700}.statusrow{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:12px}.status{font-size:13px;line-height:1.4;color:#cad6df}.state-chip{flex:none;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);border:1px solid #39495a;border-radius:99px;padding:5px 8px}.state-chip.live{color:var(--mint);border-color:#27705a}.state-chip.alert{color:var(--red);border-color:#723744}.model-name{margin-top:12px;font-size:13px;font-weight:650}.small{font-size:11px;line-height:1.5;color:var(--muted)}.controls{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}.button{min-height:42px;border:1px solid transparent;border-radius:9px;padding:9px 11px;background:linear-gradient(135deg,#5de1ae,#39ba92);color:#062219;font-weight:800;font-size:13px;cursor:pointer;box-shadow:0 5px 16px #44d4a328}.button:hover{filter:brightness(1.08)}.button.stop{background:#38202a;border-color:#66313f;color:#ffdfe4;box-shadow:none}.button.exit{grid-column:1/-1;background:#1b2835;border-color:#34495a;color:#d4e0e9;box-shadow:none}.button:disabled{opacity:.42;cursor:default;filter:saturate(.5)}.hint{margin-top:10px;padding-top:10px;border-top:1px solid #263647;color:#91a3b4;font-size:10px;line-height:1.45}
.camera-panel{min-width:0;min-height:0;display:flex;flex-direction:column;overflow:hidden;border-color:#324b54;background:linear-gradient(150deg,#111c28,#080d14)}.cam-head{height:52px;flex:none;display:flex;align-items:center;justify-content:space-between;padding:0 15px;border-bottom:1px solid #293947}.cam-title{font-size:12px;letter-spacing:.12em;font-weight:800}.cam-live{font-size:10px;color:var(--muted);display:flex;align-items:center;gap:7px}.live-light{height:7px;width:7px;border-radius:50%;background:#627386}.live-light.on{background:var(--red);box-shadow:0 0 12px #ff687b88}.cam-stage{position:relative;flex:1;min-height:0;display:flex;align-items:center;justify-content:center;overflow:hidden;background-color:#060a0f;background-image:linear-gradient(#14212a44 1px,transparent 1px),linear-gradient(90deg,#14212a44 1px,transparent 1px);background-size:32px 32px}.cam-stage:after{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse,transparent 50%,#02050a66 100%)}.feed{z-index:1;width:100%;height:100%;display:flex;align-items:center;justify-content:center}.feed img{display:none;width:100%;height:100%;object-fit:contain}.placeholder{z-index:1;max-width:320px;padding:24px;text-align:center;color:#94a8b9;font-size:13px;line-height:1.6}.placeholder:before{content:"◉";display:block;color:#55d9a9;font-size:34px;margin-bottom:8px}.cam-foot{height:42px;flex:none;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:0 14px;border-top:1px solid #293947;color:#9db0bf;font-size:10px}.footleft{display:flex;gap:14px}.signal{display:inline-flex;gap:6px;align-items:center}.signal i{width:6px;height:6px;border-radius:50%;background:var(--mint)}
.kpi{display:flex;align-items:flex-end;justify-content:space-between;margin-top:12px}.kpi-num{font-size:31px;line-height:1;font-weight:780;letter-spacing:-.04em}.kpi-unit{font-size:11px;color:var(--muted);padding-bottom:3px}.kpi.defect .kpi-num{color:var(--mint)}.kpi.defect.alert .kpi-num{color:var(--red)}.confrow{display:flex;align-items:center;justify-content:space-between;margin-top:12px}.confval{color:var(--mint);font-size:19px;font-weight:750}.threshold{width:100%;margin:12px 0 2px;accent-color:var(--mint)}.snap-card{flex:1;min-height:100px;display:flex;flex-direction:column;overflow:hidden}.snap{margin-top:10px;overflow:auto;min-height:0}.snap-entry{padding:8px 0;border-top:1px solid #263647}.snap-entry:first-child{border-top:0}.snap img{display:block;width:100%;border-radius:8px;margin-top:6px;border:1px solid #344554}.alerttxt{color:var(--red)}
@media(max-width:900px){main{grid-template-columns:185px minmax(240px,1fr) 195px;gap:9px;padding:9px}.card{padding:11px}.cam-head{height:44px}.cam-foot{height:36px}.title{font-size:15px}}
@media(max-width:700px){body{overflow:auto}header{height:58px;padding:0 11px}.tag{display:none}main{height:auto;min-height:calc(100vh - 58px);grid-template-columns:1fr;padding:9px}.camera-panel{height:55vh;min-height:300px;grid-row:1}.side{display:grid;grid-template-columns:1fr 1fr}.left-side{grid-row:2}.right-side{grid-row:3}.side .wide{grid-column:1/-1}.snap-card{min-height:180px}.cam-stage{min-height:220px}}
</style></head><body>
<header><div class="brand"><div class="mark">⌁</div><div><div class="title">Railway Track Inspector</div><div class="subtitle">On-device vision · Raspberry Pi 4</div></div></div><div class="headright"><a class="tag navlink" href="/">LIVE CONSOLE</a><a class="tag navlink" href="/review">PROJECT REVIEW</a><div class="badge" id="badge"><i class="dot"></i><span id="badgeText">STANDBY</span></div></div></header>
<main>
<aside class="side left-side">
  <section class="card"><div class="eyebrow">Inspection status</div><div class="statusrow"><div id="status" class="status">Detector stopped</div><div id="stateChip" class="state-chip">Idle</div></div><div class="hint">Camera stays fixed while the model analyzes each frame. Expect about one analyzed frame per second.</div></section>
  <section class="card"><div class="eyebrow">Detector controls</div><div class="controls"><button id="start" class="button" onclick="control('start')">▶ Start</button><button id="stop" class="button stop" onclick="control('stop')">■ Stop</button><button class="button exit" onclick="exitDashboard()">↩ Exit to desktop</button></div><div class="hint">Exit stops detection and closes this dashboard window.</div></section>
  <section class="card"><div class="eyebrow">Model</div><div class="model-name">Rail Defect · YOLOv8n</div><div class="small">Local NCNN inference · no cloud connection</div></section>
</aside>
<section class="camera-panel"><div class="cam-head"><div class="cam-title">LIVE INSPECTION FEED</div><div class="cam-live"><i id="liveLight" class="live-light"></i><span id="updated">WAITING FOR CAMERA</span></div></div><div class="cam-stage"><div class="feed"><img id="feed" alt="Annotated live camera feed"><div id="placeholder" class="placeholder">Tap <b>Start</b> to open the camera and begin local defect detection.</div></div></div><div class="cam-foot"><div class="footleft"><span class="signal"><i></i> Defect detections are saved locally</span></div><span>640 × 480 capture</span></div></section>
<aside class="side right-side">
  <section class="card"><div class="eyebrow">Defects · latest frame</div><div id="defectCard" class="kpi defect"><div id="defects" class="kpi-num">—</div><div class="kpi-unit">objects</div></div><div class="small">Defective class only</div></section>
  <section class="card"><div class="eyebrow">Inference time</div><div class="kpi"><div id="latency" class="kpi-num">—</div><div class="kpi-unit">seconds / frame</div></div><div class="small">Pi CPU · NCNN backend</div></section>
  <section class="card"><div class="eyebrow">Detection confidence</div><div class="confrow"><span class="small">Minimum score</span><span id="confval" class="confval">0.35</span></div><input id="conf" class="threshold" type="range" min="0.10" max="0.90" step="0.05" value="0.35"><div class="small">Raise to reduce weak detections.</div></section>
  <section class="card snap-card"><div class="eyebrow">Recent defect snapshots</div><div id="snaps" class="snap small">No defect snapshots saved yet.</div></section>
</aside>
</main>
<script>
const feed=document.getElementById('feed'), placeholder=document.getElementById('placeholder');
feed.onload=()=>{feed.style.display='block';placeholder.style.display='none'};
feed.onerror=()=>{feed.style.display='none';placeholder.style.display='block'};
function connectFeed(){feed.style.display='block';feed.src='/video_feed?session='+Date.now()}
function showStopped(){feed.removeAttribute('src');feed.style.display='none';placeholder.style.display='block';placeholder.innerHTML='Detector stopped.<br>Tap <b>Start</b> to resume.'}
async function refresh(){try{let r=await fetch('/api/status');let d=await r.json();document.getElementById('badgeText').textContent=d.running?'INSPECTING':'STANDBY';document.getElementById('badge').className='badge '+(d.running?'live':'');document.getElementById('liveLight').className='live-light '+(d.running?'on':'');document.getElementById('status').textContent=d.message;document.getElementById('status').className='status '+(d.error?'alerttxt':'');document.getElementById('stateChip').textContent=d.error?'Error':(d.running?'Live':'Idle');document.getElementById('stateChip').className='state-chip '+(d.error?'alert':(d.running?'live':''));document.getElementById('defects').textContent=d.defect_count;document.getElementById('defectCard').className='kpi defect '+(d.defect_count?'alert':'');document.getElementById('latency').textContent=d.latency_s===null?'—':d.latency_s.toFixed(2);document.getElementById('updated').textContent=d.timestamp?('FRAME · '+d.timestamp.toUpperCase()):(d.running?'STARTING':'WAITING FOR CAMERA');document.getElementById('start').disabled=d.running;document.getElementById('stop').disabled=!d.running;if(!d.running&&d.message==='Stopped')showStopped();let box=document.getElementById('snaps');box.innerHTML=d.snapshots.length?d.snapshots.map(x=>'<div class="snap-entry"><div>'+x.name+'</div><img src="/captures/'+encodeURIComponent(x.name)+'" loading="lazy"></div>').join(''):'No defect snapshots saved yet.'}catch(e){document.getElementById('status').textContent='Dashboard connection lost'}}
async function control(action){if(action==='stop'){showStopped();document.getElementById('status').textContent='Stopping camera and detector…'}const response=await fetch('/api/'+action,{method:'POST'});if(action==='start'){const data=await response.json();if(!response.ok){document.getElementById('status').textContent=data.message;refresh();return}placeholder.innerHTML='Starting camera and model…';connectFeed()}refresh()}
async function exitDashboard(){showStopped();document.getElementById('status').textContent='Closing dashboard…';await fetch('/api/exit',{method:'POST'});document.body.innerHTML='<main style="display:grid;place-items:center;height:100vh;color:white">Dashboard closed. Returning to the Pi desktop…</main>';}
const slider=document.getElementById('conf');slider.oninput=()=>document.getElementById('confval').textContent=Number(slider.value).toFixed(2);slider.onchange=()=>fetch('/api/conf?value='+slider.value,{method:'POST'});setInterval(refresh,1500);refresh();
</script></body></html>'''

REVIEW_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Railway Detector · Project Review</title>
<style>
:root{color-scheme:dark;--bg:#080d16;--panel:#101925;--line:#263749;--muted:#8ca0b5;--text:#edf5fa;--mint:#55e0ad;--cyan:#63c8e8;--red:#ff687b;--amber:#f6c76b}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 50% -30%,#1b3940 0%,transparent 48%),var(--bg);color:var(--text);font:14px Inter,system-ui,sans-serif}header{height:66px;padding:0 22px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #253543;background:#0b121d}.brand{font-size:16px;font-weight:750}.sub{font-size:10px;color:var(--muted);letter-spacing:.15em;text-transform:uppercase;margin-top:4px}.nav{display:flex;gap:8px}.nav a{color:#b7c7d5;text-decoration:none;border:1px solid var(--line);background:#111c28;border-radius:8px;padding:8px 11px;font-size:11px;letter-spacing:.06em}.nav a.active{color:var(--mint);border-color:#397a68}main{max-width:1450px;margin:auto;padding:20px}.intro{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:15px}.intro h1{font-size:23px;margin:0 0 5px}.intro p{margin:0;color:var(--muted);font-size:12px}.review-tag{color:var(--mint);border:1px solid #28634f;border-radius:99px;padding:7px 11px;font-size:10px;letter-spacing:.1em}.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}.card{background:linear-gradient(145deg,#14202e,#0c1520);border:1px solid var(--line);border-radius:13px;padding:14px;box-shadow:0 10px 28px #0002}.label{font-size:10px;color:#91a6b8;letter-spacing:.13em;text-transform:uppercase;font-weight:700}.metric{font-size:27px;font-weight:800;letter-spacing:-.04em;margin-top:9px;color:var(--mint)}.metric.blue{color:var(--cyan)}.metric.white{color:var(--text)}.hint{font-size:10px;color:var(--muted);line-height:1.45;margin-top:5px}.section-title{margin:20px 0 10px;font-weight:750;font-size:14px;letter-spacing:.03em}.lower{display:grid;grid-template-columns:1.2fr 1fr;gap:11px}.diagram{display:flex;align-items:stretch;gap:8px;margin-top:12px}.stage{flex:1;min-width:0;border:1px solid #304456;background:linear-gradient(150deg,#142738,#101923);border-radius:10px;padding:13px 10px;text-align:center}.stage .icon{font-size:21px;color:var(--cyan)}.stage strong{display:block;font-size:12px;margin:5px 0}.stage span{font-size:10px;line-height:1.4;color:var(--muted);display:block}.arrow{align-self:center;color:var(--mint);font-size:18px}.arch-note{margin-top:11px;color:var(--muted);font-size:10px;line-height:1.55}.split{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:13px}.split div{padding:11px 8px;border:1px solid #2a3a4b;border-radius:9px;background:#0c1520;text-align:center}.split b{display:block;font-size:19px;color:var(--text)}.split span{font-size:10px;color:var(--muted)}.plot{margin-top:12px;width:100%;height:190px}.legend{display:flex;gap:15px;font-size:10px;color:var(--muted)}.legend i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}.plotrow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:11px}.plotimg{width:100%;max-height:280px;object-fit:contain;background:#fff;border-radius:8px;margin-top:10px}.note{margin-top:12px;padding:10px 12px;border:1px solid #66572d;background:#241f13;border-radius:9px;color:#f4d58c;font-size:11px;line-height:1.5}.pill{display:inline-block;border:1px solid #34485a;border-radius:99px;padding:4px 8px;color:#b5c7d7;font-size:10px;margin:3px}.error{color:var(--red)}
@media(max-width:900px){main{padding:13px}.metrics{grid-template-columns:repeat(3,1fr)}.lower{grid-template-columns:1fr}.plotrow{grid-template-columns:1fr 1fr}}
@media(max-width:600px){header{padding:0 12px}.sub{display:none}.intro{align-items:flex-start;gap:10px;flex-direction:column}.metrics{grid-template-columns:repeat(2,1fr)}.diagram{flex-direction:column}.arrow{transform:rotate(90deg)}.plotrow{grid-template-columns:1fr}}
</style></head><body>
<header><div><div class="brand">Railway Track Inspector · Project Review</div><div class="sub">YOLOv8n · Raspberry Pi 4 · local edge inference</div></div><nav class="nav"><a href="/">LIVE CONSOLE</a><a href="/review" class="active">PROJECT REVIEW</a></nav></header>
<main><div class="intro"><div><h1>Model, data & evaluation</h1><p>Review-ready summary generated from the trained model artifacts on this Pi.</p></div><div class="review-tag">VALIDATION RESULTS · NOT TEST RESULTS</div></div>
<section class="metrics">
<div class="card"><div class="label">mAP @ 0.50 IoU</div><div id="map50" class="metric">—</div><div id="map50note" class="hint">Validation set</div></div>
<div class="card"><div class="label">mAP @ 0.50:0.95</div><div id="map5095" class="metric blue">—</div><div class="hint">Stricter localization average</div></div>
<div class="card"><div class="label">Precision</div><div id="precision" class="metric">—</div><div class="hint">Correct predictions / all predictions</div></div>
<div class="card"><div class="label">Recall</div><div id="recall" class="metric blue">—</div><div class="hint">Found objects / actual objects</div></div>
<div class="card"><div class="label">Pi inference</div><div class="metric white">~1.2 FPS</div><div class="hint">One still-image run · about 0.83 sec end-to-end</div></div>
</section>
<div class="section-title">Detection pipeline & dataset</div>
<section class="lower"><div class="card"><div class="label">YOLOv8n object-detection architecture</div><div class="diagram"><div class="stage"><div class="icon">▧</div><strong>Input</strong><span>Camera frame<br>640 × 640 model input</span></div><div class="arrow">›</div><div class="stage"><div class="icon">◈</div><strong>Backbone</strong><span>CSPDarknet-style<br>Conv · C2f · SPPF</span></div><div class="arrow">›</div><div class="stage"><div class="icon">⌘</div><strong>Neck</strong><span>FPN + PAN<br>multi-scale features</span></div><div class="arrow">›</div><div class="stage"><div class="icon">▣</div><strong>Detect head</strong><span>Anchor-free boxes<br>2 class scores</span></div></div><div class="arch-note">The model predicts bounding boxes and class scores at multiple feature scales, then applies post-processing to produce detections. Exported to NCNN and run locally on the Pi CPU.</div><div style="margin-top:8px"><span class="pill">YOLOv8n</span><span class="pill">2 classes</span><span class="pill">640 × 640</span><span class="pill">NCNN · CPU</span><span class="pill">100 epochs</span></div></div>
<div class="card"><div class="label">Dataset split</div><div class="split"><div><b>1,198</b><span>Train images</span></div><div><b>101</b><span>Validation images</span></div><div><b>54</b><span>Held-out test images</span></div></div><div class="arch-note">Classes: <b>defective</b> and <b>non-defective</b>. Train and validation metrics are available in this package.</div><div class="note">Test metrics are not recorded in the current deployment ZIP. Do not present validation metrics as test-set results. Run a separate test evaluation to report test performance.</div></div></section>
<div class="section-title">Training behavior & diagnostic plots</div>
<section class="plotrow"><div class="card"><div class="label">Validation mAP by epoch</div><div class="legend"><span><i style="background:var(--mint)"></i>mAP50</span><span><i style="background:var(--cyan)"></i>mAP50–95</span></div><svg id="mapChart" class="plot" viewBox="0 0 600 190" preserveAspectRatio="none" aria-label="Validation mAP curve"></svg><div class="hint">Epoch-wise metrics from results.csv</div></div>
<div class="card"><div class="label">Confusion matrix · validation</div><img class="plotimg" src="/review/plot/confusion_matrix.png" alt="Validation confusion matrix"></div>
<div class="card"><div class="label">Precision–recall curve · validation</div><img class="plotimg" src="/review/plot/PR_curve.png" alt="Precision recall curve"></div>
<div class="card"><div class="label">F1 vs confidence · validation</div><img class="plotimg" src="/review/plot/F1_curve.png" alt="F1 confidence curve"></div></section>
<div class="note">mAP50 measures average precision at IoU 0.50. mAP50–95 averages it over IoU thresholds 0.50 to 0.95 and is a stricter localization measure. The Pi speed figure is a single still-image measurement, not a sustained video benchmark. Validate on representative track footage before making operational claims.</div>
</main>
<script>
function pct(id,v){document.getElementById(id).textContent=(100*Number(v)).toFixed(1)+'%'}
function drawChart(rows){const svg=document.getElementById('mapChart'),W=600,H=190,L=38,R=12,T=10,B=25;let values=rows.map(r=>[Number(r['metrics/mAP50(B)']),Number(r['metrics/mAP50-95(B)'])]);let max=Math.max(.2,...values.flat()),min=0;let x=i=>L+(W-L-R)*(i/Math.max(1,values.length-1)),y=v=>H-B-(H-T-B)*(v-min)/(max-min);let lines='';[0,.25,.5,.75,1].forEach(k=>{let yy=T+(H-T-B)*k;lines+='<line x1="'+L+'" y1="'+yy+'" x2="'+(W-R)+'" y2="'+yy+'" stroke="#273849" stroke-width="1"/><text x="2" y="'+(yy+4)+'" fill="#8ca0b5" font-size="10">'+(max*(1-k)).toFixed(1)+'</text>'});values.forEach((v,j)=>{let px=x(j);});for(let s=0;s<2;s++){let points=values.map((v,i)=>x(i)+','+y(v[s])).join(' ');let color=s===0?'#55e0ad':'#63c8e8';lines+='<polyline fill="none" stroke="'+color+'" stroke-width="2.5" points="'+points+'"/>'}lines+='<text x="'+L+'" y="'+(H-5)+'" fill="#8ca0b5" font-size="10">Epoch 1</text><text x="'+(W-R-45)+'" y="'+(H-5)+'" fill="#8ca0b5" font-size="10">Epoch '+rows.length+'</text>';svg.innerHTML=lines}
async function load(){try{let r=await fetch('/api/review'),d=await r.json();if(!r.ok)throw new Error(d.error||'Could not load training artifacts');pct('map50',d.metrics.map50);pct('map5095',d.metrics.map5095);pct('precision',d.metrics.precision);pct('recall',d.metrics.recall);document.getElementById('map50note').textContent='Epoch '+d.metrics.epoch+' · validation';drawChart(d.history)}catch(e){document.getElementById('map50').textContent='N/A';document.getElementById('map50note').innerHTML='<span class="error">'+e.message+'</span>'}}
load();
</script></body></html>'''

app = Flask(__name__)
class Detector:
    def __init__(self, model_path: Path, save_dir: Path, width: int, height: int, conf: float):
        self.model_path, self.save_dir = model_path, save_dir
        self.width, self.height = width, height
        self.conf = conf
        self.lock = threading.RLock()
        self.running = False
        self.stop_event = threading.Event()
        self.frame_jpeg: bytes | None = None
        self.defect_count = 0
        self.latency_s: float | None = None
        self.timestamp = ""
        self.message = "Stopped"
        self.error = ""
        self.snapshots: list[Path] = []
        self.thread: threading.Thread | None = None
        self.camera: Picamera2 | None = None

    def start(self) -> bool:
        with self.lock:
            if self.running or (self.thread is not None and self.thread.is_alive()):
                self.message = "Waiting for camera to finish shutting down…"
                return False
            self.stop_event.clear()
            self.running, self.error, self.message = True, "", "Loading model and camera…"
            self.frame_jpeg = None
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            return True

    def stop(self) -> None:
        with self.lock:
            if self.running:
                self.stop_event.set()
                self.frame_jpeg = None
                self.message = "Stopping camera and detector…"

    def _run(self) -> None:
        camera = None
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model directory not found: {self.model_path}")
            self.save_dir.mkdir(parents=True, exist_ok=True)
            model = YOLO(str(self.model_path), task="detect")
            camera = Picamera2()
            camera.configure(camera.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"}, buffer_count=2
            ))
            camera.start()
            self.camera = camera
            time.sleep(1)
            with self.lock:
                if self.running:
                    self.message = "Camera and detector running"
            while True:
                with self.lock:
                    if self.stop_event.is_set():
                        break
                    conf = self.conf
                started = time.monotonic()
                frame = camera.capture_array()
                result = model.predict(frame, imgsz=640, conf=conf, device="cpu", verbose=False)[0]
                annotated = result.plot()
                defect_count = 0
                if result.boxes is not None:
                    for cls_id in result.boxes.cls.tolist():
                        label = str(result.names.get(int(cls_id), int(cls_id))).lower()
                        if "defect" in label and "non-defect" not in label:
                            defect_count += 1
                latency = time.monotonic() - started
                cv2.putText(annotated, f"{latency:.2f}s | defects: {defect_count}", (10, 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)
                # Ultralytics result.plot() returns an OpenCV BGR image.
                ok, encoded = cv2.imencode('.jpg', annotated,
                                           [cv2.IMWRITE_JPEG_QUALITY, 82])
                if defect_count:
                    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    path = self.save_dir / f"defect_{stamp}.jpg"
                    cv2.imwrite(str(path), annotated)
                    with self.lock:
                        self.snapshots.insert(0, path)
                        self.snapshots = self.snapshots[:8]
                with self.lock:
                    self.frame_jpeg = encoded.tobytes() if ok else None
                    self.defect_count = defect_count
                    self.latency_s = latency
                    self.timestamp = datetime.now().strftime('%H:%M:%S')
                    self.message = "Defect detected — review snapshot" if defect_count else "Monitoring — no defect in latest frame"
                # Limit resource usage; measured inference already takes about 0.75s on this Pi.
                if self.stop_event.wait(0.08):
                    break
        except Exception as exc:
            with self.lock:
                self.error = str(exc)
                self.frame_jpeg = None
                self.message = f"Detector error: {exc}"
        finally:
            if camera is not None:
                try:
                    camera.close()  # stop streaming and release the libcamera device fully
                except Exception as close_exc:
                    with self.lock:
                        self.error = self.error or f"Camera release error: {close_exc}"
            self.camera = None
            with self.lock:
                self.running = False
                self.frame_jpeg = None
                if not self.error:
                    self.message = "Stopped"

    def status(self) -> dict:
        with self.lock:
            return {
                "running": self.running or (self.thread is not None and self.thread.is_alive()),
                "message": self.message, "error": self.error,
                "defect_count": self.defect_count,
                "latency_s": self.latency_s, "timestamp": self.timestamp,
                "snapshots": [{"name": p.name} for p in self.snapshots if p.exists()],
            }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default=str(Path.home() / 'railway_detector' / 'best_ncnn_model'))
    parser.add_argument('--save-dir', default=str(Path.home() / 'railway_detector' / 'captures'))
    parser.add_argument('--host', default='127.0.0.1', help='Keep localhost unless LAN access is needed.')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    parser.add_argument('--conf', type=float, default=0.35)
    args = parser.parse_args()
    detector = Detector(Path(args.model), Path(args.save_dir), args.width, args.height, args.conf)
    app.config['detector'] = detector

    @app.get('/')
    def index():
        return render_template_string(HTML)

    @app.get('/review')
    def project_review():
        return render_template_string(REVIEW_HTML)

    @app.get('/api/review')
    def review_data():
        results_csv = detector.model_path.parent / 'results.csv'
        try:
            with results_csv.open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            if not rows:
                raise ValueError('results.csv has no training rows')
            best = max(rows, key=lambda row: float(row['metrics/mAP50-95(B)']))
            return jsonify({
                'metrics': {
                    'epoch': int(float(best['epoch'])),
                    'precision': float(best['metrics/precision(B)']),
                    'recall': float(best['metrics/recall(B)']),
                    'map50': float(best['metrics/mAP50(B)']),
                    'map5095': float(best['metrics/mAP50-95(B)']),
                },
                'history': rows,
            })
        except (OSError, KeyError, ValueError) as exc:
            return jsonify({'error': f'Could not read training results at {results_csv}: {exc}'}), 404

    @app.get('/review/plot/<name>')
    def review_plot(name: str):
        allowed = {'confusion_matrix.png', 'PR_curve.png', 'F1_curve.png'}
        if name not in allowed:
            return 'Not found', 404
        return send_from_directory(detector.model_path.parent, name)

    @app.get('/video_feed')
    def video_feed():
        def stream():
            while True:
                with detector.lock:
                    frame = detector.frame_jpeg
                    running = detector.running
                if frame:
                    yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
                elif not running:
                    return
                else:
                    time.sleep(0.1)
        return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.get('/api/status')
    def status():
        return jsonify(detector.status())

    @app.post('/api/start')
    def start():
        started = detector.start()
        return jsonify({'ok': started, 'message': detector.status()['message']}), (200 if started else 409)

    @app.post('/api/stop')
    def stop():
        detector.stop()
        return jsonify({'ok': True})

    @app.post('/api/exit')
    def exit_dashboard():
        detector.stop()
        browser_pid_file = Path.home() / 'railway_detector' / 'browser.pid'
        def close_dashboard_window():
            try:
                pid = int(browser_pid_file.read_text().strip())
                import os, signal
                os.kill(pid, signal.SIGTERM)
            except (OSError, ValueError):
                pass
        threading.Timer(0.7, close_dashboard_window).start()
        return jsonify({'ok': True})

    @app.post('/api/conf')
    def confidence():
        try:
            value = float(request.args.get('value', '0.35'))
            if not 0.05 <= value <= 0.95:
                raise ValueError('Confidence must be between 0.05 and 0.95')
            with detector.lock:
                detector.conf = value
            return jsonify({'ok': True, 'conf': value})
        except Exception as exc:
            return jsonify({'ok': False, 'error': str(exc)}), 400

    @app.get('/captures/<path:name>')
    def capture(name: str):
        return send_from_directory(detector.save_dir, name)

    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)


if __name__ == '__main__':
    main()
