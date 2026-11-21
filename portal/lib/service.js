import { randomBytes, randomUUID, createHash, scryptSync, timingSafeEqual } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { join } from 'node:path';
const catalog = JSON.parse(gunzipSync(readFileSync(join(process.cwd(),'lib/catalog.json.gz'))));
const matches = catalog.map(({items,phases,...metadata})=>metadata);
const indexed = new Map(catalog.flatMap(m=>m.items.map(e=>[e.id,e])));
const matchOf = d=>catalog.find(m=>m.id===(d.matchId||'3869486'));
const fullRange = m=>({fromPeriod:1,from:0,toPeriod:Object.keys(m.ends).length,to:Object.values(m.ends).at(-1)});
function expand(record,staff=false){
  return record.items.map(e=>{
    const source=indexed.get(e.id);
    if(!e.clock)return {...source,...e};
    // Historical snapshots predate observation windows. Preserve the evidence staff published.
    if(staff)return {...source,...e};
    return {start:source?.start,finish:source?.finish,kind:source?.kind,...e};
  });
}
function inRange(e,r){
  const [min,sec]=e.clock.split(':').map(Number);
  const position=e.p*100000+min*60+sec;
  return position>=r.fromPeriod*100000+r.from&&position<=r.toPeriod*100000+r.to;
}
function checkRange(m,r){
  const starts=[0,0,2700,5400,6300];
  for(const [period,time] of [[r.fromPeriod,r.from],[r.toPeriod,r.to]])
    requireThat(Number.isInteger(period)&&Number.isInteger(time)&&m.ends[period]!==undefined&&time>=starts[period]&&time<=m.ends[period],'Intervalle hors des limites de la période.',400);
  requireThat(r.fromPeriod<r.toPeriod||(r.fromPeriod===r.toPeriod&&r.from<=r.to),'La fin précède le début.',400);
}
export const modes=['Préparer un adversaire','Débriefer mon équipe'];
export const scenarios=['Progression offensive','Transitions après perte'];
const roles=['Administrateur','Staff','Entraîneur'];
const now=()=>new Date().toISOString();
const hash=s=>createHash('sha256').update(s).digest('hex');
const token=()=>randomBytes(32).toString('base64url');
const requireThat=(ok,msg='Accès refusé.',status=403)=>{if(!ok)throw Object.assign(Error(msg),{status})};
const normalize=s=>s.normalize('NFD').replace(/\p{M}/gu,'').toLowerCase();
const safe=(s,max=512)=>typeof s==='string'&&s.length>0&&s.length<=max;
function password(value,salt=randomBytes(16).toString('hex')){
  return salt+':'+scryptSync(value,salt,32).toString('hex');
}
function invitation(state,name,role){
  requireThat(safe(name,64)&&roles.includes(role)&&!state.users.some(u=>u.name===name),'Nom indisponible ou rôle invalide.',400);
  const code=token();
  state.users.push({id:randomUUID(),name,role,invite:hash(code),until:Date.now()+86400000});
  return code;
}
function openSession(state,user){
  const raw=token();
  state.sessions=state.sessions.filter(s=>s.expires>Date.now());
  state.sessions.push({user:user.id,key:hash(raw),expires:Date.now()+8*3600000});
  return {cookie:raw,body:{success:true},write:true};
}
function answer(input,items,context={},phases={},range={fromPeriod:1,toPeriod:2}){
  let q=normalize(input);
  if(/\bcelles?\b/.test(q)&&Array.isArray(context?.ids)){
    const previous=new Set(context.ids);items=items.filter(e=>previous.has(e.id));
  }
  const wordsOf=s=>normalize(s).match(/[a-z0-9]+/g)||[];
  const players=[...new Set(items.map(e=>e.player))];
  const named=players.filter(name=>wordsOf(name).some(w=>w.length>=4&&wordsOf(q).includes(w)));
  if(named.length>1&&!named.some(n=>normalize(input).includes(normalize(n))))return {message:'Plusieurs joueurs correspondent. Précisez le nom complet.',ids:[]};
  const anchor=items.find(e=>e.id===context?.event);
  const follow=/ses |celles|ce type|cette passe|autres|a.t.il/.test(q);
  const player=named.find(n=>q.includes(normalize(n)))||named[0]||(follow&&(players.includes(context?.player)?context.player:anchor?.player));
  if(player){items=items.filter(e=>e.player===player);q=wordsOf(q).filter(w=>!wordsOf(player).includes(w)).join(' ')}
  if(/autres/.test(q)&&anchor)items=items.filter(e=>e.id!==anchor.id);
  if(anchor&&/de ce type|cette passe/.test(normalize(input))){
    items=items.filter(e=>anchor.tags.every(t=>e.tags.includes(t)));
  }
  const phaseFor=e=>phases[e.phase];
  const after=e=>{const steps=phaseFor(e)?.steps||[];const i=steps.findIndex(s=>s.id===e.id);return i<0?[]:steps.slice(i+1)};
  if(/a qui|qui recoit|destinataire/.test(q)){
    const passes=items.filter(e=>e.recipient);
    const counts=new Map();for(const e of passes)counts.set(e.recipient,(counts.get(e.recipient)||0)+1);
    return {message:passes.length?'Destinataires dans cette sélection : '+[...counts].map(([n,c])=>n+' ('+c+')').join(', ')+'.':'Aucun destinataire documenté dans cette sélection.',ids:passes.map(e=>e.id)};
  }
  if(/entree/.test(q)&&/tir/.test(q)){
    const hits=items.filter(e=>e.tags.includes('Entrée dans le dernier tiers')&&after(e).some(s=>s.kind==='Tir'));
    return {message:hits.length+' entrée(s) suivie(s) d’un tir dans la même possession. '+hits.map(e=>e.clock+' · '+e.player).join(' ; '),ids:hits.map(e=>e.id)};
  }
  if(/ensuite|se termine|apres la reception|suite de/.test(q)&&anchor&&phaseFor(anchor)){
    const steps=after(anchor);
    return {message:(steps.slice(0,4).map(s=>s.kind+' · '+s.player+(s.result?' ('+s.result+')':'')).join(' → ')||'Aucune étape offensive suivante enregistrée')+'. '+phaseFor(anchor).outcome,ids:[anchor.id]};
  }
  const previousKind=context?.kind||anchor?.kind;
  const kind=/passe/.test(q)?'Passe':/conduite/.test(q)?'Conduite':follow?previousKind:null;
  if(kind)items=items.filter(e=>e.kind===kind);
  if(player||follow)q=q.replace(/\b(est ce qu|est ce que|montre moi|a t il|a trouve|a reussi|plusieurs fois|de ce type|cette|ses|autres|celles|trouve|reussi|il)\b/g,' ').trim()+' actions';
  const words=q.match(/[a-z0-9]+/g)||[];
  const known=/^(retrouve|rechercher?|cherche|trouve|montre|affiche|compare[rz]?|combien|quels?|quelles?|quelle|ou|y|a|t|il|les?|la|l|d|du|de|des|un|une|en|au|aux|dans|dans|par|sur|ce|cette|ces|celles|sont|ont|est|ete|entre|et|aussi|apres|avec|pour|moi|nous|toutes?|tous|deux|1|2|1re|2e|premiere|seconde|deuxieme|mi|temps|periodes?|entrees?|dernier|tiers|renversements?|changements?|cotes?|droite?s?|gauche?s?|axe|pertes?|balle|ballon|transitions?|passes?|conduites?|progressions?|progressives?|offensives?|actions?|situations?|observations?|correspondent|match|dossier|selection|nombre|total)$/;
  const clarification={message:'Précisez une action (perte, passe, conduite, renversement, entrée), une zone ou une mi-temps dans ce dossier.',ids:[]};
  if(words.some(word=>!known.test(word)&&!['qu','trouve','fois','plusieurs','type','deuxieme'].includes(word)))return clarification;
  const tags=[[/entree/,'Entrée dans le dernier tiers'],[/renversement|changement de cote/,'Renversement'],[/perte|transition/,'Perte candidate'],[/passe.*progressiv/,'Passe progressive'],[/conduite/,'Conduite progressive']];
  const keys=tags.filter(([re])=>re.test(q)).map(t=>t[1]);
  const compare=/compar|mi.temps|periode/.test(q);
  const right=/droit/.test(q), left=/gauche/.test(q);
  if((right&&left)||(!keys.length&&!compare&&!right&&!left&&!/axe/.test(q)&&!/progression|action|situation|observation/.test(q))||/pourquoi|pressing|xg|score|brouillon|vitesse|butteur|buteur|distance|bless|possession|hors.jeu/.test(q)) return {message:'Cette question dépasse les preuves disponibles. Précisez une action, un côté ou une mi-temps.',ids:[]};
  let selected=items.filter(e=>(!keys.length||keys.some(k=>e.tags.includes(k)))&&(!right||e.y>=160/3)&&(!left||e.y<80/3));
  if(/progression/.test(q)&&!keys.length)selected=selected.filter(e=>e.tags.some(t=>t.endsWith('progressive')));
  if(/axe/.test(q))selected=selected.filter(e=>e.y>=80/3&&e.y<160/3);
  if(/dernier tiers/.test(q)&&!keys.includes('Entrée dans le dernier tiers'))selected=selected.filter(e=>e.x>=80);
  if(/premiere|1re/.test(q)&&!/compar/.test(q))selected=selected.filter(e=>e.p===1);
  if(/seconde|deuxieme|2e/.test(q)&&!/compar/.test(q))selected=selected.filter(e=>e.p===2);
  const labels=['','Première mi-temps','Seconde mi-temps','Prolongation 1','Prolongation 2'];
  const counts=labels.slice(range.fromPeriod,range.toPeriod+1).map((label,i)=>label+' : '+selected.filter(e=>e.p===range.fromPeriod+i).length);
  return {message:selected.length+' action(s) dans la sélection. '+counts.join(' · ')+'.',ids:selected.map(e=>e.id),context:{player:player||null,kind:kind||null,event:anchor?.id,ids:selected.map(e=>e.id)}};
}
export function serve(state,body,sessionKey,bootstrapHash){
  const {action}=body;
  const result=(data,write=false)=>({body:data,write});
  if(action==='activate'){
    requireThat(safe(body.code)&&safe(body.password,128)&&body.password.length>=12,'Code ou mot de passe invalide.',400);
    const digest=hash(body.code);
    let user=state.users.find(u=>u.invite===digest&&u.until>Date.now()&&!u.disabled);
    if(!user&&!state.users.length&&bootstrapHash&&digest===bootstrapHash){
      user={id:randomUUID(),name:'Clara',role:'Administrateur'};state.users.push(user);
    }
    requireThat(user,'Invitation invalide ou expirée.',401);
    user.password=password(body.password);delete user.invite;delete user.until;
    return openSession(state,user);
  }
  if(action==='login'){
    const user=state.users.find(u=>u.name===body.name&&!u.disabled);
    requireThat(safe(body.password,128),'Connexion refusée.',401);
    const stored=user?.password||'00000000000000000000000000000000:'+ '0'.repeat(64);
    const candidate=password(body.password,stored.split(':')[0]);
    requireThat(timingSafeEqual(Buffer.from(candidate),Buffer.from(stored))&&user?.password,'Connexion refusée.',401);
    return openSession(state,user);
  }
  const session=state.sessions.find(s=>s.key===hash(sessionKey||'')&&s.expires>Date.now());
  const user=state.users.find(u=>u.id===session?.user&&!u.disabled);requireThat(user,'Connectez-vous.',401);
  const admin=user.role===roles[0], staff=user.role!==roles[2];
  const mine=d=>admin||d.owner===user.id;
  if(action==='logout'){state.sessions=state.sessions.filter(s=>s!==session);return {body:{},cookie:'',write:true}}
  if(action==='invite'){requireThat(admin);return result({code:invitation(state,body.name?.trim(),body.role)},true)}
  if(action==='changeRole'||action==='renew'){
    requireThat(admin&&body.id!==user.id);
    const target=state.users.find(u=>u.id===body.id&&!u.disabled);requireThat(target);
    if(action==='changeRole'){requireThat(roles.includes(body.role));target.role=body.role}
    else {const code=token();target.invite=hash(code);target.until=Date.now()+86400000;delete target.password;
      state.sessions=state.sessions.filter(s=>s.user!==target.id);return result({code},true)}
    state.sessions=state.sessions.filter(s=>s.user!==target.id);return result({},true);
  }
  if(action==='revoke'){
    requireThat(admin&&(body.id!==user.id||state.users.some(u=>u.id!==user.id&&!u.disabled&&u.role===roles[0]&&(u.password||u.until>Date.now()))));
    const target=state.users.find(u=>u.id===body.id);requireThat(target);
    target.disabled=true;state.sessions=state.sessions.filter(s=>s.user!==target.id);return result({},true);
  }
  if(action==='home')return result({name:user.name,role:user.role,modes,scenarios,matches,
    dossiers:state.dossiers.filter(d=>!d.archived&&((staff&&mine(d))||d.published)).map(d=>{
      const owned=staff&&mine(d),r=owned?d:d.published;
      return {id:d.id,canDelete:owned,version:owned?d.version:undefined,range:d.range||fullRange(matchOf(d)),matchId:matchOf(d).id,title:r.title||d.team+' · '+d.scenario,summary:r.summary||'',date:r.publication?.date||d.published?.publication?.date||r.created||r.validation?.date||d.history?.[0]?.date,author:state.users.find(u=>u.id===d.owner)?.name,team:d.team,mode:d.mode,scenario:d.scenario,status:owned?d.status:'Publié',published:!!d.published}
    }),
    archives:staff?state.dossiers.filter(d=>d.archived&&mine(d)).map(d=>({id:d.id,title:d.title||d.team+' · '+d.scenario,version:d.version,published:!!d.published})):[],
    users:admin?state.users.map(({id,name,role,disabled})=>({id,name,role,disabled})):[]});
  if(action==='create'){
    const m=catalog.find(m=>m.id===(body.matchId||matches[0].id));
    requireThat(staff&&m&&modes.includes(body.mode)&&scenarios.includes(body.scenario)&&m.teams.includes(body.team));
    const range=body.range||fullRange(m);checkRange(m,range);
    requireThat(body.title===undefined||safe(body.title.trim(),120),'Titre requis (120 caractères maximum).',400);
    const items=m.items.filter(e=>inRange(e,range)&&e.team===body.team&&(e.tags.includes('Perte candidate')===(body.scenario===scenarios[1])));
    const d={id:randomUUID(),matchId:m.id,range,created:now(),title:body.title?.trim()||body.team+' · '+body.scenario,owner:user.id,team:body.team,mode:body.mode,scenario:body.scenario,status:'Proposée',version:1,
      items:items.map(e=>({id:e.id,decision:'À examiner',note:''})),history:[]};
    state.dossiers.push(d);return result({id:d.id},true);
  }
  const d=state.dossiers.find(d=>d.id===body.id);
  requireThat(d&&(!d.archived||(action==='delete'&&staff&&mine(d))),'Dossier inaccessible.',404);
  const edit=staff&&mine(d)&&body.view!=='coach';
  requireThat(edit||d.published,'Dossier inaccessible.',404);
  const record=edit?d:d.published;
  const items=expand(record,edit);
  const match=matchOf(d),range=d.range||fullRange(match);
  const phases=edit?Object.fromEntries([...new Set(items.map(e=>e.phase))].filter(k=>match.phases[k]).map(k=>[k,match.phases[k]])):record.phases||{};
  if(action==='detail')return result({id:d.id,matchId:matchOf(d).id,range:d.range||fullRange(matchOf(d)),team:d.team,mode:d.mode,scenario:d.scenario,status:edit?d.status:'Publié',edit,version:record.version,items,phases,title:record.title||d.team+' · '+d.scenario,summary:record.summary||'',discussion:record.discussion||'',includeTotal:!!record.includeTotal,total:edit?d.items.length:record.total,published:!!d.published,thirdSeconds:edit?d.thirdSeconds:undefined,validation:record.validation,publication:record.publication});
  if(action==='ask'){requireThat(safe(body.q,300),'Question invalide.',400);return result(answer(body.q,items.filter(e=>!body.preview||e.decision==='Retenue'),body.context,phases,range))}
  requireThat(edit);
  requireThat(d.version===body.version,'Ce dossier a changé. Rouvrez-le.',409);
  if(action==='delete'&&(!d.published||body.confirmPublished===true)){state.dossiers=state.dossiers.filter(x=>x!==d);return result({},true)}
  if(action==='archive'&&d.published){d.archived=true}
  else if(action==='metadata'&&d.status==='En revue'){
    requireThat(safe(body.title?.trim(),120)&&typeof body.summary==='string'&&body.summary.length<=1500&&typeof body.discussion==='string'&&body.discussion.length<=500,'Vérifiez le titre et les champs du briefing.',400);
    Object.assign(d,{title:body.title.trim(),summary:body.summary.trim(),discussion:body.discussion.trim(),includeTotal:body.includeTotal===true});
  }
  else if(action==='review'&&['Proposée','Publiée','Validée','Rejetée'].includes(d.status)){d.status='En revue';delete d.validation}
  else if(action==='reject'&&d.status==='En revue'){d.status='Rejetée'}
  else if(action==='mark'&&d.status==='En revue'){
    const e=d.items.find(e=>e.id===body.event);
    requireThat(e&&['Retenue','Écartée','À examiner'].includes(body.decision)&&typeof body.note==='string'&&body.note.length<=1200,'Observation invalide.',400);
    if(body.clip!==undefined){
      if(body.clip===null)delete e.clip;
      else{
        let url;try{url=new URL(body.clip.url)}catch{}
        requireThat(body.clip.checked===true&&url?.protocol==='https:'&&!url.username&&!url.password&&url.href.length<2048&&Number.isFinite(body.clip.start)&&body.clip.start>=0,'Vérifiez la source HTTPS et le repère vidéo.',400);
        e.clip={url:url.href,start:body.clip.start};
      }
    }
    if(body.featured!==undefined){
      requireThat(!body.featured||body.decision==='Retenue','Une illustration de briefing doit être retenue.',400);
      requireThat(!body.featured||d.items.filter(x=>x.id!==e.id&&x.featured&&x.decision==='Retenue').length<3,'Choisissez au plus trois illustrations principales.',400);
      e.featured=!!body.featured;
    }
    e.decision=body.decision;e.note=body.note.trim();
    if(e.decision!=='Retenue')e.featured=false;
    if(d.created&&d.thirdSeconds===undefined&&d.items.filter(i=>i.decision==='Retenue').length>=3)d.thirdSeconds=Math.floor((Date.now()-Date.parse(d.created))/1000);
  }else if(action==='validate'&&d.status==='En revue'&&d.items.some(e=>e.decision==='Retenue')){
    d.validation={author:user.name,date:now()};d.status='Validée';
  }else if(action==='publish'&&d.status==='Validée'){
    const kept=items.filter(e=>e.decision==='Retenue');
    d.status='Publiée';d.published={phases:Object.fromEntries(kept.filter(e=>phases[e.phase]).map(e=>[e.phase,phases[e.phase]])),title:d.title,summary:d.summary,discussion:d.discussion,includeTotal:d.includeTotal,total:d.includeTotal?d.items.length:undefined,version:d.version+1,validation:{...d.validation},publication:{author:user.name,date:now()},items:structuredClone(kept)};
  }else requireThat(false,'Transition impossible. Retenez au moins une observation avant validation.',400);
  d.version++;d.history.push({action,author:user.name,date:now(),version:d.version,event:body.event});return result({},true);
}
