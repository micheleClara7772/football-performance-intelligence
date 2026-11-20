const app=document.querySelector('#app'), nav=document.querySelector('#nav'),notice=document.querySelector('#notice');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const opt=a=>a.map(v=>'<option>'+esc(v)+'</option>').join('');
const btn=(label,fn,secondary=false)=>'<button type="button" data-action="'+fn+'" class="'+(secondary?'secondary':'')+'">'+label+'</button>';
let home,d,view='',page=0,ids=null,period='',zone='',activation=false;
async function api(action,extra={}){
 const r=await fetch('/api/portal',{method:'POST',headers:{'Content-Type':'application/json','X-FPI':'1'},body:JSON.stringify({action,...extra})});
 const data=await r.json();if(!r.ok)throw Object.assign(Error(data.error||'Demande impossible.'),{status:r.status});return data;
}
function auth(){
 nav.innerHTML='';app.innerHTML='<section class="auth"><small>Football Performance Intelligence</small><h1>'+ (activation?'Activer mon accès':'Espace privé')+'</h1><form id="auth">'+(activation?'<label>Code d’invitation<input required name="code" autocomplete="one-time-code"></label>':'<label>Identifiant<input required name="name" autocomplete="username"></label>')+'<label>'+ (activation?'Choisissez un mot de passe (12 caractères minimum)':'Mot de passe')+'<input required type="password" name="password" autocomplete="'+(activation?'new-password':'current-password')+'" minlength="'+(activation?12:1)+'"></label><div class="row"><button>'+ (activation?'Activer mon compte':'Se connecter')+'</button>'+btn(activation?'Déjà inscrite ou inscrit':'Première connexion','toggle',true)+'</div></form></section>';
}
const match='<section class="hero"><small>Coupe du monde 2022 · Quart de finale · 10 décembre</small><div class="score">Maroc &nbsp;1 – 0&nbsp; Portugal</div><p>Analyse événementielle · StatsBomb Open Data</p></section>';
async function dashboard(){
 home=await api('home');d=null;nav.innerHTML=btn('Mes dossiers','home',true)+btn('Déconnexion','logout',true);
 let html='<small>'+esc(home.role)+' · '+esc(home.name)+'</small><h1>Dossiers tactiques</h1>'+match;
 if(home.role!=='Entraîneur')html+='<section><h2>Préparer une analyse</h2><form id="create"><div class="grid"><label>Match<select><option>Maroc – Portugal</option></select></label><label>Objectif<select name="mode">'+opt(home.modes)+'</select></label><label>Équipe observée<select name="team">'+opt(['Maroc','Portugal'])+'</select></label><label>Scénario<select name="scenario">'+opt(home.scenarios)+'</select></label></div><button>Lancer l’analyse</button></form></section>';
 html+='<section><h2>'+ (home.role==='Entraîneur'?'Publications du staff':'Dossiers disponibles')+'</h2>'+ (home.dossiers.length?home.dossiers.map(x=>'<article class="evidence"><span class="pill">'+esc(x.status)+'</span><h3>'+esc(x.team)+' · '+esc(x.scenario)+'</h3><p>'+esc(x.mode)+' · '+esc(x.author)+'</p>'+btn('Ouvrir le dossier','open:'+x.id)+(x.published&&home.role!=='Entraîneur'?' '+btn('Vue entraîneur','coach:'+x.id,true):'')+'</article>').join(''):'<p>Aucun dossier disponible pour le moment.</p>')+'</section>';
 if(home.role==='Administrateur')html+='<details class="card"><summary>Gérer les accès</summary><form id="invite" class="row"><label>Identifiant<input name="name" maxlength="64" required></label><label>Rôle<select name="role">'+opt(['Staff','Entraîneur','Administrateur'])+'</select></label><button>Créer une invitation</button></form><p id="invitation"></p>'+home.users.map(u=>'<p>'+esc(u.name)+' · '+esc(u.role)+' '+(u.disabled?'Accès révoqué':u.name===home.name?'':btn('Renouveler l’invitation','renew:'+u.id,true)+' '+btn('Révoquer','revoke:'+u.id,true)+'<form class="roleform row" data-id="'+u.id+'"><label>Nouveau rôle<select name="role">'+opt(['Staff','Entraîneur','Administrateur'])+'</select></label><button>Attribuer le rôle</button></form>')+'</p>').join('')+'</details>';
 app.innerHTML=html;
}
const side=y=>y<80/3?'Gauche':y>=160/3?'Droite':'Axe';
async function open(id,coach=false,reset=true){
 view=coach?'coach':'';d=await api('detail',{id,view});if(reset){page=0;ids=null;period='';zone=''}render();
}
function evidence(e){
 const edit=d.edit&&d.status==='En revue';
 return '<details class="evidence"><summary><b>'+esc(e.clock)+'</b> · '+esc(e.tags.join(' · '))+' · '+esc(e.player)+'</summary><p>Mi-temps '+e.p+' · '+side(e.y)+' · Départ ('+e.x+' ; '+e.y+')'+(e.end.length?' → ('+e.end.join(' ; ')+')':'')+'</p><small>Événement StatsBomb <code>'+esc(e.id)+'</code></small>'+ (e.after.length?'<p>Dans les 8 secondes suivantes</p><ul>'+e.after.map(a=>'<li>+'+a.s+' s · '+esc(a.team)+' · '+esc(a.action)+' <small>'+esc(a.id)+'</small></li>').join('')+'</ul>':'')+'<p>'+esc(e.note||'')+'</p>'+ (edit?'<form class="mark" data-id="'+e.id+'"><label>Observation du staff<textarea name="note" maxlength="1200">'+esc(e.note)+'</textarea></label><label>Décision<select name="decision">'+['Retenue','Écartée','À examiner'].map(v=>'<option '+(v===e.decision?'selected':'')+'>'+v+'</option>').join('')+'</select></label><button>Enregistrer la décision</button></form>':'')+'</details>';
}
function pitch(items){
 const dots=items.map(e=>'<circle cx="'+(4+e.x)+'" cy="'+(4+e.y)+'" r="1.1"><title>'+esc(e.clock+' · '+e.player)+'</title></circle>').join('');
 return '<figure><svg viewBox="0 0 128 88" role="img" aria-label="Localisation des actions sélectionnées, attaque vers la droite"><g fill="none" stroke="#c0dbc9" stroke-width=".55"><rect x="4" y="4" width="120" height="80"/><path d="M64 4v80 M4 23h18v42H4 M124 23h-18v42h18"/><circle cx="64" cy="44" r="10"/></g><g fill="#e7f791">'+dots+'</g></svg><figcaption>Points de départ · Attaque vers la droite →</figcaption></figure>';
}
function render(){
 const items=d.items.filter(e=>(!period||e.p===Number(period))&&(!zone||side(e.y)===zone)&&(!ids||ids.includes(e.id)));
 page=Math.min(page,Math.max(0,Math.ceil(items.length/12)-1));
 let html='<small>'+esc(d.mode)+' · '+esc(d.team)+'</small><h1>'+esc(d.scenario)+'</h1>'+match+'<section><span class="pill">'+esc(d.status)+'</span><h2>'+ (d.edit?'Revue du staff':'Observations validées')+'</h2><div class="grid stats">'+[[items.length,'Actions sélectionnées'],[items.filter(e=>e.p===1).length,'Première mi-temps'],[items.filter(e=>e.p===2).length,'Seconde mi-temps']].map(([n,l])=>'<div><b>'+n+'</b>'+l+'</div>').join('')+'</div><p class="help">'+(d.scenario.startsWith('Progression')?'Passe réussie ou conduite progressive : départ avant x=80 et gain d’au moins 15 unités. Entrée : franchissement de x=80. Renversement : passe réussie avec au moins 35 unités latérales.':'Pertes candidates : contrôle manqué ou dépossession du porteur, dans une possession de son équipe. Les actions suivantes sont relevées sur 8 secondes dans la même période.')+' Terrain StatsBomb de 120 × 80, orienté vers le but adverse.</p>';
 html+=pitch(items);
 if(d.edit&&items.length){const counts=Object.entries(items.reduce((a,e)=>{const k=side(e.y);a[k]=(a[k]||0)+1;return a},{})).sort((a,b)=>b[1]-a[1]);html+='<p class="result"><b>À examiner</b> · '+counts[0][1]+' des '+items.length+' actions sélectionnées commencent dans la zone « '+counts[0][0]+' ». Vérifiez les situations de cette zone avant de retenir une observation.</p>'}
 if(d.validation)html+='<p>Validé par '+esc(d.validation.author)+' · '+new Date(d.validation.date).toLocaleString('fr-FR')+'</p>';
 if(d.edit&&home.role==='Administrateur')html+=btn('Archiver le dossier','archive',true);
 if(d.edit){html+='<p>'+d.items.filter(e=>e.decision==='Retenue').length+' observation(s) retenue(s) pour publication.</p><div class="row">'+(d.status==='En revue'?btn('Valider les observations retenues','validate')+btn('Rejeter le dossier','reject',true):d.status==='Validée'?btn('Publier pour l’entraîneur','publish')+btn('Reprendre la revue','review',true):btn(d.status==='Publiée'?'Préparer une nouvelle version':'Ouvrir la revue','review'))+'</div>'}
 else html+=btn('Exporter le dossier JSON','export');
 html+='</section><section class="assistant"><h2>Interroger les actions</h2><form id="ask"><label>Recherche factuelle dans ce dossier<input name="q" maxlength="300" placeholder="Compare les entrées dans le dernier tiers" required></label><button>Rechercher</button></form><p id="answer"></p></section><section><h2>Preuves événementielles</h2><div class="filters"><label>Mi-temps<select id="period"><option value="">Les deux</option>'+opt(['1','2'])+'</select></label><label>Zone de départ<select id="zone"><option value="">Tout le terrain</option>'+opt(['Gauche','Axe','Droite'])+'</select></label>'+btn('Réinitialiser','reset',true)+'</div><div>'+items.slice(page*12,page*12+12).map(evidence).join('')+(items.length?'':'Aucune action dans cette sélection.')+'</div><div class="row">'+(page?btn('Précédent','prev',true):'')+(items.length>(page+1)*12?btn('Suivant','next',true):'')+'</div></section><section><h2>Revoir le match</h2><p>Replay externe. Les horodatages ci-dessus correspondent aux événements de match. Le suivi vidéo intégral reste expérimental.</p><a class="link" target="_blank" rel="noreferrer" href="https://www.plus.fifa.com/it/content/marocco-portogallo-quarti-di-finale-coppa-del-mondo-fifa-qatar-2022-match-completo/5f1b5797-25d0-4e10-b723-5072b470bae8">Ouvrir le replay FIFA+</a></section>';
 app.innerHTML=html;document.querySelector('#period').value=period;document.querySelector('#zone').value=zone;
}
function listen(type,fn){document.addEventListener(type,async ev=>{
 const busy=type==='submit'||(type==='click'&&ev.target.closest('[data-action]'));
 if(busy){app.inert=true;nav.inert=true;app.setAttribute('aria-busy','true')}
 try{notice.textContent='';await fn(ev)}catch(e){notice.textContent=e.message;if(e.status===401)auth()}
 finally{if(busy){app.inert=false;nav.inert=false;app.removeAttribute('aria-busy')}}
})}
listen('change',ev=>{if(ev.target.id==='period'||ev.target.id==='zone'){period=document.querySelector('#period').value;zone=document.querySelector('#zone').value;page=0;render()}});
listen('click',async ev=>{
 const a=ev.target.closest('[data-action]')?.dataset.action;if(!a)return;
 const [action,id]=a.split(':');
 if(action==='toggle'){activation=!activation;auth()}
 if(action==='home')await dashboard();
 if(action==='logout'){await api('logout');activation=false;auth()}
 if(action==='open'||action==='coach')await open(id,action==='coach');
 if(action==='renew'&&confirm('Renouveler l’invitation et fermer les sessions de ce compte ?')){const r=await api('renew',{id});document.querySelector('#invitation').textContent='Nouveau code valable 24 h : '+r.code}
 if(action==='revoke'&&confirm('Révoquer cet accès ?')){await api('revoke',{id});await dashboard()}
 if(['review','validate','reject','publish'].includes(action)){await api(action,{id:d.id,version:d.version});await open(d.id,false,false)}
 if(action==='next'||action==='prev'){page+=action==='next'?1:-1;render()}
 if(action==='reset'){ids=null;page=0;zone='';period='';render()}
 if(action==='archive'&&confirm('Archiver le dossier et le retirer des espaces actifs ?')){await api('archive',{id:d.id,version:d.version});await dashboard()}
 if(action==='export'){const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'}));link.download='FPI-Maroc-Portugal.json';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),2000)}
});
listen('submit',async ev=>{
 ev.preventDefault();const f=ev.target,b=Object.fromEntries(new FormData(f));
 if(f.id==='auth'){await api(activation?'activate':'login',b);await dashboard()}
 if(f.id==='create'){const r=await api('create',b);await open(r.id)}
 if(f.id==='invite'){const r=await api('invite',b);document.querySelector('#invitation').textContent='Code à usage unique, valable 24 h : '+r.code}
 if(f.matches('.roleform')&&confirm('Modifier le rôle et fermer les sessions de ce compte ?')){await api('changeRole',{id:f.dataset.id,...b});await dashboard()}
 if(f.className==='mark'){await api('mark',{...b,id:d.id,event:f.dataset.id,version:d.version});await open(d.id,false,false)}
 if(f.id==='ask'){const r=await api('ask',{...b,id:d.id,view});ids=r.ids;page=0;period='';zone='';render();document.querySelector('#answer').textContent=r.message;document.querySelector('[name=q]').value=b.q}
});
dashboard().catch(e=>{auth();if(e.status!==401)notice.textContent=e.message});
