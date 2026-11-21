const app=document.querySelector('#app'), nav=document.querySelector('#nav'),notice=document.querySelector('#notice');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const opt=a=>a.map(v=>'<option>'+esc(v)+'</option>').join('');
const btn=(label,fn,secondary=false)=>'<button type="button" data-action="'+fn+'" class="'+(secondary?'secondary':'')+'">'+label+'</button>';
let home,d,view='',ids=null,activation=false,activeMatch='',focusId='',selection={},response='',conversation={},groupBy='player',preview=false;
const periodNames=['','1re mi-temps','2e mi-temps','Prolongation 1','Prolongation 2'];
const clock=t=>Math.floor(t/60).toString().padStart(2,'0')+':'+(t%60).toString().padStart(2,'0');
const when=(p,t)=>periodNames[p]+' · '+clock(t);
const span=r=>when(r.fromPeriod,r.from)+' → '+when(r.toPeriod,r.to);
const bounds=e=>periodNames[e.p]+' · '+clock(e.start)+' – '+clock(e.finish);
const side=y=>y<80/3?'Gauche':y>=160/3?'Droite':'Axe';
const date=s=>s?new Date(s).toLocaleDateString('fr-FR',{day:'numeric',month:'short',year:'numeric'}):'';
const matchBy=id=>home.matches.find(m=>m.id===id);
const matchName=m=>m.teams.join(' – ');
const flags={'Maroc':'🇲🇦','Portugal':'🇵🇹','Argentine':'🇦🇷','France':'🇫🇷'};
const question=mode=>mode==='Préparer un adversaire'?'Que devons-nous surveiller chez cet adversaire ?':'Que voulons-nous reproduire ou corriger ?';
const options=(values,selected)=>values.map(v=>'<option '+(String(v)===String(selected)?'selected':'')+'>'+esc(v)+'</option>').join('');
const replay={'3869486':['Résumé sur YouTube','https://www.youtube.com/watch?v=M766FGsv5do'],'3869685':['Résumé officiel FIFA','https://www.fifa.com/en/watch/63XwuAOoqYgNW0Q3E9PxJG']};

async function api(action,extra={}){
 const r=await fetch('/api/portal',{method:'POST',headers:{'Content-Type':'application/json','X-FPI':'1'},body:JSON.stringify({action,...extra})});
 const data=await r.json();if(!r.ok)throw Object.assign(Error(data.error||'Demande impossible.'),{status:r.status});return data;
}
function auth(){
 nav.innerHTML='';app.innerHTML='<section class="auth"><small>Football Performance Intelligence</small><h1>'+ (activation?'Activer mon accès':'Espace privé')+'</h1><form id="auth">'+(activation?'<label>Code d’invitation<input required name="code" autocomplete="one-time-code"></label>':'<label>Identifiant<input required name="name" autocomplete="username"></label>')+'<label>'+ (activation?'Choisissez un mot de passe (12 caractères minimum)':'Mot de passe')+'<input required type="password" name="password" autocomplete="'+(activation?'new-password':'current-password')+'" minlength="'+(activation?12:1)+'"></label><div class="row"><button>'+ (activation?'Activer mon compte':'Se connecter')+'</button>'+btn(activation?'Déjà inscrite ou inscrit':'Première connexion','toggle',true)+'</div></form></section>';
}
function adminPanel(){let html="";
 if(home.role==='Administrateur')html+='<details class="card"><summary>Gérer les accès</summary><form id="invite" class="row"><label>Identifiant<input name="name" maxlength="64" required></label><label>Rôle<select name="role">'+opt(['Staff','Entraîneur','Administrateur'])+'</select></label><button>Créer une invitation</button></form><p id="invitation"></p>'+home.users.map(u=>'<p>'+esc(u.name)+' · '+esc(u.role)+' '+(u.disabled?'Accès révoqué':u.name===home.name?'':btn('Renouveler l’invitation','renew:'+u.id,true)+' '+btn('Révoquer','revoke:'+u.id,true)+'<form class="roleform row" data-id="'+u.id+'"><label>Nouveau rôle<select name="role">'+opt(['Staff','Entraîneur','Administrateur'])+'</select></label><button>Attribuer le rôle</button></form>')+'</p>').join('')+'</details>';
return html}
function matchCard(m){
 const selected=activeMatch===m.id;
 return '<button class="matchcard '+(selected?'chosen ':'')+(m.id==='3869685'?'finale':'')+'" type="button" aria-pressed="'+selected+'" data-action="match:'+m.id+'"><small>Coupe du monde 2022 · '+esc(m.stage)+'</small><strong>'+m.teams.map(t=>flags[t]+' '+esc(t)).join('<i> / </i>')+'</strong><span>'+date(m.date)+' · '+m.score.join(' – ')+(m.penalties.some(Boolean)?' · '+m.penalties.join('–')+' t.a.b.':'')+'</span></button>';
}
async function dashboard(){
 home=await api('home');d=null;preview=false;
 nav.innerHTML=btn('Mes dossiers','home',true)+btn('Déconnexion','logout',true);
 const staff=home.role!=='Entraîneur';
 const list=home.dossiers.filter(x=>!activeMatch||x.matchId===activeMatch).reverse();
 app.innerHTML='<section class="banner"><small>'+esc(home.role)+' / '+esc(home.name)+'</small><h1>'+(staff?'Atelier tactique':'Briefings de match')+'</h1><p>'+(staff?'Préparer, illustrer et transmettre une lecture du jeu.':'Les observations et situations retenues par votre staff.')+'</p></section><div class="sectionhead"><h2>Bibliothèque de matchs</h2>'+ (activeMatch?btn('Tous les matchs','all',true):'')+'</div><div class="grid">'+home.matches.map(matchCard).join('')+'</div><div class="sectionhead"><h2>'+(staff?'Dossiers tactiques':'Publications du staff')+'</h2>'+(staff?btn('＋ Créer un dossier','new'):'')+'</div><div class="grid">'+(list.map(x=>'<article class="card"><small>'+esc(matchName(matchBy(x.matchId)))+' · '+esc(x.status)+'</small><h3>'+esc(x.title)+'</h3><p>'+esc(x.summary||x.mode)+'</p><small>'+esc(x.author)+' · '+esc(date(x.date))+'<br>'+span(x.range)+'</small><div class="row">'+btn('Ouvrir le dossier','open:'+x.id)+(x.published&&staff?btn('Vue entraîneur','coach:'+x.id,true):'')+'</div></article>').join('')||'<p>Aucun dossier pour cette sélection.</p>')+'</div>'+adminPanel();
}
function createForm(){
 const m=matchBy(activeMatch)||home.matches[0];
 app.innerHTML='<small>Atelier du staff</small><h1>Créer un dossier</h1><form id="create" class="card"><label>Titre métier<input required maxlength="120" name="title" placeholder="Comment entrons-nous dans le dernier tiers ?"></label><div class="grid"><label>Match<select name="matchId">'+home.matches.map(x=>'<option value="'+x.id+'" '+(x.id===m.id?'selected':'')+'>'+esc(matchName(x))+'</option>').join('')+'</select></label><label>Équipe observée<select name="team"></select></label><label>Objectif<select name="mode">'+opt(home.modes)+'</select></label><label>Scénario<select name="scenario">'+opt(home.scenarios)+'</select></label></div><fieldset><legend>Intervalle d’analyse · temps de match</legend><div id="range" class="grid"></div></fieldset><div class="row"><button>Lancer l’analyse</button>'+btn('Annuler','home',true)+'</div></form>';
 setMatch(m.id);
}
function setMatch(id){
 const m=matchBy(id), periods=Object.keys(m.ends);
 document.querySelector('[name=team]').innerHTML=opt(m.teams);
 document.querySelector('#range').innerHTML=['from','to'].map((k,i)=>'<div><label>'+['Période de début','Période de fin'][i]+'<select name="'+k+'Period">'+periods.map(p=>'<option value="'+p+'" '+(i&&p===periods.at(-1)?'selected':'')+'>'+periodNames[p]+'</option>').join('')+'</select></label><label>'+['Début','Fin'][i]+' (mm:ss)<input name="'+k+'" required pattern="[0-9]{1,3}:[0-5][0-9]" value="'+clock(i?m.ends[periods.at(-1)]:0)+'"></label></div>').join('');
}
async function open(id,coach=false,reset=true){
 view=coach?'coach':'';d=await api('detail',{id,view});
 if(reset){ids=null;selection={};response='';conversation={};focusId='';preview=false;window.scrollTo(0,0)}
 render();
}
function field(e){
 const x=e.x+4,y=e.y+4,hasEnd=e.end?.length===2;
 const marker='tip-'+crypto.randomUUID();
 return '<svg class="pitch" viewBox="0 0 128 89" role="img" aria-label="'+esc(e.player+' · '+e.tags.join(', ')+' · attaque vers la droite')+'"><defs><marker id="'+marker+'" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ffdf72"/></marker></defs><rect width="128" height="89" rx="3" fill="#133f3d"/><path fill="#1b5150" d="M4 4h20v80H4z M44 4h20v80H44z M84 4h20v80H84z"/><g fill="none" stroke="#82aaa1" stroke-width=".55"><rect x="4" y="4" width="120" height="80"/><path d="M64 4v80 M4 23h18v42H4 M124 23h-18v42h18 M4 34h6v20H4 M124 34h-6v20h6"/><circle cx="64" cy="44" r="9.15"/></g><path d="M84 4v80" stroke="#c3e8ad" stroke-width=".65" stroke-dasharray="2 1.6"/><text x="85" y="9" fill="#e6f4d9" font-size="2.8">DERNIER TIERS</text>'+(hasEnd?'<line x1="'+x+'" y1="'+y+'" x2="'+(4+e.end[0])+'" y2="'+(4+e.end[1])+'" stroke="#ffdf72" stroke-width="1.3" '+(e.kind==='Conduite'?'stroke-dasharray="2 1"':'')+' marker-end="url(#'+marker+')"/>':'')+'<circle cx="'+x+'" cy="'+y+'" r="2.2" fill="#fff" stroke="#102434" stroke-width=".8"/></svg>';
}
function excerpt(s,n){return s.length>n?s.slice(0,n-1)+'…':s}
function printSheet(items){
 return '<div id="sheet"><small>FPI · Briefing du staff</small><h1>'+esc(d.title)+'</h1><p>'+esc(matchName(matchBy(d.matchId)))+' · '+esc(span(d.range))+'</p><h2>'+esc(excerpt(d.summary||items[0]?.note||d.scenario,350))+'</h2><div class="printgrid">'+items.slice(0,3).map(e=>'<article>'+field(e)+'<b>'+esc(e.player)+'</b><p>'+bounds(e)+'</p><p>'+esc(excerpt(e.note||e.tags.join(' · '),190))+'</p></article>').join('')+'</div><h3>Point à discuter</h3><p>'+esc(d.discussion||question(d.mode))+'</p></div>';
}
function editor(){
 return '<details class="card"><summary>Modifier le titre et le briefing</summary><form id="meta"><label>Titre métier<input required maxlength="120" name="title" value="'+esc(d.title)+'"></label><label>Conclusion du staff<textarea name="summary" maxlength="1500">'+esc(d.summary)+'</textarea></label><label>Point à discuter<textarea name="discussion" maxlength="500">'+esc(d.discussion)+'</textarea></label><label class="check"><input type="checkbox" name="includeTotal" '+(d.includeTotal?'checked':'')+'> Publier aussi le nombre de situations candidates</label><button>Enregistrer le briefing</button></form></details>';
}
function actionDetail(e,editing){
 if(!e)return '<p>Aucune situation dans cette sélection.</p>';
 const events=[...(e.before||[]),...(e.after||[])];
 return '<div class="tactical"><div class="pitchhead"><b>'+esc(e.kind)+' · '+e.clock+'</b><span>Attaque →</span></div>'+field(e)+'<p class="caption">Départ ● · '+(e.kind==='Conduite'?'Conduite en pointillés':e.end.length?'Flèche vers l’arrivée':'Lieu de la perte candidate')+'</p></div><div class="reading"><small>'+bounds(e)+' · fenêtre d’observation</small><h2>'+esc(e.player)+'</h2><b>'+esc(e.tags.join(' · '))+'</b><p>'+esc(e.note||'')+'</p>'+(events.length?'<details><summary>Événements autour de l’action</summary><ol>'+events.map(a=>'<li>'+clock(Number(e.clock.split(':')[0])*60+Number(e.clock.split(':')[1])+a.s)+' · '+esc(a.team)+' · '+esc(a.action)+'</li>').join('')+'</ol></details>':'')+(e.clip?btn('Voir la séquence','clip'):'<small>Preuve événementielle · vidéo synchronisée indisponible</small>')+'<div id="video"></div><details><summary>Source de la situation</summary><small>StatsBomb Open Data · '+esc(e.id)+'</small></details></div>'+(editing?'<form class="mark card" data-id="'+e.id+'"><label>Observation du staff<textarea name="note" maxlength="1200">'+esc(e.note)+'</textarea></label><label>Décision<select name="decision">'+options(['Retenue','Écartée','À examiner'],e.decision)+'</select></label><label class="check"><input name="featured" type="checkbox" '+(e.featured?'checked':'')+'> Illustration principale pour le briefing (3 maximum)</label><details><summary>Associer une vidéo autorisée et synchronisée</summary><label>URL HTTPS du fichier vidéo<input type="url" name="clipUrl" value="'+esc(e.clip?.url)+'"></label><label>Seconde vidéo correspondant au début de la fenêtre<input type="number" min="0" step=".01" name="clipStart" value="'+(e.clip?.start||0)+'"></label><label class="check"><input type="checkbox" name="checked" '+(e.clip?'checked':'')+'> Source autorisée et synchronisation vérifiée par le staff</label></details><button>Enregistrer la décision</button></form>':'');
}
function render(){
 const m=matchBy(d.matchId), retained=d.items.filter(e=>e.decision==='Retenue'), editing=d.edit&&d.status==='En revue'&&!preview;
 const source=(preview||!d.edit)?[...retained].sort((a,b)=>Number(!!b.featured)-Number(!!a.featured)):d.items;
 const values={player:e=>e.player,zone:e=>side(e.y),kind:e=>e.kind,period:e=>periodNames[e.p]};
 const items=source.filter(e=>(!ids||ids.includes(e.id))&&Object.entries(selection).every(([k,v])=>!v||values[k](e)===v));
 const e=items.find(e=>e.id===focusId)||items[0];focusId=e?.id||'';
 const metric=(!d.edit||preview)?retained.length+(retained.length===1?' situation retenue':' situations retenues')+' par le staff'+(d.includeTotal?' parmi '+d.total+' candidates':''):d.items.length+' situations candidates · '+retained.length+' retenues';
 const controls=d.edit?'<div class="row">'+(d.status==='En revue'?(preview?btn('Valider les observations retenues','validate')+btn('Revenir à la revue','preview',true):btn('Relire avant validation','preview')+btn('Rejeter le dossier','reject',true)):d.status==='Validée'?btn('Publier pour l’entraîneur','publish')+btn('Reprendre la revue','review',true):btn(d.published?'Préparer une nouvelle version':'Ouvrir la revue','review'))+'</div>':'';
 const groups=new Map();
 for(const item of items){const key=values[groupBy](item);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(item)}
 const grouped=[...groups].sort(([a],[b])=>a.localeCompare(b,'fr')).map(([key,rows])=>'<optgroup label="'+esc(key)+' · '+rows.length+'">'+rows.map(a=>'<option value="'+a.id+'" '+(a.id===focusId?'selected':'')+'>'+a.clock+' · '+esc(a.player)+' · '+esc(a.kind)+'</option>').join('')+'</optgroup>').join('');
 const totalByPeriod=Object.keys(m.ends).map(p=>[periodNames[p],items.filter(e=>e.p===Number(p)).length]).filter(x=>x[1]);
 const video=replay[m.id];
 let html='<div class="sectionhead">'+btn('← Dossiers','home',true)+'<small>'+esc(d.mode)+'</small></div><section class="lead"><small>'+esc(matchName(m))+' · '+m.score.join(' – ')+(m.penalties.some(Boolean)?' ('+m.penalties.join('–')+' t.a.b.)':'')+' · '+esc(d.status)+'</small><h1>'+esc(d.title)+'</h1><p>'+esc(d.summary||(!d.edit&&retained[0]?.note)||question(d.mode))+'</p><small>Intervalle analysé · '+span(d.range)+'</small></section><div class="sectionhead"><div><strong>'+esc(metric)+'</strong>'+(d.edit&&d.thirdSeconds!==undefined?'<small> · 3 situations retenues en '+clock(d.thirdSeconds)+' (temps écoulé)</small>':'')+'</div>'+controls+'</div>';
 if((!d.edit||preview)&&e)html+='<div class="spotlight"><div><small>Situation à montrer · '+bounds(e)+'</small><h2>'+esc(e.player)+'</h2><p>'+esc(e.note||e.tags.join(' · '))+'</p>'+btn('Explorer cette action','jump',true)+'</div>'+field(e)+'</div>';
 if(editing)html+=editor();
 if(preview)html+='<p class="result">Aperçu entraîneur · seuls les éléments retenus seront publiés.</p>';
 html+='<section class="card"><div class="sectionhead"><h2>Explorer les situations</h2>'+btn('Réinitialiser','reset',true)+'</div><div class="filters">'+Object.entries(values).map(([k,fn],i)=>'<label>'+['Joueur','Zone de départ','Type d’action','Période'][i]+'<select data-filter="'+k+'"><option value="">Tout afficher</option>'+options([...new Set(source.map(fn))].sort(),selection[k])+'</select></label>').join('')+'</div><div class="work"><aside><label>Regrouper par<select id="group">'+Object.entries({player:'Joueur',zone:'Zone',kind:'Type d’action',period:'Période'}).map(([k,v])=>'<option value="'+k+'" '+(groupBy===k?'selected':'')+'>'+v+'</option>').join('')+'</select></label><label>Situations similaires · '+items.length+'<select size="7" id="events">'+grouped+'</select></label><div class="row">'+btn('← Précédente','prev',true)+btn('Suivante →','next',true)+'</div></aside><div id="observation">'+actionDetail(e,editing)+'</div></div></section>';
 if(totalByPeriod.length>1)html+='<details class="card"><summary>Comparer les périodes de la sélection</summary>'+totalByPeriod.map(([label,n])=>'<p>'+label+' · '+n+' <meter value="'+n+'" max="'+items.length+'"></meter></p>').join('')+'</details>';
 html+='<section class="card"><h2>Interroger le dossier</h2><form id="ask"><label>Recherche factuelle · '+(d.edit&&!preview?'situations candidates':'actions publiées par le staff')+'<input name="q" maxlength="300" required placeholder="Montre-moi ses autres passes"></label><button>Rechercher</button></form><p role="status">'+esc(response)+'</p></section><section class="card"><h2>Briefing</h2><p>'+esc(d.discussion||question(d.mode))+'</p><div class="row">'+(!d.edit||preview?btn('Imprimer la fiche · PDF','print'):'')+(!d.edit?btn('Exporter le dossier JSON','export',true):'')+(d.published?btn('Copier le lien privé','share',true):'')+(m.id==='3869486'?'<a href="https://www.plus.fifa.com/it/content/marocco-portogallo-quarti-di-finale-coppa-del-mondo-fifa-qatar-2022-match-completo/5f1b5797-25d0-4e10-b723-5072b470bae8" target="_blank" rel="noreferrer">Replay externe FIFA+</a>':'')+'<a href="'+video[1]+'" target="_blank" rel="noreferrer">'+video[0]+'</a></div></section>';
 if(d.edit)html+='<details class="card"><summary>Gérer ce dossier</summary>'+btn(d.published?'Archiver le dossier':'Supprimer le brouillon',d.published?'archive':'delete',true)+'</details>';
 app.innerHTML=html+printSheet([...retained].sort((a,b)=>Number(!!b.featured)-Number(!!a.featured)));
}
function listen(type,fn){document.addEventListener(type,async ev=>{
 const busy=type==='submit'||(type==='click'&&ev.target.closest('[data-action]'));
 if(busy){app.inert=true;nav.inert=true;app.setAttribute('aria-busy','true')}
 try{notice.textContent='';await fn(ev)}catch(e){notice.textContent=e.message;if(e.status===401)auth()}
 finally{if(busy){app.inert=false;nav.inert=false;app.removeAttribute('aria-busy')}}
})}
async function enter(){
 await dashboard();const requested=new URL(location.href).searchParams.get('dossier');
 if(requested)await open(requested,true);
}
function navigationReset(){history.replaceState(null,'',location.pathname)}
async function change(action,fields={}){
 await api(action,{id:d.id,version:d.version,...fields});preview=false;await open(d.id,false,false);
}
listen('change',ev=>{
 const el=ev.target;
 if(el.name==='matchId')setMatch(el.value);
 if(el.name==='fromPeriod'||el.name==='toPeriod'){
   const m=matchBy(document.querySelector('[name=matchId]').value),first=el.name==='fromPeriod';
   document.querySelector(first?'[name=from]':'[name=to]').value=clock(first?[0,0,2700,5400,6300][el.value]:m.ends[el.value]);
 }
 if(el.dataset.filter){selection[el.dataset.filter]=el.value;focusId='';render()}
 if(el.id==='group'){groupBy=el.value;render()}
 if(el.id==='events'){focusId=el.value;conversation={};render()}
});
listen('click',async ev=>{
 const a=ev.target.closest('[data-action]')?.dataset.action;if(!a)return;
 const [action,id]=a.split(':');
 if(action==='toggle'){activation=!activation;auth()}
 if(action==='home'){navigationReset();await dashboard()}
 if(action==='logout'){await api('logout');activation=false;d=null;home=null;app.innerHTML='';auth()}
 if(action==='all'||action==='match'){activeMatch=action==='all'?'':activeMatch===id?'':id;await dashboard()}
 if(action==='jump')document.querySelector('#observation').scrollIntoView({block:'start'});
 if(action==='new')createForm();
 if(action==='open'||action==='coach')await open(id,action==='coach');
 if(action==='renew'&&confirm('Renouveler l’invitation et fermer les sessions de ce compte ?')){const r=await api('renew',{id});document.querySelector('#invitation').textContent='Code valable 24 h : '+r.code}
 if(action==='revoke'&&confirm('Révoquer cet accès ?')){await api('revoke',{id});await dashboard()}
 if(action==='preview'){preview=!preview;ids=null;selection={};render();window.scrollTo(0,0)}
 if(['review','validate','reject','publish'].includes(action))await change(action);
 if(action==='next'||action==='prev'){const list=document.querySelector('#events');const option=list.options[list.selectedIndex+(action==='next'?1:-1)];if(option){focusId=option.value;conversation={};render()}}
 if(action==='reset'){ids=null;selection={};response='';conversation={};render()}
 if(action==='delete'||action==='archive'){if(confirm((action==='delete'?'Supprimer définitivement le brouillon « ':'Archiver et retirer le dossier publié « ')+d.title+' » ?')){await api(action,{id:d.id,version:d.version});await dashboard()}}
 if(action==='print')window.print();
 if(action==='share'){const u=new URL(location.origin);u.searchParams.set('dossier',d.id);await navigator.clipboard.writeText(u.href);notice.textContent='Lien privé copié. Connexion requise.'}
 if(action==='clip'){
   const e=d.items.find(e=>e.id===focusId);const video=document.createElement('video');
   video.controls=true;video.playsInline=true;video.src=e.clip.url.split('#')[0]+'#t='+e.clip.start+','+(e.clip.start+e.finish-e.start);
   video.addEventListener('error',()=>{notice.textContent='Cette source vidéo ne répond pas. Le schéma et les événements restent disponibles.'});
   document.querySelector('#video').replaceChildren(video);
 }
 if(action==='export'){const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'}));link.download='FPI-'+d.matchId+'-'+d.id+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),2000)}
});
listen('submit',async ev=>{
 ev.preventDefault();const f=ev.target,b=Object.fromEntries(new FormData(f));
 if(f.id==='auth'){await api(activation?'activate':'login',b);await enter()}
 if(f.id==='create'){
   const sec=s=>s.split(':').reduce((a,n)=>60*a+Number(n),0);
   b.range={fromPeriod:Number(b.fromPeriod),from:sec(b.from),toPeriod:Number(b.toPeriod),to:sec(b.to)};
   const r=await api('create',b);await open(r.id);
 }
 if(f.id==='invite'){const r=await api('invite',b);document.querySelector('#invitation').textContent='Code à usage unique, valable 24 h : '+r.code}
 if(f.matches('.roleform')&&confirm('Modifier le rôle ?')){await api('changeRole',{id:f.dataset.id,...b});await dashboard()}
 if(f.id==='meta')await change('metadata',{...b,includeTotal:!!b.includeTotal});
 if(f.matches('.mark')){
   const clip=b.clipUrl?{url:b.clipUrl,start:Number(b.clipStart),checked:!!b.checked}:null;
   await change('mark',{decision:b.decision,note:b.note,event:f.dataset.id,featured:!!b.featured,clip});
   notice.textContent='Décision enregistrée.';
 }
 if(f.id==='ask'){
   const r=await api('ask',{q:b.q,id:d.id,view,preview,context:{event:focusId,...conversation}});
   ids=r.ids;selection={};response=r.message;conversation=r.context||{};render();
   document.querySelector('[name=q]').value=b.q;
 }
});
enter().catch(e=>{if(!home||e.status===401)auth();if(e.status!==401)notice.textContent=e.message});
